// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
export function joinDateTime(dateString, timeString) {
    return "".concat(dateString, "T").concat(timeString);
}
export function splitDateTime(dateStr) {
    var _a = dateStr.split('T'), _b = _a[0], date = _b === void 0 ? '' : _b, _c = _a[1], time = _c === void 0 ? '' : _c;
    return { date: date, time: time };
}
//# sourceMappingURL=join-date-time.js.map