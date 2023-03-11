// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign } from "tslib";
export function filterOptions(options, searchText) {
    if (searchText === void 0) { searchText = ''; }
    if (!searchText) {
        return options;
    }
    var filtered = [];
    for (var _i = 0, options_1 = options; _i < options_1.length; _i++) {
        var option = options_1[_i];
        if (isGroup(option)) {
            var childOptions = filterOptions(option.options, searchText);
            if (childOptions.length > 0) {
                filtered.push(__assign(__assign({}, option), { options: childOptions }));
            }
        }
        else if (matchSingleOption(option, searchText)) {
            filtered.push(option);
        }
    }
    return filtered;
}
function isGroup(optionOrGroup) {
    return 'options' in optionOrGroup;
}
function matchSingleOption(option, searchText) {
    var _a, _b;
    searchText = searchText.toLowerCase();
    var label = ((_a = option.label) !== null && _a !== void 0 ? _a : '').toLowerCase();
    var labelPrefix = (_b = option.__labelPrefix) !== null && _b !== void 0 ? _b : '';
    var value = (option.value ? option.value.slice(labelPrefix.length) : '').toLowerCase();
    return label.indexOf(searchText) !== -1 || value.indexOf(searchText) !== -1;
}
//# sourceMappingURL=filter-options.js.map