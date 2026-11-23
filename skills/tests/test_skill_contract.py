"""Contract tests for skills/redshift-test-drive.

The skill is written instructions that drive the code in this repository. These
tests fail the build when the skill names something the code no longer has: a
config key, a make target, a repository path, an output-layout marker or a
reference file. They are tripwires against stale text, not proof that the
procedure works; skills/tests/EVALS.md covers behaviour.
"""
import re
import sys
import warnings
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO / "skills" / "redshift-test-drive"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = sorted((SKILL_DIR / "references").glob("*.md"))
SKILL_FILES = [SKILL_MD] + REFERENCES

ALLOWED_TOP_LEVEL = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
REPO_PATH_PREFIXES = ("config/", "core/", "tools/", "common/")
REPO_ROOT_FILES = {"README.md", "Makefile", "CONTRIBUTING.md", "LICENSE", "NOTICE"}
CODE_SPAN = re.compile(r"`([^`\n]+)`")
FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.S | re.M)
KEY_LIKE = re.compile(r"[a-z][a-z0-9_]*")


def _split(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, text
    _, front, body = text.split("---\n", 2)
    return front, body


class _UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate keys instead of keeping the last one."""


def _construct_unique_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        assert key not in seen, f"duplicate frontmatter key: {key}"
        seen.add(key)
    return loader.construct_mapping(node, deep=deep)


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _front():
    front, _ = _split(SKILL_MD)
    assert front is not None, "SKILL.md must start with YAML frontmatter"
    return front, yaml.load(front, Loader=_UniqueKeyLoader)


def _code_text(text):
    """Code spans plus fenced blocks: the places a command or path is named."""
    return CODE_SPAN.findall(text) + FENCE.findall(text)


def _config_keys():
    keys = set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                keys.add(str(k))
                walk(v)

    for name in ("extract.yaml", "replay.yaml"):
        walk(yaml.safe_load((REPO / "config" / name).read_text(encoding="utf-8")))
    return keys


def _sections(text):
    """Split at headings, keeping each heading with its section."""
    return re.split(r"(?=^#{1,6} )", text, flags=re.M)


def _slug(heading):
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


# 1. Frontmatter follows the Agent Skills specification.
def test_frontmatter():
    front, meta = _front()
    flow = re.compile(r"^\s*(?:[\w-]+:|-)\s*[\[{]", re.M)
    assert not flow.search(front), "use block style, not flow-style lists or maps"
    assert set(meta) <= ALLOWED_TOP_LEVEL, f"unexpected keys: {set(meta) - ALLOWED_TOP_LEVEL}"
    assert all(isinstance(meta[k], str) for k in ("name", "description"))
    assert meta["name"] == SKILL_DIR.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["name"]) and len(meta["name"]) <= 64
    desc = meta["description"]
    assert 1 <= len(desc) <= 1024 and len(desc.encode("utf-8")) <= 1024
    assert len(meta.get("compatibility", "")) <= 500
    md = meta["metadata"]
    assert all(isinstance(v, str) for v in md.values()), "metadata values must be strings"
    assert md["telemetry-channel"] == "skill/" + md["version"]


# 2. Every telemetry prefix equals skill/<metadata.version>.
def test_telemetry_token():
    _, meta = _front()
    expected = "skill/" + meta["metadata"]["version"]
    found = []
    for path in SKILL_FILES:
        text = path.read_text(encoding="utf-8")
        found += re.findall(r"REDSHIFT_TEST_DRIVE_CLIENT=[\"']?([^\s`\"']+)", text)
    assert found, "SKILL.md must show the telemetry prefix"
    assert set(found) == {expected}, f"telemetry tokens {set(found)} != {expected}"


def test_telemetry_token_matches_runtime_regex():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from common import version

    _, meta = _front()
    channel = "skill/" + meta["metadata"]["version"]
    assert version._CHANNEL_RE.fullmatch(channel), f"{channel} rejected by _CHANNEL_RE"


# 3. Identifiers presented as config keys exist in the shipped config files.
def test_config_keys_exist():
    keys = _config_keys()
    bad = []
    for path in SKILL_FILES:
        text = path.read_text(encoding="utf-8")
        candidates = set()
        # `key: value` anywhere in a code span, and key lines in yaml fences
        for span in CODE_SPAN.findall(text):
            m = re.match(r"([a-z_][a-z0-9_]*):\s", span)
            if m:
                candidates.add(m.group(1))
        for block in re.findall(r"^```yaml\n(.*?)^```", text, re.S | re.M):
            candidates |= set(re.findall(r"^\s*([a-z_][a-z0-9_]*):", block, re.M))
        # bullets and table rows that lead with a key, in sections about the config files
        for section in _sections(text):
            if "extract.yaml" not in section and "replay.yaml" not in section:
                continue
            for line in section.splitlines():
                m = re.match(r"\s*(?:[-*]|\|)\s*((?:`[^`]+`\s*/?\s*)+)", line)
                if m:
                    spans = CODE_SPAN.findall(m.group(1))
                    candidates |= {t for t in spans if KEY_LIKE.fullmatch(t)}
        bad += [f"{path.name}: {k}" for k in sorted(candidates - keys)]
    assert not bad, "not a key of config/extract.yaml or config/replay.yaml: " + ", ".join(bad)


# 4. Every make target named exists in the root Makefile.
def test_make_targets_exist():
    makefile = (REPO / "Makefile").read_text()
    targets = set(re.findall(r"^([A-Za-z_][\w-]*):", makefile, re.M))
    bad = []
    for path in SKILL_FILES:
        for chunk in _code_text(path.read_text(encoding="utf-8")):
            for t in re.findall(r"\bmake\s+([a-z_][\w-]*)", chunk):
                if t not in targets:
                    bad.append(f"{path.name}: make {t}")
    assert not bad, "missing make targets: " + ", ".join(bad)


# 5. Every repository path named exists (runtime log directories checked against the code).
def test_repository_paths_exist():
    log_dirs = []
    for src in ("core/extract/extract.py", "core/replay/replay.py", "core/replay/worker.py"):
        found = re.findall(r'dir=f?"([^"]+)"', (REPO / src).read_text())
        log_dirs += [re.sub(r"\{[^}]*\}", "", d) for d in found]
    bad = []
    for path in SKILL_FILES:
        for span in CODE_SPAN.findall(path.read_text(encoding="utf-8")):
            p = span.strip().rstrip(".,;:)")
            if not (p.startswith(REPO_PATH_PREFIXES) or p in REPO_ROOT_FILES) or " " in p:
                continue
            if p.startswith("core/logs/"):
                prefix = p.split("<", 1)[0]
                if not any(d.startswith(prefix) or prefix.startswith(d) for d in log_dirs):
                    bad.append(f"{path.name}: {p}")
            elif "<" in p or "*" in p:
                if not (REPO / p.split("<", 1)[0].split("*", 1)[0]).exists():
                    bad.append(f"{path.name}: {p}")
            elif not (REPO / p).exists():
                bad.append(f"{path.name}: {p}")
    assert not bad, "missing repository paths: " + ", ".join(bad)


# 6. Output-layout markers the skill relies on are still produced by the code.
@pytest.mark.parametrize(
    "source, marker",
    [
        ("core/extract/extractor.py", "Extraction_"),
        ("core/replay/report_gen.py", "analysis/"),
        ("core/replay/report_gen.py", "raw_data/"),
        ("core/replay/unload_sys_table.py", "system_tables/"),
        ("core/replay/connection_thread.py", '"source": "Test-Drive"'),
        ("core/replay/connection_thread.py", '"replay_start"'),
        ("core/sql/query_metrics.sql", "replay_start"),
        (
            "core/extract/extractor.py",
            "Original location,Replacement location,Replacement IAM role",
        ),
    ],
)
def test_output_layout_markers(source, marker):
    text = (REPO / source).read_text(encoding="utf-8")
    assert marker in text, f"{marker!r} no longer in {source}"


# 7. Reference links resolve (including anchors) and every reference is linked from SKILL.md.
LINK = re.compile(r"\]\(((?:references/)?[\w\-]+\.md)(#[\w\-]+)?\)")


def test_reference_links():
    bad, linked = [], set()
    for path in SKILL_FILES:
        for target, anchor in LINK.findall(path.read_text(encoding="utf-8")):
            dest = (path.parent / target).resolve()
            if not dest.exists():
                bad.append(f"{path.name} -> {target}")
                continue
            if path == SKILL_MD:
                linked.add(dest.name)
            if anchor:
                headings = re.findall(r"^#{1,6} (.*)$", dest.read_text(encoding="utf-8"), re.M)
                if anchor[1:] not in {_slug(h) for h in headings}:
                    bad.append(f"{path.name} -> {target}{anchor}")
    assert not bad, "broken links: " + ", ".join(bad)
    unlinked = {p.name for p in REFERENCES} - linked
    assert not unlinked, f"references not linked from SKILL.md: {unlinked}"


# 8. Size limits.
def test_sizes():
    _, body = _split(SKILL_MD)
    n = body.count("\n")
    assert n <= 500, f"SKILL.md body is {n} lines (limit 500)"
    if n > 250:
        warnings.warn(f"SKILL.md body is {n} lines; consider moving detail to references")
    for ref in REFERENCES:
        lines = ref.read_text(encoding="utf-8").splitlines()
        assert len(lines) <= 150, f"{ref.name} is {len(lines)} lines (limit 150)"
        if len(lines) > 100:
            has_toc = any(line.strip() == "## Contents" for line in lines[:20])
            assert has_toc, f"{ref.name} needs a table of contents"


# 9. Nothing internal, secret-like or left over from review reaches the public files.
# Literal tokens are split into fragments so this file does not match its own patterns
# and a plain grep over skills/ stays empty.
_TOKENS = ["SEC" + "-NEW", "PLACE" + "HOLDER", "eval" + "-wg", "eval" + "-prov", "owner" + "_cti"]
FORBIDDEN = re.compile(
    r"code\.amazon\.com|w\.amazon\.com|t\.corp\.amazon\.com|amazon\.dev|corp\.amazon\.com"
    r"|a2z\.com|aws\.dev|\br1p[0-9]+\b|\bC[BH]-0[0-9]\b|UP-0[0-9]|AKIA[0-9A-Z]{16}"
    r"|(^|[^0-9])[0-9]{12}([^0-9]|$)|" + "|".join(_TOKENS),
    re.M,
)


def test_no_internal_identifiers():
    bad = []
    for path in sorted((REPO / "skills").rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            bad.append(f"{path.relative_to(REPO)}: binary file under skills/")
            continue
        for m in FORBIDDEN.finditer(text):
            bad.append(f"{path.relative_to(REPO)}: {m.group(0).strip()}")
    assert not bad, "forbidden content: " + ", ".join(bad)
