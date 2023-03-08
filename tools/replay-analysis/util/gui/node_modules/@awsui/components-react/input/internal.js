import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useRef, useEffect } from 'react';
import clsx from 'clsx';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import InternalIcon from '../icon/internal';
import InternalButton from '../button/internal';
import { fireNonCancelableEvent, fireKeyboardEvent } from '../internal/events';
import { getBaseProps } from '../internal/base-component';
import { useSearchProps, convertAutoComplete } from './utils';
import { useDebounceCallback } from '../internal/hooks/use-debounce-callback';
import { useFormFieldContext } from '../internal/context/form-field-context';
import styles from './styles.css.js';
function InternalInput(_a, ref) {
    var _b;
    var _c = _a.type, type = _c === void 0 ? 'text' : _c, step = _a.step, inputMode = _a.inputMode, _d = _a.autoComplete, autoComplete = _d === void 0 ? true : _d, ariaLabel = _a.ariaLabel, clearAriaLabel = _a.clearAriaLabel, name = _a.name, value = _a.value, placeholder = _a.placeholder, autoFocus = _a.autoFocus, disabled = _a.disabled, readOnly = _a.readOnly, disableBrowserAutocorrect = _a.disableBrowserAutocorrect, spellcheck = _a.spellcheck, __noBorderRadius = _a.__noBorderRadius, __leftIcon = _a.__leftIcon, _e = _a.__leftIconVariant, __leftIconVariant = _e === void 0 ? 'subtle' : _e, __onLeftIconClick = _a.__onLeftIconClick, ariaRequired = _a.ariaRequired, __rightIcon = _a.__rightIcon, __onRightIconClick = _a.__onRightIconClick, onKeyDown = _a.onKeyDown, onKeyUp = _a.onKeyUp, onChange = _a.onChange, __onDelayedInput = _a.__onDelayedInput, __onBlurWithDetail = _a.__onBlurWithDetail, onBlur = _a.onBlur, onFocus = _a.onFocus, __nativeAttributes = _a.__nativeAttributes, __internalRootRef = _a.__internalRootRef, __inheritFormFieldProps = _a.__inheritFormFieldProps, rest = __rest(_a, ["type", "step", "inputMode", "autoComplete", "ariaLabel", "clearAriaLabel", "name", "value", "placeholder", "autoFocus", "disabled", "readOnly", "disableBrowserAutocorrect", "spellcheck", "__noBorderRadius", "__leftIcon", "__leftIconVariant", "__onLeftIconClick", "ariaRequired", "__rightIcon", "__onRightIconClick", "onKeyDown", "onKeyUp", "onChange", "__onDelayedInput", "__onBlurWithDetail", "onBlur", "onFocus", "__nativeAttributes", "__internalRootRef", "__inheritFormFieldProps"]);
    var baseProps = getBaseProps(rest);
    var fireDelayedInput = useDebounceCallback(function (value) { return fireNonCancelableEvent(__onDelayedInput, { value: value }); });
    var handleChange = function (value) {
        fireDelayedInput(value);
        fireNonCancelableEvent(onChange, { value: value });
    };
    var inputRef = useRef(null);
    var searchProps = useSearchProps(type, disabled, readOnly, value, inputRef, handleChange);
    __leftIcon = __leftIcon !== null && __leftIcon !== void 0 ? __leftIcon : searchProps.__leftIcon;
    __rightIcon = __rightIcon !== null && __rightIcon !== void 0 ? __rightIcon : searchProps.__rightIcon;
    __onRightIconClick = __onRightIconClick !== null && __onRightIconClick !== void 0 ? __onRightIconClick : searchProps.__onRightIconClick;
    var formFieldContext = useFormFieldContext(rest);
    var _f = __inheritFormFieldProps
        ? formFieldContext
        : __assign({ __useReactAutofocus: undefined }, rest), ariaLabelledby = _f.ariaLabelledby, ariaDescribedby = _f.ariaDescribedby, controlId = _f.controlId, invalid = _f.invalid, __useReactAutofocus = _f.__useReactAutofocus;
    var autoFocusEnabled = (__nativeAttributes === null || __nativeAttributes === void 0 ? void 0 : __nativeAttributes.autoFocus) || autoFocus;
    var reactAutofocusProps = __useReactAutofocus
        ? { autoFocus: !autoFocusEnabled, 'data-awsui-react-autofocus': autoFocusEnabled }
        : {};
    var attributes = __assign(__assign({ 'aria-label': ariaLabel, 'aria-labelledby': ariaLabelledby, 'aria-describedby': ariaDescribedby, name: name, placeholder: placeholder, autoFocus: autoFocus, id: controlId, className: clsx(styles.input, type && styles["input-type-".concat(type)], __rightIcon && styles['input-has-icon-right'], __leftIcon && styles['input-has-icon-left'], __noBorderRadius && styles['input-has-no-border-radius'], (_b = {},
            _b[styles['input-readonly']] = readOnly,
            _b[styles['input-invalid']] = invalid,
            _b)), autoComplete: convertAutoComplete(autoComplete), disabled: disabled, readOnly: readOnly, type: type, step: step, inputMode: inputMode, spellCheck: spellcheck, onKeyDown: onKeyDown && (function (event) { return fireKeyboardEvent(onKeyDown, event); }), onKeyUp: onKeyUp && (function (event) { return fireKeyboardEvent(onKeyUp, event); }), 
        // We set a default value on the component in order to force it into the controlled mode.
        value: value !== null && value !== void 0 ? value : '', onChange: onChange && (function (event) { return handleChange(event.target.value); }), onBlur: function (e) {
            onBlur && fireNonCancelableEvent(onBlur);
            __onBlurWithDetail && fireNonCancelableEvent(__onBlurWithDetail, { relatedTarget: e.relatedTarget });
        }, onFocus: onFocus && (function () { return fireNonCancelableEvent(onFocus); }) }, __nativeAttributes), reactAutofocusProps);
    if (type === 'number') {
        // Chrome and Safari have a weird built-in behavior of letting focused
        // number inputs be controlled by scrolling on them. However, they don't
        // lock the browser's scroll, so it's very easy to accidentally increment
        // the input while scrolling down the page.
        attributes.onWheel = function (event) { return event.currentTarget.blur(); };
    }
    if (disableBrowserAutocorrect) {
        attributes.autoCorrect = 'off';
        attributes.autoCapitalize = 'off';
    }
    // ensure aria properties are string literal "true"
    if (ariaRequired) {
        attributes['aria-required'] = 'true';
    }
    if (invalid) {
        attributes['aria-invalid'] = 'true';
    }
    var mergedRef = useMergeRefs(ref, inputRef);
    // type = "visualSearch" renders a type="text' input
    if (attributes.type === 'visualSearch') {
        attributes.type = 'text';
    }
    useEffect(function () {
        var _a;
        if (__useReactAutofocus && autoFocusEnabled) {
            (_a = inputRef.current) === null || _a === void 0 ? void 0 : _a.focus({ preventScroll: true });
        }
    }, [__useReactAutofocus, autoFocusEnabled]);
    return (React.createElement("div", __assign({}, baseProps, { className: clsx(baseProps.className, styles['input-container']), ref: __internalRootRef }),
        __leftIcon && (React.createElement("span", { onClick: __onLeftIconClick, className: styles['input-icon-left'] },
            React.createElement(InternalIcon, { name: __leftIcon, variant: disabled ? 'disabled' : __leftIconVariant }))),
        React.createElement("input", __assign({ ref: mergedRef }, attributes)),
        __rightIcon && (React.createElement("span", { className: styles['input-icon-right'] },
            React.createElement(InternalButton
            // Used for test utils
            // eslint-disable-next-line react/forbid-component-props
            , { 
                // Used for test utils
                // eslint-disable-next-line react/forbid-component-props
                className: styles['input-button-right'], variant: "inline-icon", formAction: "none", iconName: __rightIcon, onClick: __onRightIconClick, ariaLabel: clearAriaLabel, disabled: disabled })))));
}
export default React.forwardRef(InternalInput);
//# sourceMappingURL=internal.js.map