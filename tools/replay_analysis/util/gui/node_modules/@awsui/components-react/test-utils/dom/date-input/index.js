"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        if (typeof b !== "function" && b !== null)
            throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
var base_input_1 = require("../input/base-input");
var styles_selectors_js_1 = require("../../../date-input/styles.selectors.js");
var DateInputWrapper = /** @class */ (function (_super) {
    __extends(DateInputWrapper, _super);
    function DateInputWrapper() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    DateInputWrapper.rootSelector = styles_selectors_js_1.default.root;
    return DateInputWrapper;
}(base_input_1.default));
exports.default = DateInputWrapper;
//# sourceMappingURL=index.js.map