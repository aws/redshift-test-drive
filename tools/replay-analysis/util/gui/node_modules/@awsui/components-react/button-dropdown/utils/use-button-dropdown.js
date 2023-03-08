import { __rest } from "tslib";
import { useOpenState } from '../../internal/components/options-list/utils/use-open-state';
import { fireCancelableEvent, isPlainLeftClick } from '../../internal/events';
import { KeyCode } from '../../internal/keycode';
import { getItemTarget, isItemGroup, isLinkItem } from './utils';
import useHighlightedMenu from './use-highlighted-menu';
export function useButtonDropdown(_a) {
    var items = _a.items, onItemClick = _a.onItemClick, onItemFollow = _a.onItemFollow, onReturnFocus = _a.onReturnFocus, hasExpandableGroups = _a.hasExpandableGroups, _b = _a.isInRestrictedView, isInRestrictedView = _b === void 0 ? false : _b, _c = _a.expandToViewport, expandToViewport = _c === void 0 ? false : _c;
    var _d = useHighlightedMenu({
        items: items,
        hasExpandableGroups: hasExpandableGroups,
        isInRestrictedView: isInRestrictedView
    }), targetItem = _d.targetItem, isHighlighted = _d.isHighlighted, isKeyboardHighlight = _d.isKeyboardHighlight, isExpanded = _d.isExpanded, highlightItem = _d.highlightItem, moveHighlight = _d.moveHighlight, expandGroup = _d.expandGroup, collapseGroup = _d.collapseGroup, reset = _d.reset, setIsUsingMouse = _d.setIsUsingMouse;
    var _e = useOpenState({ onClose: reset }), isOpen = _e.isOpen, closeDropdown = _e.closeDropdown, openStateProps = __rest(_e, ["isOpen", "closeDropdown"]);
    var toggleDropdown = function (options) {
        var _a;
        if (options === void 0) { options = {}; }
        var moveHighlightOnOpen = (_a = options.moveHighlightOnOpen) !== null && _a !== void 0 ? _a : true;
        if (!isOpen && moveHighlightOnOpen) {
            moveHighlight(1);
        }
        openStateProps.toggleDropdown();
    };
    var onGroupToggle = function (item) { return (!isExpanded(item) ? expandGroup(item) : collapseGroup()); };
    var onItemActivate = function (item, event) {
        var details = {
            id: item.id || 'undefined',
            href: item.href,
            external: item.external,
            target: getItemTarget(item)
        };
        if (onItemFollow && item.href && isPlainLeftClick(event)) {
            fireCancelableEvent(onItemFollow, details, event);
        }
        if (onItemClick) {
            fireCancelableEvent(onItemClick, details, event);
        }
        onReturnFocus();
        closeDropdown();
    };
    var doVerticalNavigation = function (direction) {
        if (isOpen) {
            moveHighlight(direction);
        }
    };
    var openAndSelectFirst = function (event) {
        toggleDropdown();
        event.preventDefault();
    };
    var actOnParentDropdown = function (event) {
        // if there is no highlighted item we act on the trigger by opening or closing dropdown
        if (!targetItem) {
            if (isOpen && !isInRestrictedView) {
                toggleDropdown();
            }
            else {
                openAndSelectFirst(event);
            }
        }
        else {
            if (isItemGroup(targetItem)) {
                onGroupToggle(targetItem, event);
            }
            else {
                onItemActivate(targetItem, event);
            }
        }
    };
    var activate = function (event, isEnter) {
        setIsUsingMouse(false);
        // if item is a link we rely on default behavior of an anchor, no need to prevent
        if (targetItem && isLinkItem(targetItem) && isEnter) {
            return;
        }
        event.preventDefault();
        actOnParentDropdown(event);
    };
    var onKeyDown = function (event) {
        setIsUsingMouse(false);
        switch (event.keyCode) {
            case KeyCode.down: {
                doVerticalNavigation(1);
                event.preventDefault();
                break;
            }
            case KeyCode.up: {
                doVerticalNavigation(-1);
                event.preventDefault();
                break;
            }
            case KeyCode.space: {
                // Prevent scrolling the list of items and highlighting the trigger
                event.preventDefault();
                break;
            }
            case KeyCode.enter: {
                if (!(targetItem === null || targetItem === void 0 ? void 0 : targetItem.disabled)) {
                    activate(event, true);
                }
                break;
            }
            case KeyCode.left:
            case KeyCode.right: {
                if (targetItem && !targetItem.disabled && isItemGroup(targetItem) && !isExpanded(targetItem)) {
                    expandGroup();
                }
                else if (hasExpandableGroups) {
                    collapseGroup();
                }
                event.preventDefault();
                break;
            }
            case KeyCode.escape: {
                onReturnFocus();
                closeDropdown();
                event.preventDefault();
                break;
            }
            case KeyCode.tab: {
                // When expanded to viewport the focus can't move naturally to the next element.
                // Returning the focus to the trigger instead.
                if (expandToViewport) {
                    onReturnFocus();
                }
                closeDropdown();
                break;
            }
        }
    };
    var onKeyUp = function (event) {
        // We need to handle activating items with Space separately because there is a bug
        // in Firefox where changing the focus during a Space keydown event it will trigger
        // unexpected click events on the new element: https://bugzilla.mozilla.org/show_bug.cgi?id=1220143
        if (event.keyCode === KeyCode.space && !(targetItem === null || targetItem === void 0 ? void 0 : targetItem.disabled)) {
            activate(event);
        }
    };
    return {
        isOpen: isOpen,
        targetItem: targetItem,
        isHighlighted: isHighlighted,
        isKeyboardHighlight: isKeyboardHighlight,
        isExpanded: isExpanded,
        highlightItem: highlightItem,
        onKeyDown: onKeyDown,
        onKeyUp: onKeyUp,
        onItemActivate: onItemActivate,
        onGroupToggle: onGroupToggle,
        toggleDropdown: toggleDropdown,
        setIsUsingMouse: setIsUsingMouse
    };
}
//# sourceMappingURL=use-button-dropdown.js.map