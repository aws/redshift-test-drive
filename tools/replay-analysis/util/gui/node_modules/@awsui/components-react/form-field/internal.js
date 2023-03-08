import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import clsx from 'clsx';
import { getBaseProps } from '../internal/base-component';
import { FormFieldContext, useFormFieldContext } from '../internal/context/form-field-context';
import { useUniqueId } from '../internal/hooks/use-unique-id';
import { useVisualRefresh } from '../internal/hooks/use-visual-mode';
import InternalGrid from '../grid/internal';
import InternalIcon from '../icon/internal';
import { getAriaDescribedBy, getGridDefinition, getSlotIds } from './util';
import styles from './styles.css.js';
import { joinStrings } from '../internal/utils/strings';
export var FormFieldError = function (_a) {
    var id = _a.id, children = _a.children, errorIconAriaLabel = _a.errorIconAriaLabel;
    return (React.createElement("div", { id: id, className: styles.error },
        React.createElement("div", { className: styles['error-icon-shake-wrapper'] },
            React.createElement("div", { role: "img", "aria-label": errorIconAriaLabel, className: styles['error-icon-scale-wrapper'] },
                React.createElement(InternalIcon, { name: "status-warning", size: "small" }))),
        React.createElement("span", { className: styles.error__message }, children)));
};
export default function InternalFormField(_a) {
    var controlId = _a.controlId, _b = _a.stretch, stretch = _b === void 0 ? false : _b, label = _a.label, info = _a.info, i18nStrings = _a.i18nStrings, children = _a.children, secondaryControl = _a.secondaryControl, description = _a.description, constraintText = _a.constraintText, errorText = _a.errorText, __hideLabel = _a.__hideLabel, _c = _a.__internalRootRef, __internalRootRef = _c === void 0 ? null : _c, _d = _a.__disableGutters, __disableGutters = _d === void 0 ? false : _d, _e = _a.__useReactAutofocus, __useReactAutofocus = _e === void 0 ? false : _e, rest = __rest(_a, ["controlId", "stretch", "label", "info", "i18nStrings", "children", "secondaryControl", "description", "constraintText", "errorText", "__hideLabel", "__internalRootRef", "__disableGutters", "__useReactAutofocus"]);
    var baseProps = getBaseProps(rest);
    var isRefresh = useVisualRefresh();
    var instanceUniqueId = useUniqueId('formField');
    var generatedControlId = controlId || instanceUniqueId;
    var formFieldId = controlId || generatedControlId;
    var slotIds = getSlotIds(formFieldId, label, description, constraintText, errorText);
    var ariaDescribedBy = getAriaDescribedBy(slotIds);
    var gridDefinition = getGridDefinition(stretch, !!secondaryControl, isRefresh);
    var _f = useFormFieldContext({}), parentAriaLabelledby = _f.ariaLabelledby, parentAriaDescribedby = _f.ariaDescribedby, parentInvalid = _f.invalid;
    var contextValuesWithoutControlId = {
        ariaLabelledby: joinStrings(parentAriaLabelledby, slotIds.label) || undefined,
        ariaDescribedby: joinStrings(parentAriaDescribedby, ariaDescribedBy) || undefined,
        invalid: !!errorText || !!parentInvalid,
        __useReactAutofocus: __useReactAutofocus
    };
    return (React.createElement("div", __assign({}, baseProps, { className: clsx(baseProps.className, styles.root), ref: __internalRootRef }),
        React.createElement("div", { className: clsx(__hideLabel && styles['visually-hidden']) },
            label && (React.createElement("label", { className: styles.label, id: slotIds.label, htmlFor: generatedControlId }, label)),
            !__hideLabel && info && React.createElement("span", { className: styles.info }, info)),
        description && (React.createElement("div", { className: styles.description, id: slotIds.description }, description)),
        React.createElement("div", { className: clsx(styles.controls, __hideLabel && styles['label-hidden']) },
            React.createElement(InternalGrid, { gridDefinition: gridDefinition, disableGutters: __disableGutters },
                React.createElement(FormFieldContext.Provider, { value: __assign({ controlId: generatedControlId }, contextValuesWithoutControlId) }, children && React.createElement("div", { className: styles.control }, children)),
                secondaryControl && (React.createElement(FormFieldContext.Provider, { value: contextValuesWithoutControlId },
                    React.createElement("div", { className: styles['secondary-control'] }, secondaryControl))))),
        (constraintText || errorText) && (React.createElement("div", { className: styles.hints },
            errorText && (React.createElement(FormFieldError, { id: slotIds.error, errorIconAriaLabel: i18nStrings === null || i18nStrings === void 0 ? void 0 : i18nStrings.errorIconAriaLabel }, errorText)),
            constraintText && (React.createElement("div", { className: clsx(styles.constraint, errorText && styles['constraint-has-error']), id: slotIds.constraint }, constraintText))))));
}
//# sourceMappingURL=internal.js.map