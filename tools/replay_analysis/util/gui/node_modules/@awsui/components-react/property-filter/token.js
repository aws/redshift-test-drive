// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import styles from './styles.css.js';
import { TokenEditor } from './token-editor';
import { getExtendedOperator, getPropertyByKey } from './controller';
import FilteringToken from '../internal/components/filtering-token';
export var TokenButton = function (_a) {
    var _b;
    var token = _a.token, _c = _a.operation, operation = _c === void 0 ? 'and' : _c, first = _a.first, removeToken = _a.removeToken, setToken = _a.setToken, setOperation = _a.setOperation, filteringOptions = _a.filteringOptions, filteringProperties = _a.filteringProperties, asyncProps = _a.asyncProps, onLoadItems = _a.onLoadItems, i18nStrings = _a.i18nStrings, asyncProperties = _a.asyncProperties, hideOperations = _a.hideOperations, customGroupsText = _a.customGroupsText, disabled = _a.disabled, disableFreeTextFiltering = _a.disableFreeTextFiltering, expandToViewport = _a.expandToViewport;
    var valueFormatter = token.propertyKey && ((_b = getExtendedOperator(filteringProperties, token.propertyKey, token.operator)) === null || _b === void 0 ? void 0 : _b.format);
    var property = token.propertyKey && getPropertyByKey(filteringProperties, token.propertyKey);
    var propertyLabel = property && property.propertyLabel;
    var tokenValue = valueFormatter ? valueFormatter(token.value) : token.value;
    return (React.createElement(FilteringToken, { showOperation: !first && !hideOperations, operation: operation, andText: i18nStrings.operationAndText, orText: i18nStrings.operationOrText, dismissAriaLabel: i18nStrings.removeTokenButtonAriaLabel(token), operatorAriaLabel: i18nStrings.tokenOperatorAriaLabel, onChange: setOperation, onDismiss: removeToken, disabled: disabled },
        React.createElement(TokenEditor, { setToken: setToken, triggerComponent: React.createElement("span", { className: styles['token-trigger'] },
                React.createElement(TokenTrigger, { property: propertyLabel, operator: token.operator, value: tokenValue })), filteringOptions: filteringOptions, filteringProperties: filteringProperties, token: token, asyncProps: asyncProps, onLoadItems: onLoadItems, i18nStrings: i18nStrings, asyncProperties: asyncProperties, customGroupsText: customGroupsText, disableFreeTextFiltering: disableFreeTextFiltering, expandToViewport: expandToViewport })));
};
var TokenTrigger = function (_a) {
    var property = _a.property, operator = _a.operator, value = _a.value;
    if (property) {
        property += ' ';
    }
    var freeTextContainsToken = operator === ':' && !property;
    var operatorText = freeTextContainsToken ? '' : operator + ' ';
    return (React.createElement(React.Fragment, null,
        property,
        React.createElement("span", { className: styles['token-operator'] }, operatorText),
        value));
};
//# sourceMappingURL=token.js.map