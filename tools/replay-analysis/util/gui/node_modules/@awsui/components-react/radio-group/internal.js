import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React from 'react';
import { getBaseProps } from '../internal/base-component';
import RadioButton from './radio-button';
import styles from './styles.css.js';
import { useFormFieldContext } from '../internal/context/form-field-context';
import { useUniqueId } from '../internal/hooks/use-unique-id';
import useRadioGroupForwardFocus from '../internal/hooks/forward-focus/radio-group';
var InternalRadioGroup = React.forwardRef(function (_a, ref) {
    var name = _a.name, value = _a.value, items = _a.items, ariaLabel = _a.ariaLabel, ariaRequired = _a.ariaRequired, ariaControls = _a.ariaControls, onChange = _a.onChange, _b = _a.__internalRootRef, __internalRootRef = _b === void 0 ? null : _b, props = __rest(_a, ["name", "value", "items", "ariaLabel", "ariaRequired", "ariaControls", "onChange", "__internalRootRef"]);
    var _c = useFormFieldContext(props), ariaDescribedby = _c.ariaDescribedby, ariaLabelledby = _c.ariaLabelledby;
    var baseProps = getBaseProps(props);
    var generatedName = useUniqueId('awsui-radio-');
    var _d = useRadioGroupForwardFocus(ref, items, value), radioButtonRef = _d[0], radioButtonRefIndex = _d[1];
    return (React.createElement("div", __assign({ role: "radiogroup", "aria-labelledby": ariaLabelledby, "aria-label": ariaLabel, "aria-describedby": ariaDescribedby, "aria-required": ariaRequired, "aria-controls": ariaControls }, baseProps, { className: clsx(baseProps.className, styles.root), ref: __internalRootRef }), items &&
        items.map(function (item, index) { return (React.createElement(RadioButton, { key: item.value, ref: index === radioButtonRefIndex ? radioButtonRef : undefined, checked: item.value === value, name: name || generatedName, value: item.value, label: item.label, description: item.description, disabled: item.disabled, onChange: onChange, controlId: item.controlId })); })));
});
export default InternalRadioGroup;
//# sourceMappingURL=internal.js.map