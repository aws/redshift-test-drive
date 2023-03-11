import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useMemo } from 'react';
import styles from './styles.css.js';
import { isSameMonth, isAfter, isBefore, isSameDay, addWeeks, addDays, isLastDayOfMonth, getDaysInMonth, isToday, } from 'date-fns';
import { getCalendarMonth } from 'mnth';
import { getDateLabel, renderDayName } from '../../../calendar/utils/intl';
import clsx from 'clsx';
import { formatDate } from '../../../internal/utils/date-time';
import useFocusVisible from '../../../internal/hooks/focus-visible/index.js';
import ScreenreaderOnly from '../../../internal/components/screenreader-only/index.js';
export function Grid(_a) {
    var baseDate = _a.baseDate, selectedStartDate = _a.selectedStartDate, selectedEndDate = _a.selectedEndDate, rangeStartDate = _a.rangeStartDate, rangeEndDate = _a.rangeEndDate, focusedDate = _a.focusedDate, focusedDateRef = _a.focusedDateRef, onSelectDate = _a.onSelectDate, onGridKeyDownHandler = _a.onGridKeyDownHandler, onFocusedDateChange = _a.onFocusedDateChange, isDateEnabled = _a.isDateEnabled, locale = _a.locale, startOfWeek = _a.startOfWeek, todayAriaLabel = _a.todayAriaLabel, ariaLabelledby = _a.ariaLabelledby, className = _a.className;
    var baseDateTime = baseDate === null || baseDate === void 0 ? void 0 : baseDate.getTime();
    // `baseDateTime` is used as a more stable replacement for baseDate
    var weeks = useMemo(function () { return getCalendarMonth(baseDate, { firstDayOfWeek: startOfWeek }); }, 
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [baseDateTime, startOfWeek]);
    var weekdays = weeks[0].map(function (date) { return date.getDay(); });
    var focusVisible = useFocusVisible();
    return (React.createElement("table", { role: "grid", "aria-labelledby": ariaLabelledby, className: clsx(styles.grid, className) },
        React.createElement("thead", null,
            React.createElement("tr", null, weekdays.map(function (dayIndex) { return (React.createElement("th", { key: dayIndex, scope: "col", className: clsx(styles['grid-cell'], styles['day-header']) },
                React.createElement("span", { "aria-hidden": "true" }, renderDayName(locale, dayIndex, 'short')),
                React.createElement(ScreenreaderOnly, null, renderDayName(locale, dayIndex, 'long')))); }))),
        React.createElement("tbody", { onKeyDown: onGridKeyDownHandler }, weeks.map(function (week, weekIndex) {
            return (React.createElement("tr", { key: weekIndex, className: styles.week }, week.map(function (date, dateIndex) {
                var _a, _b, _c;
                var isStartDate = !!selectedStartDate && isSameDay(date, selectedStartDate);
                var isEndDate = !!selectedEndDate && isSameDay(date, selectedEndDate);
                var isSelected = isStartDate || isEndDate;
                var isRangeStartDate = !!rangeStartDate && isSameDay(date, rangeStartDate);
                var isRangeEndDate = !!rangeEndDate && isSameDay(date, rangeEndDate);
                var isFocused = !!focusedDate && isSameDay(date, focusedDate) && isSameMonth(date, baseDate);
                var dateIsInRange = isStartDate || isEndDate || isInRange(date, rangeStartDate, rangeEndDate);
                var inRangeStartWeek = rangeStartDate && isInRange(date, rangeStartDate, addDays(addWeeks(rangeStartDate, 1), -1));
                var inRangeEndWeek = rangeEndDate && isInRange(date, rangeEndDate, addDays(addWeeks(rangeEndDate, -1), 1));
                var onlyOneSelected = !!rangeStartDate && !!rangeEndDate
                    ? isSameDay(rangeStartDate, rangeEndDate)
                    : !selectedStartDate || !selectedEndDate;
                var isEnabled = !isDateEnabled || isDateEnabled(date);
                var isFocusable = isFocused && isEnabled;
                var baseClasses = (_a = {},
                    _a[styles.day] = true,
                    _a[styles['grid-cell']] = true,
                    _a[styles['in-first-row']] = weekIndex === 0,
                    _a[styles['in-first-column']] = dateIndex === 0,
                    _a);
                if (!isSameMonth(date, baseDate)) {
                    return (React.createElement("td", { key: "".concat(weekIndex, ":").concat(dateIndex), ref: isFocused ? focusedDateRef : undefined, className: clsx(baseClasses, (_b = {},
                            _b[styles['in-previous-month']] = isBefore(date, baseDate),
                            _b[styles['last-day-of-month']] = isLastDayOfMonth(date),
                            _b[styles['in-next-month']] = isAfter(date, baseDate),
                            _b)) }));
                }
                var handlers = {};
                if (isEnabled) {
                    handlers.onClick = function () { return onSelectDate(date); };
                    handlers.onFocus = function () { return onFocusedDateChange(date); };
                }
                // Can't be focused.
                var tabIndex = undefined;
                if (isFocusable && isEnabled) {
                    // Next focus target.
                    tabIndex = 0;
                }
                else if (isEnabled) {
                    // Can be focused programmatically.
                    tabIndex = -1;
                }
                // Screen-reader announcement for the focused day.
                var dayAnnouncement = getDateLabel(locale, date, 'short');
                if (isToday(date)) {
                    dayAnnouncement += '. ' + todayAriaLabel;
                }
                return (React.createElement("td", __assign({ ref: isFocused ? focusedDateRef : undefined, key: "".concat(weekIndex, ":").concat(dateIndex), className: clsx(baseClasses, (_c = {},
                        _c[styles['in-current-month']] = isSameMonth(date, baseDate),
                        _c[styles.enabled] = isEnabled,
                        _c[styles.selected] = isSelected,
                        _c[styles['start-date']] = isStartDate,
                        _c[styles['end-date']] = isEndDate,
                        _c[styles['range-start-date']] = isRangeStartDate,
                        _c[styles['range-end-date']] = isRangeEndDate,
                        _c[styles['no-range']] = isSelected && onlyOneSelected,
                        _c[styles['in-range']] = dateIsInRange,
                        _c[styles['in-range-border-top']] = !!inRangeStartWeek || date.getDate() <= 7,
                        _c[styles['in-range-border-bottom']] = !!inRangeEndWeek || date.getDate() > getDaysInMonth(date) - 7,
                        _c[styles['in-range-border-left']] = dateIndex === 0 || date.getDate() === 1 || isRangeStartDate,
                        _c[styles['in-range-border-right']] = dateIndex === week.length - 1 || isLastDayOfMonth(date) || isRangeEndDate,
                        _c[styles.today] = isToday(date),
                        _c)), "aria-selected": isEnabled ? isSelected || dateIsInRange : undefined, "aria-current": isToday(date) ? 'date' : undefined, "data-date": formatDate(date), "aria-disabled": !isEnabled, tabIndex: tabIndex }, handlers, focusVisible),
                    React.createElement("span", { className: styles['day-inner'], "aria-hidden": "true" }, date.getDate()),
                    React.createElement(ScreenreaderOnly, null, dayAnnouncement)));
            })));
        }))));
}
function isInRange(date, dateOne, dateTwo) {
    if (!dateOne || !dateTwo || isSameDay(dateOne, dateTwo)) {
        return false;
    }
    var inRange = (isAfter(date, dateOne) && isBefore(date, dateTwo)) || (isAfter(date, dateTwo) && isBefore(date, dateOne));
    return inRange || isSameDay(date, dateOne) || isSameDay(date, dateTwo);
}
//# sourceMappingURL=grid.js.map