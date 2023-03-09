// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign, __rest } from "tslib";
import React, { useEffect, useRef, useState } from 'react';
import { isSameMonth } from 'date-fns';
import styles from './styles.css.js';
import CalendarHeader from './header';
import Grid from './grid';
import { normalizeLocale, normalizeStartOfWeek } from '../internal/utils/locale';
import { formatDate, parseDate } from '../internal/utils/date-time';
import { fireNonCancelableEvent } from '../internal/events/index.js';
import checkControlled from '../internal/hooks/check-controlled/index.js';
import clsx from 'clsx';
import { getBaseProps } from '../internal/base-component';
import { getBaseDate } from './utils/navigation';
import { useDateCache } from '../internal/hooks/use-date-cache/index.js';
import { useUniqueId } from '../internal/hooks/use-unique-id/index.js';
export default function Calendar(_a) {
    var value = _a.value, _b = _a.locale, locale = _b === void 0 ? '' : _b, startOfWeek = _a.startOfWeek, _c = _a.isDateEnabled, isDateEnabled = _c === void 0 ? function () { return true; } : _c, ariaLabel = _a.ariaLabel, ariaLabelledby = _a.ariaLabelledby, ariaDescribedby = _a.ariaDescribedby, todayAriaLabel = _a.todayAriaLabel, nextMonthAriaLabel = _a.nextMonthAriaLabel, previousMonthAriaLabel = _a.previousMonthAriaLabel, onChange = _a.onChange, __internalRootRef = _a.__internalRootRef, rest = __rest(_a, ["value", "locale", "startOfWeek", "isDateEnabled", "ariaLabel", "ariaLabelledby", "ariaDescribedby", "todayAriaLabel", "nextMonthAriaLabel", "previousMonthAriaLabel", "onChange", "__internalRootRef"]);
    checkControlled('Calendar', 'value', value, 'onChange', onChange);
    var baseProps = getBaseProps(rest);
    var normalizedLocale = normalizeLocale('Calendar', locale);
    var normalizedStartOfWeek = normalizeStartOfWeek(startOfWeek, normalizedLocale);
    var gridWrapperRef = useRef(null);
    var _d = useState(null), focusedDate = _d[0], setFocusedDate = _d[1];
    var valueDateCache = useDateCache();
    var focusedDateCache = useDateCache();
    // Set displayed date to value if defined or to current date otherwise.
    var parsedValue = value && value.length >= 4 ? parseDate(value) : null;
    var memoizedValue = parsedValue ? valueDateCache(parsedValue) : null;
    var defaultDisplayedDate = memoizedValue !== null && memoizedValue !== void 0 ? memoizedValue : new Date();
    var _e = useState(defaultDisplayedDate), displayedDate = _e[0], setDisplayedDate = _e[1];
    var headingId = useUniqueId('calendar-heading');
    // Update displayed date if value changes.
    useEffect(function () {
        memoizedValue && setDisplayedDate(function (prev) { return (prev.getTime() !== memoizedValue.getTime() ? memoizedValue : prev); });
    }, [memoizedValue]);
    var selectFocusedDate = function (selected, baseDate) {
        if (selected && isDateEnabled(selected) && isSameMonth(selected, baseDate)) {
            return selected;
        }
        var today = new Date();
        if (isDateEnabled(today) && isSameMonth(today, baseDate)) {
            return today;
        }
        if (isDateEnabled(baseDate)) {
            return baseDate;
        }
        return null;
    };
    var baseDate = getBaseDate(displayedDate, isDateEnabled);
    var focusableDate = focusedDate || selectFocusedDate(memoizedValue, baseDate);
    var onHeaderChangeMonthHandler = function (date) {
        setDisplayedDate(date);
        setFocusedDate(null);
    };
    var onGridChangeMonthHandler = function (newMonth) {
        setDisplayedDate(newMonth);
        setFocusedDate(null);
    };
    var onGridFocusDateHandler = function (date) {
        if (date) {
            setFocusedDate(date ? focusedDateCache(date) : null);
        }
    };
    var onGridSelectDateHandler = function (date) {
        fireNonCancelableEvent(onChange, { value: formatDate(date) });
        setFocusedDate(null);
    };
    var onGridBlur = function (event) {
        var _a;
        var newFocusTargetIsInGrid = event.relatedTarget && ((_a = gridWrapperRef.current) === null || _a === void 0 ? void 0 : _a.contains(event.relatedTarget));
        if (!newFocusTargetIsInGrid) {
            setFocusedDate(null);
        }
    };
    return (React.createElement("div", __assign({ ref: __internalRootRef }, baseProps, { role: "group", "aria-label": ariaLabel, "aria-labelledby": ariaLabelledby, "aria-describedby": ariaDescribedby, className: clsx(styles.root, styles.calendar, baseProps.className) }),
        React.createElement("div", { className: styles['calendar-inner'] },
            React.createElement(CalendarHeader, { baseDate: baseDate, locale: normalizedLocale, onChangeMonth: onHeaderChangeMonthHandler, previousMonthLabel: previousMonthAriaLabel, nextMonthLabel: nextMonthAriaLabel, headingId: headingId }),
            React.createElement("div", { onBlur: onGridBlur, ref: gridWrapperRef },
                React.createElement(Grid, { locale: normalizedLocale, baseDate: baseDate, isDateEnabled: isDateEnabled, focusedDate: focusedDate, focusableDate: focusableDate, onSelectDate: onGridSelectDateHandler, onFocusDate: onGridFocusDateHandler, onChangeMonth: onGridChangeMonthHandler, startOfWeek: normalizedStartOfWeek, todayAriaLabel: todayAriaLabel, selectedDate: memoizedValue, ariaLabelledby: headingId })))));
}
//# sourceMappingURL=internal.js.map