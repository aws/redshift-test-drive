import { __assign } from "tslib";
import React from 'react';
import useFocusVisible from '../internal/hooks/focus-visible';
import InternalIcon from '../icon/internal';
import clsx from 'clsx';
import styles from './styles.css.js';
import InternalHeader from '../header/internal';
import ScreenreaderOnly from '../internal/components/screenreader-only';
import { generateUniqueId } from '../internal/hooks/use-unique-id';
import { isDevelopment } from '../internal/is-development';
import { warnOnce } from '../internal/logging';
var ExpandableDefaultHeader = function (_a) {
    var id = _a.id, className = _a.className, onClick = _a.onClick, ariaLabel = _a.ariaLabel, ariaControls = _a.ariaControls, expanded = _a.expanded, children = _a.children, icon = _a.icon, onKeyUp = _a.onKeyUp, onKeyDown = _a.onKeyDown;
    var focusVisible = useFocusVisible();
    return (React.createElement("div", __assign({ id: id, role: "button", className: className, tabIndex: 0, onKeyUp: onKeyUp, onKeyDown: onKeyDown, onClick: onClick, "aria-label": ariaLabel, "aria-controls": ariaControls, "aria-expanded": expanded }, focusVisible),
        React.createElement("div", { className: styles['icon-container'] }, icon),
        children));
};
var ExpandableNavigationHeader = function (_a) {
    var id = _a.id, className = _a.className, onClick = _a.onClick, ariaLabelledBy = _a.ariaLabelledBy, ariaLabel = _a.ariaLabel, ariaControls = _a.ariaControls, expanded = _a.expanded, children = _a.children, icon = _a.icon;
    var focusVisible = useFocusVisible();
    return (React.createElement("div", { id: id, className: className, onClick: onClick },
        React.createElement("button", __assign({ className: styles['icon-container'], "aria-labelledby": ariaLabelledBy, "aria-label": ariaLabel, "aria-controls": ariaControls, "aria-expanded": expanded }, focusVisible), icon),
        children));
};
var ExpandableContainerHeader = function (_a) {
    var id = _a.id, className = _a.className, onClick = _a.onClick, ariaLabel = _a.ariaLabel, ariaControls = _a.ariaControls, expanded = _a.expanded, children = _a.children, icon = _a.icon, headerDescription = _a.headerDescription, headerCounter = _a.headerCounter, headingTagOverride = _a.headingTagOverride, onKeyUp = _a.onKeyUp, onKeyDown = _a.onKeyDown;
    var focusVisible = useFocusVisible();
    var screenreaderContentId = generateUniqueId('expandable-section-header-content-');
    return (React.createElement("div", __assign({ id: id, className: className, onClick: onClick }, focusVisible),
        React.createElement(InternalHeader, { variant: 'h2', description: headerDescription, counter: headerCounter, headingTagOverride: headingTagOverride },
            React.createElement("span", { className: styles['header-container-button'], role: "button", tabIndex: 0, onKeyUp: onKeyUp, onKeyDown: onKeyDown, "aria-label": ariaLabel, "aria-labelledby": ariaLabel ? undefined : screenreaderContentId, "aria-controls": ariaControls, "aria-expanded": expanded },
                React.createElement("span", { className: styles['icon-container'] }, icon),
                React.createElement("span", null, children))),
        React.createElement(ScreenreaderOnly, { id: screenreaderContentId },
            children,
            " ",
            headerCounter,
            " ",
            headerDescription)));
};
export var ExpandableSectionHeader = function (_a) {
    var id = _a.id, className = _a.className, variant = _a.variant, header = _a.header, headerText = _a.headerText, headerDescription = _a.headerDescription, headerCounter = _a.headerCounter, headingTagOverride = _a.headingTagOverride, expanded = _a.expanded, ariaControls = _a.ariaControls, ariaLabel = _a.ariaLabel, ariaLabelledBy = _a.ariaLabelledBy, onKeyUp = _a.onKeyUp, onKeyDown = _a.onKeyDown, onClick = _a.onClick;
    var icon = (React.createElement(InternalIcon, { size: variant === 'container' ? 'medium' : 'normal', className: clsx(styles.icon, expanded && styles.expanded), name: "caret-down-filled" }));
    var defaultHeaderProps = {
        id: id,
        icon: icon,
        expanded: expanded,
        ariaControls: ariaControls,
        ariaLabel: ariaLabel,
        onClick: onClick
    };
    var triggerClassName = clsx(styles.trigger, styles["trigger-".concat(variant)], expanded && styles['trigger-expanded']);
    if (variant === 'navigation') {
        return (React.createElement(ExpandableNavigationHeader, __assign({ className: clsx(className, triggerClassName), ariaLabelledBy: ariaLabelledBy }, defaultHeaderProps), headerText !== null && headerText !== void 0 ? headerText : header));
    }
    if (variant === 'container' && headerText) {
        return (React.createElement(ExpandableContainerHeader, __assign({ className: clsx(className, triggerClassName, expanded && styles.expanded), headerDescription: headerDescription, headerCounter: headerCounter, headingTagOverride: headingTagOverride, onKeyUp: onKeyUp, onKeyDown: onKeyDown }, defaultHeaderProps), headerText));
    }
    if (variant === 'container' && header && isDevelopment) {
        warnOnce('ExpandableSection', 'Use `headerText` instead of `header` to provide the button within the heading for a11y.');
    }
    return (React.createElement(ExpandableDefaultHeader, __assign({ className: clsx(className, triggerClassName, styles.focusable, expanded && styles.expanded), onKeyUp: onKeyUp, onKeyDown: onKeyDown }, defaultHeaderProps), headerText !== null && headerText !== void 0 ? headerText : header));
};
//# sourceMappingURL=expandable-section-header.js.map