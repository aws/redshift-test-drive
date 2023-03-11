// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign } from "tslib";
// Finds the longest property the filtering text starts from.
export function matchFilteringProperty(filteringProperties, filteringText) {
    var maxLength = 0;
    var matchedProperty = null;
    for (var _i = 0, filteringProperties_1 = filteringProperties; _i < filteringProperties_1.length; _i++) {
        var property = filteringProperties_1[_i];
        if ((property.propertyLabel.length >= maxLength && startsWith(filteringText, property.propertyLabel)) ||
            (property.propertyLabel.length > maxLength &&
                startsWith(filteringText.toLowerCase(), property.propertyLabel.toLowerCase()))) {
            maxLength = property.propertyLabel.length;
            matchedProperty = property;
        }
    }
    return matchedProperty;
}
// Finds the longest operator the filtering text starts from.
export function matchOperator(allowedOperators, filteringText) {
    filteringText = filteringText.toLowerCase();
    var maxLength = 0;
    var matchedOperator = null;
    for (var _i = 0, allowedOperators_1 = allowedOperators; _i < allowedOperators_1.length; _i++) {
        var operator = allowedOperators_1[_i];
        if (operator.length > maxLength && startsWith(filteringText, operator.toLowerCase())) {
            maxLength = operator.length;
            matchedOperator = operator;
        }
    }
    return matchedOperator;
}
// Finds if the filtering text matches any operator prefix.
export function matchOperatorPrefix(allowedOperators, filteringText) {
    if (filteringText.trim().length === 0) {
        return '';
    }
    for (var _i = 0, allowedOperators_2 = allowedOperators; _i < allowedOperators_2.length; _i++) {
        var operator = allowedOperators_2[_i];
        if (startsWith(operator.toLowerCase(), filteringText.toLowerCase())) {
            return filteringText;
        }
    }
    return null;
}
export function matchTokenValue(token, filteringOptions) {
    var _a, _b;
    var value = token.value.toLowerCase();
    var propertyOptions = filteringOptions.filter(function (option) { return option.propertyKey === token.propertyKey; });
    for (var _i = 0, propertyOptions_1 = propertyOptions; _i < propertyOptions_1.length; _i++) {
        var option = propertyOptions_1[_i];
        var optionText = ((_b = (_a = option.label) !== null && _a !== void 0 ? _a : option.value) !== null && _b !== void 0 ? _b : '').toLowerCase();
        if (optionText === value) {
            return __assign(__assign({}, token), { value: option.value });
        }
    }
    return token;
}
export function trimStart(source) {
    var spacesLength = 0;
    for (var i = 0; i < source.length; i++) {
        if (source[i] === ' ') {
            spacesLength++;
        }
        else {
            break;
        }
    }
    return source.slice(spacesLength);
}
export function trimFirstSpace(source) {
    return source[0] === ' ' ? source.slice(1) : source;
}
function startsWith(source, target) {
    return source.indexOf(target) === 0;
}
//# sourceMappingURL=utils.js.map