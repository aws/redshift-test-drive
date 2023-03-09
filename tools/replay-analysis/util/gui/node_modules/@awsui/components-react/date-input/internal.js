// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign, __rest } from "tslib";
import clsx from 'clsx';
import { getDaysInMonth } from 'date-fns';
import React from 'react';
import { fireNonCancelableEvent } from '../internal/events';
import { displayToIso, isoToDisplay, parseDate } from '../internal/utils/date-time';
import MaskedInput from '../internal/components/masked-input';
import styles from './styles.css.js';
function daysMax(value) {
    // force to first day in month, as new Date('2018-02-30') -> March 2nd 2018
    var baseDate = displayToIso(value).substring(0, 7);
    return getDaysInMonth(parseDate(baseDate));
}
var maskArgs = {
    separator: '/',
    inputSeparators: ['-', '.', ' '],
    segments: [
        { min: 0, max: 9999, "default": 2000, length: 4 },
        { min: 1, max: 12, length: 2 },
        { min: 1, max: daysMax, length: 2 },
    ]
};
var InternalDateInput = React.forwardRef(function (_a, ref) {
    var value = _a.value, onChange = _a.onChange, _b = _a.__internalRootRef, __internalRootRef = _b === void 0 ? null : _b, props = __rest(_a, ["value", "onChange", "__internalRootRef"]);
    return (React.createElement(MaskedInput, __assign({ ref: ref }, props, { value: isoToDisplay(value || ''), onChange: function (event) { return fireNonCancelableEvent(onChange, { value: displayToIso(event.detail.value) }); }, className: clsx(styles.root, props.className), mask: maskArgs, autofix: true, autoComplete: false, disableAutocompleteOnBlur: false, disableBrowserAutocorrect: true, __internalRootRef: __internalRootRef })));
});
export default InternalDateInput;
//# sourceMappingURL=internal.js.map