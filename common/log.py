import logging
import logging.handlers
import time
import os

log_date_format = "%Y-%m-%d %H:%M:%S"


def log_version():
    """Read the VERSION file and log it"""
    logger = logging.getLogger("WorkloadReplicatorLogger")
    try:
        with open("VERSION", "r") as fp:
            logger.info(f"Version {fp.read().strip()}")
    except:
        logger.warning(f"Version unknown")


def init_logging(
    filename,
    dir="core/logs/extract",
    level=logging.DEBUG,
    backup_count=2,
    preamble="",
    script_type="extract",
    logger_name="WorkloadReplicatorLogger",
):
    """Initialize logging to stdio"""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logging.Formatter.converter = time.gmtime
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(get_log_formatter())
    logger.addHandler(ch)

    """ Additionally log to a logfile """
    os.makedirs(dir, exist_ok=True)
    filename = f"{dir}/{filename}"
    file_exists = os.path.isfile(filename)
    fh = logging.handlers.RotatingFileHandler(filename, backupCount=backup_count)

    # if the file exists from a previous run, rotate it
    if file_exists:
        fh.doRollover()

    # dump the preamble to the file first
    if preamble:
        with open(filename, "w") as fp:
            fp.write(preamble.rstrip() + "\n\n" + "-" * 40 + "\n")

    fh.setLevel(level)
    fh.setFormatter(get_log_formatter())
    logger = logging.getLogger(logger_name)
    logger.info(f"Starting the {script_type}")
    logger.info(f"Logging to {filename}")
    logger.addHandler(fh)
    logger.info("== Initializing logfile ==")


def get_log_formatter():
    """Define the log format, with the option to prepend process and job/thread to each message"""
    fmt = "([%(levelname)s] %(asctime)s %(threadName)s %(processName)s): %(message)s"
    formatter = logging.Formatter(fmt, datefmt=log_date_format)
    formatter.converter = time.gmtime
    return formatter
