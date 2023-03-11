import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useEffect, useRef } from 'react';
import { fireNonCancelableEvent } from '../internal/events';
import useForwardFocus from '../internal/hooks/forward-focus';
import { getBaseProps } from '../internal/base-component';
import AbstractSwitch from '../internal/components/abstract-switch';
import styles from './styles.css.js';
import CheckboxIcon from '../internal/components/checkbox-icon';
import { useFormFieldContext } from '../internal/context/form-field-context';
var InternalCheckbox = React.forwardRef(function (_a, ref) {
    var controlId = _a.controlId, name = _a.name, checked = _a.checked, disabled = _a.disabled, indeterminate = _a.indeterminate, children = _a.children, description = _a.description, ariaLabel = _a.ariaLabel, onFocus = _a.onFocus, onBlur = _a.onBlur, onChange = _a.onChange, tabIndex = _a.tabIndex, __internalRootRef = _a.__internalRootRef, rest = __rest(_a, ["controlId", "name", "checked", "disabled", "indeterminate", "children", "description", "ariaLabel", "onFocus", "onBlur", "onChange", "tabIndex", "__internalRootRef"]);
    var _b = useFormFieldContext(rest), ariaDescribedby = _b.ariaDescribedby, ariaLabelledby = _b.ariaLabelledby;
    var baseProps = getBaseProps(rest);
    var checkboxRef = useRef(null);
    useForwardFocus(ref, checkboxRef);
    useEffect(function () {
        if (checkboxRef.current) {
            checkboxRef.current.indeterminate = Boolean(indeterminate);
        }
    });
    return (React.createElement(AbstractSwitch, __assign({}, baseProps, { className: clsx(styles.root, baseProps.className), controlClassName: styles['checkbox-control'], outlineClassName: styles.outline, controlId: controlId, disabled: disabled, label: children, description: description, descriptionBottomPadding: true, ariaLabel: ariaLabel, ariaLabelledby: ariaLabelledby, ariaDescribedby: ariaDescribedby, nativeControl: function (nativeControlProps) { return (React.createElement("input", __assign({}, nativeControlProps, { ref: checkboxRef, type: "checkbox", checked: checked, name: name, tabIndex: tabIndex, onFocus: function () { return fireNonCancelableEvent(onFocus); }, onBlur: function () { return fireNonCancelableEvent(onBlur); }, 
            // empty handler to suppress React controllability warning
            onChange: function () { } }))); }, onClick: function () {
            var _a;
            (_a = checkboxRef.current) === null || _a === void 0 ? void 0 : _a.focus();
            fireNonCancelableEvent(onChange, 
            // for deterministic transitions "indeterminate" -> "checked" -> "unchecked"
            indeterminate ? { checked: true, indeterminate: false } : { checked: !checked, indeterminate: false });
        }, styledControl: React.createElement(CheckboxIcon, { checked: checked, indeterminate: indeterminate, disabled: disabled }), __internalRootRef: __internalRootRef })));
});
export default InternalCheckbox;
//# sourceMappingURL=internal.js.map