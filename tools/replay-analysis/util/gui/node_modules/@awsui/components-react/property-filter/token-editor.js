import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useState, useRef } from 'react';
import InternalSelect from '../select/internal';
import InternalAutosuggest from '../autosuggest/internal';
import InternalPopover from '../popover/internal';
import styles from './styles.css.js';
import { useLoadItems } from './use-load-items';
import { createPropertiesCompatibilityMap, getAllowedOperators, getPropertyOptions, getPropertyByKey, operatorToDescription, getPropertySuggestions, getExtendedOperator, } from './controller';
import InternalButton from '../button/internal';
import InternalFormField from '../form-field/internal';
import { matchTokenValue } from './utils';
var freeTextOperators = [':', '!:'];
function PropertyInput(_a) {
    var propertyKey = _a.propertyKey, onChangePropertyKey = _a.onChangePropertyKey, asyncProps = _a.asyncProps, filteringProperties = _a.filteringProperties, onLoadItems = _a.onLoadItems, customGroupsText = _a.customGroupsText, i18nStrings = _a.i18nStrings, disableFreeTextFiltering = _a.disableFreeTextFiltering;
    var property = propertyKey !== undefined ? getPropertyByKey(filteringProperties, propertyKey) : undefined;
    var propertySelectHandlers = useLoadItems(onLoadItems);
    var asyncPropertySelectProps = asyncProps ? __assign(__assign({}, asyncProps), propertySelectHandlers) : {};
    var propertyOptions = getPropertySuggestions(filteringProperties, customGroupsText, i18nStrings, function (_a) {
        var propertyLabel = _a.propertyLabel, key = _a.key;
        return ({
            value: key,
            label: propertyLabel,
            dontCloseOnSelect: true
        });
    });
    // Disallow selecting properties that have different representation.
    var checkPropertiesCompatible = createPropertiesCompatibilityMap(filteringProperties);
    propertyOptions.forEach(function (optionGroup) {
        if ('options' in optionGroup) {
            optionGroup.options.forEach(function (option) {
                if (propertyKey && option.value) {
                    option.disabled = !checkPropertiesCompatible(option.value, propertyKey);
                }
            });
        }
    });
    var allPropertiesOption = {
        label: i18nStrings.allPropertiesLabel,
        value: undefined
    };
    if (!disableFreeTextFiltering) {
        propertyOptions.unshift(allPropertiesOption);
    }
    return (React.createElement(InternalSelect, __assign({ options: propertyOptions, selectedOption: property
            ? {
                value: propertyKey !== null && propertyKey !== void 0 ? propertyKey : undefined,
                label: property.propertyLabel
            }
            : allPropertiesOption, onChange: function (e) { return onChangePropertyKey(e.detail.selectedOption.value); } }, asyncPropertySelectProps)));
}
function OperatorInput(_a) {
    var propertyKey = _a.propertyKey, operator = _a.operator, onChangeOperator = _a.onChangeOperator, filteringProperties = _a.filteringProperties, i18nStrings = _a.i18nStrings;
    var property = propertyKey !== undefined ? getPropertyByKey(filteringProperties, propertyKey) : undefined;
    var freeTextOperators = [':', '!:'];
    var operatorOptions = (property ? getAllowedOperators(property) : freeTextOperators).map(function (operator) { return ({
        value: operator,
        label: operator,
        description: operatorToDescription(operator, i18nStrings)
    }); });
    return (React.createElement(InternalSelect, { options: operatorOptions, triggerVariant: "option", selectedOption: operator
            ? {
                value: operator,
                label: operator,
                description: operatorToDescription(operator, i18nStrings)
            }
            : null, onChange: function (e) { return onChangeOperator(e.detail.selectedOption.value); } }));
}
function ValueInput(_a) {
    var _b, _c, _d;
    var propertyKey = _a.propertyKey, operator = _a.operator, value = _a.value, onChangeValue = _a.onChangeValue, asyncProps = _a.asyncProps, filteringProperties = _a.filteringProperties, filteringOptions = _a.filteringOptions, onLoadItems = _a.onLoadItems, i18nStrings = _a.i18nStrings;
    var property = propertyKey !== undefined ? getPropertyByKey(filteringProperties, propertyKey) : undefined;
    var valueOptions = property
        ? getPropertyOptions(property, filteringOptions).map(function (_a) {
            var label = _a.label, value = _a.value;
            return ({ label: label, value: value });
        })
        : [];
    var valueAutosuggestHandlers = useLoadItems(onLoadItems, '', property);
    var asyncValueAutosuggesProps = propertyKey
        ? __assign(__assign({}, valueAutosuggestHandlers), asyncProps) : { empty: asyncProps.empty };
    var mathedOption = valueOptions.filter(function (option) { return option.value === value; })[0];
    var OperatorForm = propertyKey && operator && ((_b = getExtendedOperator(filteringProperties, propertyKey, operator)) === null || _b === void 0 ? void 0 : _b.form);
    return OperatorForm ? (React.createElement(OperatorForm, { value: value, onChange: onChangeValue, operator: operator })) : (React.createElement(InternalAutosuggest, __assign({ enteredTextLabel: i18nStrings.enteredTextLabel, value: (_d = (_c = mathedOption === null || mathedOption === void 0 ? void 0 : mathedOption.label) !== null && _c !== void 0 ? _c : value) !== null && _d !== void 0 ? _d : '', clearAriaLabel: i18nStrings.clearAriaLabel, onChange: function (e) { return onChangeValue(e.detail.value); }, disabled: !operator, options: valueOptions }, asyncValueAutosuggesProps, { virtualScroll: true })));
}
export function TokenEditor(_a) {
    var asyncProperties = _a.asyncProperties, asyncProps = _a.asyncProps, customGroupsText = _a.customGroupsText, disableFreeTextFiltering = _a.disableFreeTextFiltering, expandToViewport = _a.expandToViewport, filteringOptions = _a.filteringOptions, filteringProperties = _a.filteringProperties, i18nStrings = _a.i18nStrings, onLoadItems = _a.onLoadItems, setToken = _a.setToken, token = _a.token, triggerComponent = _a.triggerComponent;
    var _b = useState(token), temporaryToken = _b[0], setTemporaryToken = _b[1];
    var popoverRef = useRef(null);
    var closePopover = function () {
        popoverRef.current && popoverRef.current.dismissPopover();
    };
    var propertyKey = temporaryToken.propertyKey;
    var onChangePropertyKey = function (newPropertyKey) {
        var filteringProperty = filteringProperties.reduce(function (acc, property) { return (property.key === newPropertyKey ? property : acc); }, undefined);
        var allowedOperators = filteringProperty ? getAllowedOperators(filteringProperty) : freeTextOperators;
        var operator = temporaryToken.operator && allowedOperators.indexOf(temporaryToken.operator) !== -1
            ? temporaryToken.operator
            : allowedOperators[0];
        setTemporaryToken(__assign(__assign({}, temporaryToken), { propertyKey: newPropertyKey, operator: operator }));
    };
    var operator = temporaryToken.operator;
    var onChangeOperator = function (newOperator) {
        setTemporaryToken(__assign(__assign({}, temporaryToken), { operator: newOperator }));
    };
    var value = temporaryToken.value;
    var onChangeValue = function (newValue) {
        setTemporaryToken(__assign(__assign({}, temporaryToken), { value: newValue }));
    };
    return (React.createElement(InternalPopover, { ref: popoverRef, className: styles['token-label'], triggerType: "text", header: i18nStrings.editTokenHeader, size: "large", position: "right", dismissAriaLabel: i18nStrings.dismissAriaLabel, __onOpen: function () { return setTemporaryToken(token); }, renderWithPortal: expandToViewport, content: React.createElement("div", { className: styles['token-editor'] },
            React.createElement("div", { className: styles['token-editor-form'] },
                React.createElement(InternalFormField, { label: i18nStrings.propertyText, className: styles['token-editor-field-property'] },
                    React.createElement(PropertyInput, { propertyKey: propertyKey, onChangePropertyKey: onChangePropertyKey, asyncProps: asyncProperties ? asyncProps : null, filteringProperties: filteringProperties, onLoadItems: onLoadItems, customGroupsText: customGroupsText, i18nStrings: i18nStrings, disableFreeTextFiltering: disableFreeTextFiltering })),
                React.createElement(InternalFormField, { label: i18nStrings.operatorText, className: styles['token-editor-field-operator'] },
                    React.createElement(OperatorInput, { propertyKey: propertyKey, operator: operator, onChangeOperator: onChangeOperator, filteringProperties: filteringProperties, i18nStrings: i18nStrings })),
                React.createElement(InternalFormField, { label: i18nStrings.valueText, className: styles['token-editor-field-value'] },
                    React.createElement(ValueInput, { propertyKey: propertyKey, operator: operator, value: value, onChangeValue: onChangeValue, asyncProps: asyncProps, filteringProperties: filteringProperties, filteringOptions: filteringOptions, onLoadItems: onLoadItems, i18nStrings: i18nStrings }))),
            React.createElement("div", { className: styles['token-editor-actions'] },
                React.createElement(InternalButton, { variant: "link", className: styles['token-editor-cancel'], onClick: closePopover }, i18nStrings.cancelActionText),
                React.createElement(InternalButton, { className: styles['token-editor-submit'], onClick: function () {
                        setToken(matchTokenValue(temporaryToken, filteringOptions));
                        closePopover();
                    } }, i18nStrings.applyActionText))) }, triggerComponent));
}
//# sourceMappingURL=token-editor.js.map