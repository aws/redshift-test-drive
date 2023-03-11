// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useState } from 'react';
import styles from './styles.css.js';
import InternalButton from '../button/internal';
import InternalFormField from '../form-field/internal';
export function PropertyEditor(_a) {
    var property = _a.property, operator = _a.operator, filter = _a.filter, operatorForm = _a.operatorForm, onCancel = _a.onCancel, onSubmit = _a.onSubmit, i18nStrings = _a.i18nStrings;
    var _b = useState(null), value = _b[0], onChange = _b[1];
    var submitToken = function () { return onSubmit({ propertyKey: property.key, operator: operator, value: value }); };
    return (React.createElement("div", { className: styles['property-editor'] },
        React.createElement("div", { className: styles['property-editor-form'] },
            React.createElement(InternalFormField, { label: property.groupValuesLabel }, operatorForm({ value: value, onChange: onChange, operator: operator, filter: filter }))),
        React.createElement("div", { className: styles['property-editor-actions'] },
            React.createElement(InternalButton, { variant: "link", className: styles['property-editor-cancel'], onClick: onCancel }, i18nStrings.cancelActionText),
            React.createElement(InternalButton, { className: styles['property-editor-submit'], onClick: submitToken }, i18nStrings.applyActionText))));
}
//# sourceMappingURL=property-editor.js.map