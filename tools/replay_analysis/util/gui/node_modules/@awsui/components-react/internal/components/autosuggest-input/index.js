// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign, __rest } from "tslib";
import React, { useRef, useState, useImperativeHandle, useEffect } from 'react';
import Dropdown from '../dropdown';
import { useFormFieldContext } from '../../context/form-field-context';
import { getBaseProps } from '../../base-component';
import { fireCancelableEvent, fireNonCancelableEvent } from '../../events';
import InternalInput from '../../../input/internal';
import { KeyCode } from '../../keycode';
import styles from './styles.css.js';
import clsx from 'clsx';
var AutosuggestInput = React.forwardRef(function (_a, ref) {
    var value = _a.value, onChange = _a.onChange, onBlur = _a.onBlur, onFocus = _a.onFocus, onKeyUp = _a.onKeyUp, onKeyDown = _a.onKeyDown, name = _a.name, placeholder = _a.placeholder, disabled = _a.disabled, readOnly = _a.readOnly, autoFocus = _a.autoFocus, ariaLabel = _a.ariaLabel, ariaRequired = _a.ariaRequired, _b = _a.disableBrowserAutocorrect, disableBrowserAutocorrect = _b === void 0 ? false : _b, expandToViewport = _a.expandToViewport, ariaControls = _a.ariaControls, ariaActivedescendant = _a.ariaActivedescendant, clearAriaLabel = _a.clearAriaLabel, _c = _a.dropdownExpanded, dropdownExpanded = _c === void 0 ? true : _c, dropdownContentKey = _a.dropdownContentKey, _d = _a.dropdownContentFocusable, dropdownContentFocusable = _d === void 0 ? false : _d, _e = _a.dropdownContent, dropdownContent = _e === void 0 ? null : _e, _f = _a.dropdownFooter, dropdownFooter = _f === void 0 ? null : _f, dropdownWidth = _a.dropdownWidth, loopFocus = _a.loopFocus, onCloseDropdown = _a.onCloseDropdown, onDelayedInput = _a.onDelayedInput, onPressArrowDown = _a.onPressArrowDown, onPressArrowUp = _a.onPressArrowUp, onPressEnter = _a.onPressEnter, __internalRootRef = _a.__internalRootRef, restProps = __rest(_a, ["value", "onChange", "onBlur", "onFocus", "onKeyUp", "onKeyDown", "name", "placeholder", "disabled", "readOnly", "autoFocus", "ariaLabel", "ariaRequired", "disableBrowserAutocorrect", "expandToViewport", "ariaControls", "ariaActivedescendant", "clearAriaLabel", "dropdownExpanded", "dropdownContentKey", "dropdownContentFocusable", "dropdownContent", "dropdownFooter", "dropdownWidth", "loopFocus", "onCloseDropdown", "onDelayedInput", "onPressArrowDown", "onPressArrowUp", "onPressEnter", "__internalRootRef"]);
    var baseProps = getBaseProps(restProps);
    var formFieldContext = useFormFieldContext(restProps);
    var inputRef = useRef(null);
    var dropdownContentRef = useRef(null);
    var dropdownFooterRef = useRef(null);
    var preventOpenOnFocusRef = useRef(false);
    var preventCloseOnBlurRef = useRef(false);
    var _g = useState(false), open = _g[0], setOpen = _g[1];
    var openDropdown = function () { return !readOnly && setOpen(true); };
    var closeDropdown = function () {
        setOpen(false);
        fireNonCancelableEvent(onCloseDropdown, null);
    };
    useImperativeHandle(ref, function () { return ({
        focus: function (options) {
            var _a;
            if (options === null || options === void 0 ? void 0 : options.preventDropdown) {
                preventOpenOnFocusRef.current = true;
            }
            (_a = inputRef.current) === null || _a === void 0 ? void 0 : _a.focus();
        },
        select: function () {
            var _a;
            (_a = inputRef.current) === null || _a === void 0 ? void 0 : _a.select();
        },
        open: openDropdown,
        close: closeDropdown
    }); });
    var handleBlur = function () {
        if (!preventCloseOnBlurRef.current) {
            closeDropdown();
            fireNonCancelableEvent(onBlur, null);
        }
    };
    var handleFocus = function () {
        if (!preventOpenOnFocusRef.current) {
            openDropdown();
            fireNonCancelableEvent(onFocus, null);
        }
        preventOpenOnFocusRef.current = false;
    };
    var handleKeyDown = function (e) {
        switch (e.detail.keyCode) {
            case KeyCode.down: {
                onPressArrowDown === null || onPressArrowDown === void 0 ? void 0 : onPressArrowDown();
                openDropdown();
                e.preventDefault();
                break;
            }
            case KeyCode.up: {
                onPressArrowUp === null || onPressArrowUp === void 0 ? void 0 : onPressArrowUp();
                openDropdown();
                e.preventDefault();
                break;
            }
            case KeyCode.enter: {
                if (open) {
                    if (!(onPressEnter === null || onPressEnter === void 0 ? void 0 : onPressEnter())) {
                        closeDropdown();
                    }
                    e.preventDefault();
                }
                fireCancelableEvent(onKeyDown, e.detail);
                break;
            }
            case KeyCode.escape: {
                if (open) {
                    closeDropdown();
                }
                else if (value) {
                    fireNonCancelableEvent(onChange, { value: '' });
                }
                e.preventDefault();
                fireCancelableEvent(onKeyDown, e.detail);
                break;
            }
            default: {
                fireCancelableEvent(onKeyDown, e.detail);
            }
        }
    };
    var handleChange = function (value) {
        openDropdown();
        fireNonCancelableEvent(onChange, { value: value });
    };
    var handleDelayedInput = function (value) {
        fireNonCancelableEvent(onDelayedInput, { value: value });
    };
    var handleDropdownMouseDown = function (event) {
        // Prevent currently focused element from losing focus.
        if (!dropdownContentFocusable) {
            event.preventDefault();
        }
        // Prevent closing dropdown on click inside.
        else {
            preventCloseOnBlurRef.current = true;
            requestAnimationFrame(function () {
                preventCloseOnBlurRef.current = false;
            });
        }
    };
    var expanded = open && dropdownExpanded;
    var nativeAttributes = {
        name: name,
        placeholder: placeholder,
        autoFocus: autoFocus,
        onClick: openDropdown,
        role: 'combobox',
        'aria-autocomplete': 'list',
        'aria-expanded': expanded,
        'aria-controls': open ? ariaControls : undefined,
        // 'aria-owns' needed for safari+vo to announce activedescendant content
        'aria-owns': open ? ariaControls : undefined,
        'aria-label': ariaLabel,
        'aria-activedescendant': ariaActivedescendant
    };
    // Closes dropdown when outside click is detected.
    // Similar to the internal dropdown implementation but includes the target as well.
    useEffect(function () {
        if (!open) {
            return;
        }
        var clickListener = function (event) {
            var _a, _b, _c;
            if (!((_a = inputRef.current) === null || _a === void 0 ? void 0 : _a.contains(event.target)) &&
                !((_b = dropdownContentRef.current) === null || _b === void 0 ? void 0 : _b.contains(event.target)) &&
                !((_c = dropdownFooterRef.current) === null || _c === void 0 ? void 0 : _c.contains(event.target))) {
                closeDropdown();
            }
        };
        window.addEventListener('mousedown', clickListener);
        return function () {
            window.removeEventListener('mousedown', clickListener);
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [open]);
    return (React.createElement("div", __assign({}, baseProps, { className: clsx(baseProps.className, styles.root), ref: __internalRootRef }),
        React.createElement(Dropdown, { minWidth: dropdownWidth, stretchWidth: !dropdownWidth, contentKey: dropdownContentKey, onFocus: handleFocus, onBlur: handleBlur, trigger: React.createElement(InternalInput, __assign({ type: "visualSearch", value: value, onChange: function (event) { return handleChange(event.detail.value); }, __onDelayedInput: function (event) { return handleDelayedInput(event.detail.value); }, onKeyDown: handleKeyDown, onKeyUp: onKeyUp, disabled: disabled, disableBrowserAutocorrect: disableBrowserAutocorrect, readOnly: readOnly, ariaRequired: ariaRequired, clearAriaLabel: clearAriaLabel, ref: inputRef, autoComplete: false, __nativeAttributes: nativeAttributes }, formFieldContext)), onMouseDown: handleDropdownMouseDown, open: open, footer: dropdownFooterRef && (React.createElement("div", { ref: dropdownFooterRef, className: styles['dropdown-footer'] }, dropdownFooter)), expandToViewport: expandToViewport, loopFocus: loopFocus }, open && dropdownContent ? (React.createElement("div", { ref: dropdownContentRef, className: styles['dropdown-content'] }, dropdownContent)) : null)));
});
export default AutosuggestInput;
//# sourceMappingURL=index.js.map