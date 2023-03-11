import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useCallback, useRef } from 'react';
import { fireCancelableEvent, isPlainLeftClick } from '../internal/events';
import useFocusVisible from '../internal/hooks/focus-visible';
import useForwardFocus from '../internal/hooks/forward-focus';
import styles from './styles.css.js';
import { LeftIcon, RightIcon } from './icon-helper';
import { checkSafeUrl } from '../internal/utils/check-safe-url';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import LiveRegion from '../internal/components/live-region';
export var InternalButton = React.forwardRef(function (_a, ref) {
    var _b;
    var children = _a.children, iconName = _a.iconName, __iconClass = _a.__iconClass, onClick = _a.onClick, onFollow = _a.onFollow, _c = _a.iconAlign, iconAlign = _c === void 0 ? 'left' : _c, iconUrl = _a.iconUrl, iconSvg = _a.iconSvg, iconAlt = _a.iconAlt, _d = _a.variant, variant = _d === void 0 ? 'normal' : _d, _e = _a.loading, loading = _e === void 0 ? false : _e, loadingText = _a.loadingText, _f = _a.disabled, disabled = _f === void 0 ? false : _f, _g = _a.wrapText, wrapText = _g === void 0 ? true : _g, href = _a.href, target = _a.target, download = _a.download, _h = _a.formAction, formAction = _h === void 0 ? 'submit' : _h, ariaLabel = _a.ariaLabel, ariaExpanded = _a.ariaExpanded, _j = _a.__hideFocusOutline, __hideFocusOutline = _j === void 0 ? false : _j, __nativeAttributes = _a.__nativeAttributes, _k = _a.__internalRootRef, __internalRootRef = _k === void 0 ? null : _k, _l = _a.__activated, __activated = _l === void 0 ? false : _l, props = __rest(_a, ["children", "iconName", "__iconClass", "onClick", "onFollow", "iconAlign", "iconUrl", "iconSvg", "iconAlt", "variant", "loading", "loadingText", "disabled", "wrapText", "href", "target", "download", "formAction", "ariaLabel", "ariaExpanded", "__hideFocusOutline", "__nativeAttributes", "__internalRootRef", "__activated"]);
    checkSafeUrl('Button', href);
    var focusVisible = useFocusVisible();
    var isAnchor = Boolean(href);
    var isDisabled = loading || disabled;
    var shouldHaveContent = children && ['icon', 'inline-icon', 'flashbar-icon', 'modal-dismiss'].indexOf(variant) === -1;
    var buttonRef = useRef(null);
    useForwardFocus(ref, buttonRef);
    var handleClick = useCallback(function (event) {
        if (isAnchor && isDisabled) {
            return event.preventDefault();
        }
        if (isAnchor && isPlainLeftClick(event)) {
            fireCancelableEvent(onFollow, null, event);
        }
        var altKey = event.altKey, button = event.button, ctrlKey = event.ctrlKey, metaKey = event.metaKey, shiftKey = event.shiftKey;
        fireCancelableEvent(onClick, { altKey: altKey, button: button, ctrlKey: ctrlKey, metaKey: metaKey, shiftKey: shiftKey }, event);
    }, [isAnchor, isDisabled, onClick, onFollow]);
    var buttonClass = clsx(props.className, styles.button, styles["variant-".concat(variant)], (_b = {},
        _b[styles.disabled] = isDisabled,
        _b[styles['button-no-wrap']] = !wrapText,
        _b[styles['button-no-text']] = !shouldHaveContent,
        _b[styles['is-activated']] = __activated,
        _b));
    var buttonProps = __assign(__assign(__assign(__assign({}, props), (__hideFocusOutline ? undefined : focusVisible)), __nativeAttributes), { 
        // https://github.com/microsoft/TypeScript/issues/36659
        ref: useMergeRefs(buttonRef, __internalRootRef), 'aria-label': ariaLabel, 'aria-expanded': ariaExpanded, className: buttonClass, onClick: handleClick });
    var iconProps = {
        loading: loading,
        iconName: iconName,
        iconAlign: iconAlign,
        iconUrl: iconUrl,
        iconSvg: iconSvg,
        iconAlt: iconAlt,
        variant: variant,
        iconClass: __iconClass,
        iconSize: variant === 'modal-dismiss' ? 'medium' : 'normal'
    };
    var buttonContent = (React.createElement(React.Fragment, null,
        React.createElement(LeftIcon, __assign({}, iconProps)),
        shouldHaveContent && React.createElement("span", { className: styles.content }, children),
        React.createElement(RightIcon, __assign({}, iconProps))));
    if (isAnchor) {
        return (
        // https://github.com/yannickcr/eslint-plugin-react/issues/2962
        // eslint-disable-next-line react/jsx-no-target-blank
        React.createElement(React.Fragment, null,
            React.createElement("a", __assign({}, buttonProps, { href: href, target: target, 
                // security recommendation: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a#target
                rel: target === '_blank' ? 'noopener noreferrer' : undefined, tabIndex: isDisabled ? -1 : undefined, "aria-disabled": isDisabled ? true : undefined, download: download }), buttonContent),
            loading && loadingText && React.createElement(LiveRegion, null, loadingText)));
    }
    return (React.createElement(React.Fragment, null,
        React.createElement("button", __assign({}, buttonProps, { type: formAction === 'none' ? 'button' : 'submit', disabled: isDisabled }), buttonContent),
        loading && loadingText && React.createElement(LiveRegion, null, loadingText)));
});
export default InternalButton;
//# sourceMappingURL=internal.js.map