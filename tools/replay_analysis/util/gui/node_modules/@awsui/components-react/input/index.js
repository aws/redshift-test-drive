import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useImperativeHandle, useRef } from 'react';
import { getBaseProps } from '../internal/base-component';
import InternalInput from './internal';
import styles from './styles.css.js';
import { applyDisplayName } from '../internal/utils/apply-display-name';
import useBaseComponent from '../internal/hooks/use-base-component';
var Input = React.forwardRef(function (_a, ref) {
    var value = _a.value, _b = _a.type, type = _b === void 0 ? 'text' : _b, step = _a.step, inputMode = _a.inputMode, _c = _a.autoComplete, autoComplete = _c === void 0 ? true : _c, spellcheck = _a.spellcheck, disabled = _a.disabled, readOnly = _a.readOnly, disableBrowserAutocorrect = _a.disableBrowserAutocorrect, onKeyDown = _a.onKeyDown, onKeyUp = _a.onKeyUp, onChange = _a.onChange, onBlur = _a.onBlur, onFocus = _a.onFocus, ariaRequired = _a.ariaRequired, name = _a.name, placeholder = _a.placeholder, autoFocus = _a.autoFocus, ariaLabel = _a.ariaLabel, ariaLabelledby = _a.ariaLabelledby, ariaDescribedby = _a.ariaDescribedby, invalid = _a.invalid, controlId = _a.controlId, clearAriaLabel = _a.clearAriaLabel, rest = __rest(_a, ["value", "type", "step", "inputMode", "autoComplete", "spellcheck", "disabled", "readOnly", "disableBrowserAutocorrect", "onKeyDown", "onKeyUp", "onChange", "onBlur", "onFocus", "ariaRequired", "name", "placeholder", "autoFocus", "ariaLabel", "ariaLabelledby", "ariaDescribedby", "invalid", "controlId", "clearAriaLabel"]);
    var baseComponentProps = useBaseComponent('Input');
    var baseProps = getBaseProps(rest);
    var inputRef = useRef(null);
    useImperativeHandle(ref, function () { return ({
        focus: function () {
            var _a;
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            (_a = inputRef.current) === null || _a === void 0 ? void 0 : _a.focus.apply(_a, args);
        },
        select: function () {
            var _a;
            (_a = inputRef.current) === null || _a === void 0 ? void 0 : _a.select();
        }
    }); }, [inputRef]);
    return (React.createElement(InternalInput, __assign({ ref: inputRef }, __assign(__assign(__assign({}, baseProps), baseComponentProps), { autoComplete: autoComplete, ariaLabel: ariaLabel, ariaRequired: ariaRequired, autoFocus: autoFocus, disabled: disabled, disableBrowserAutocorrect: disableBrowserAutocorrect, name: name, onKeyDown: onKeyDown, onKeyUp: onKeyUp, onChange: onChange, onBlur: onBlur, onFocus: onFocus, placeholder: placeholder, readOnly: readOnly, type: type, step: step, inputMode: inputMode, spellcheck: spellcheck, value: value, ariaDescribedby: ariaDescribedby, ariaLabelledby: ariaLabelledby, invalid: invalid, controlId: controlId, clearAriaLabel: clearAriaLabel }), { className: clsx(styles.root, baseProps.className), __inheritFormFieldProps: true })));
});
applyDisplayName(Input, 'Input');
export default Input;
//# sourceMappingURL=index.js.map