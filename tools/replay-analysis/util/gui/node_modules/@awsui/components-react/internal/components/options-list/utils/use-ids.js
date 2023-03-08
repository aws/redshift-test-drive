// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
export var getOptionId = function (menuId, index) {
    if (index < 0) {
        return undefined;
    }
    return "".concat(menuId, "-option-").concat(index);
};
//# sourceMappingURL=use-ids.js.map