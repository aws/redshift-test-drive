import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useEffect, useRef, useState } from 'react';
import InternalIcon from '../../icon/internal';
import styles from './styles.css.js';
import clsx from 'clsx';
import useFocusVisible from '../../internal/hooks/focus-visible';
import { fireCancelableEvent, isPlainLeftClick } from '../../internal/events';
import { getEventDetail } from '../internal';
import { Transition } from '../../internal/components/transition';
import PopoverContainer from '../../popover/container';
import PopoverBody from '../../popover/body';
import Portal from '../../internal/components/portal';
import popoverStyles from '../../popover/styles.css.js';
var BreadcrumbItemWithPopover = function (_a) {
    var item = _a.item, anchorAttributes = __rest(_a, ["item"]);
    var focusVisible = useFocusVisible();
    var _b = useState(false), showPopover = _b[0], setShowPopover = _b[1];
    var textRef = useRef(null);
    var virtualTextRef = useRef(null);
    var isTruncated = function (textRef, virtualTextRef) {
        if (!textRef || !virtualTextRef || !textRef.current || !virtualTextRef.current) {
            return false;
        }
        var virtualTextWidth = virtualTextRef.current.getBoundingClientRect().width;
        var textWidth = textRef.current.getBoundingClientRect().width;
        if (virtualTextWidth > textWidth) {
            return true;
        }
        return false;
    };
    var popoverContent = (React.createElement(Portal, null,
        React.createElement("div", { className: styles['item-popover'] },
            React.createElement(Transition, { "in": true }, function () { return (React.createElement(PopoverContainer, { trackRef: textRef, size: "small", fixedWidth: false, position: "bottom", arrow: function (position) { return (React.createElement("div", { className: clsx(popoverStyles.arrow, popoverStyles["arrow-position-".concat(position)]) },
                    React.createElement("div", { className: popoverStyles['arrow-outer'] }),
                    React.createElement("div", { className: popoverStyles['arrow-inner'] }))); } },
                React.createElement(PopoverBody, { dismissButton: false, dismissAriaLabel: undefined, onDismiss: function () { }, header: undefined }, item.text))); }))));
    useEffect(function () {
        var onKeyDown = function (event) {
            if (event.key === 'Escape') {
                setShowPopover(false);
            }
        };
        if (showPopover) {
            document.addEventListener('keydown', onKeyDown);
        }
        return function () {
            document.removeEventListener('keydown', onKeyDown);
        };
    }, [showPopover]);
    return (React.createElement(React.Fragment, null,
        React.createElement("a", __assign({}, focusVisible, anchorAttributes, { onFocus: function () {
                isTruncated(textRef, virtualTextRef) && setShowPopover(true);
            }, onBlur: function () { return setShowPopover(false); }, onMouseEnter: function () {
                isTruncated(textRef, virtualTextRef) && setShowPopover(true);
            }, onMouseLeave: function () { return setShowPopover(false); } }),
            React.createElement("span", { className: styles.text, ref: textRef }, item.text),
            React.createElement("span", { className: styles['virtual-item'], ref: virtualTextRef }, item.text)),
        showPopover && popoverContent));
};
export function BreadcrumbItem(_a) {
    var _b;
    var item = _a.item, onClick = _a.onClick, onFollow = _a.onFollow, isDisplayed = _a.isDisplayed, _c = _a.isLast, isLast = _c === void 0 ? false : _c, _d = _a.isCompressed, isCompressed = _d === void 0 ? false : _d;
    var focusVisible = useFocusVisible();
    var preventDefault = function (event) { return event.preventDefault(); };
    var onClickHandler = function (event) {
        if (isPlainLeftClick(event)) {
            fireCancelableEvent(onFollow, getEventDetail(item), event);
        }
        fireCancelableEvent(onClick, getEventDetail(item), event);
    };
    var anchorAttributes = {
        href: isLast ? undefined : item.href || '#',
        className: clsx(styles.anchor, (_b = {}, _b[styles.compressed] = isCompressed, _b)),
        'aria-current': isLast ? 'page' : undefined,
        'aria-disabled': isLast && 'true',
        onClick: isLast ? preventDefault : onClickHandler,
        tabIndex: isLast ? 0 : undefined
    };
    return (React.createElement(React.Fragment, null,
        React.createElement("div", { className: clsx(styles.breadcrumb, isLast && styles.last) },
            isDisplayed && isCompressed ? (React.createElement(BreadcrumbItemWithPopover, __assign({ item: item }, anchorAttributes))) : (React.createElement("a", __assign({}, focusVisible, anchorAttributes),
                React.createElement("span", { className: styles.text }, item.text))),
            !isLast ? (React.createElement("span", { className: styles.icon },
                React.createElement(InternalIcon, { name: "angle-right" }))) : null)));
}
//# sourceMappingURL=item.js.map