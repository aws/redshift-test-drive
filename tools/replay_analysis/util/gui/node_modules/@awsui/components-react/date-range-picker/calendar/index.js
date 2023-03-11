// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign } from "tslib";
import React, { useState } from 'react';
import { addMonths, endOfDay, isAfter, isBefore, isSameMonth, startOfDay, startOfMonth } from 'date-fns';
import styles from '../styles.css.js';
import SpaceBetween from '../../space-between/internal';
import CalendarHeader from './header';
import { Grids } from './grids';
import clsx from 'clsx';
import { useUniqueId } from '../../internal/hooks/use-unique-id';
import { getDateLabel, renderTimeLabel } from '../../calendar/utils/intl';
import LiveRegion from '../../internal/components/live-region';
import { normalizeLocale, normalizeStartOfWeek } from '../../internal/utils/locale';
import { parseDate, splitDateTime, formatDateTime } from '../../internal/utils/date-time';
import { getBaseDate } from '../../calendar/utils/navigation';
import { useMobile } from '../../internal/hooks/use-mobile/index.js';
import RangeInputs from './range-inputs.js';
import { findDateToFocus, findMonthToDisplay } from './utils';
export default function DateRangePickerCalendar(_a) {
    var _b, _c;
    var value = _a.value, setValue = _a.setValue, _d = _a.locale, locale = _d === void 0 ? '' : _d, startOfWeek = _a.startOfWeek, _e = _a.isDateEnabled, isDateEnabled = _e === void 0 ? function () { return true; } : _e, i18nStrings = _a.i18nStrings, _f = _a.dateOnly, dateOnly = _f === void 0 ? false : _f, _g = _a.timeInputFormat, timeInputFormat = _g === void 0 ? 'hh:mm:ss' : _g, customAbsoluteRangeControl = _a.customAbsoluteRangeControl;
    var isSingleGrid = useMobile();
    var normalizedLocale = normalizeLocale('DateRangePicker', locale);
    var normalizedStartOfWeek = normalizeStartOfWeek(startOfWeek, normalizedLocale);
    var _h = useState(''), announcement = _h[0], setAnnouncement = _h[1];
    var _j = useState(function () { return findMonthToDisplay(value, isSingleGrid); }), currentMonth = _j[0], setCurrentMonth = _j[1];
    var _k = useState(function () {
        if (value.start.date) {
            var startDate = parseDate(value.start.date);
            if (isSameMonth(startDate, currentMonth)) {
                return startDate;
            }
            if (!isSingleGrid && isSameMonth(startDate, addMonths(currentMonth, -1))) {
                return startDate;
            }
        }
        return findDateToFocus(parseDate(value.start.date), currentMonth, isDateEnabled);
    }), focusedDate = _k[0], setFocusedDate = _k[1];
    var updateCurrentMonth = function (startDate) {
        if (startDate.length >= 8) {
            var newCurrentMonth = startOfMonth(parseDate(startDate));
            setCurrentMonth(isSingleGrid ? newCurrentMonth : addMonths(newCurrentMonth, 1));
        }
    };
    // recommended to include the start/end time announced with the selection
    // because the user is not aware of the fact that a start/end time is also set as soon as they select a date
    var announceStart = function (startDate) {
        return (i18nStrings.startDateLabel +
            ', ' +
            getDateLabel(normalizedLocale, startDate) +
            ', ' +
            i18nStrings.startTimeLabel +
            ', ' +
            renderTimeLabel(normalizedLocale, startDate, timeInputFormat) +
            '. ');
    };
    var announceEnd = function (endDate) {
        return (i18nStrings.endDateLabel +
            ', ' +
            getDateLabel(normalizedLocale, endDate) +
            ', ' +
            i18nStrings.endTimeLabel +
            ', ' +
            renderTimeLabel(normalizedLocale, endDate, timeInputFormat) +
            '. ');
    };
    var announceRange = function (startDate, endDate) {
        if (!i18nStrings.renderSelectedAbsoluteRangeAriaLive) {
            return "".concat(getDateLabel(normalizedLocale, startDate), " \u2013 ").concat(getDateLabel(normalizedLocale, endDate));
        }
        return i18nStrings.renderSelectedAbsoluteRangeAriaLive(getDateLabel(normalizedLocale, startDate), getDateLabel(normalizedLocale, endDate));
    };
    var onSelectDateHandler = function (selectedDate) {
        var start = value.start, end = value.end;
        var newStart = undefined;
        var newEnd = undefined;
        var announcement = '';
        // If both fields are empty, we set the start date
        if (!start.date && !end.date) {
            newStart = startOfDay(selectedDate);
            announcement = announceStart(newStart);
        }
        // If both fields are set, we start new
        else if (start.date && end.date) {
            newStart = startOfDay(selectedDate);
            newEnd = null;
            announcement = announceStart(newStart);
        }
        // If only the END date is empty, we fill it (and swap dates if needed)
        else if (start.date && !end.date) {
            var parsedStartDate = parseDate(start.date);
            if (isBefore(selectedDate, parsedStartDate)) {
                // The user has selected the range backwards, so we swap start and end
                newStart = startOfDay(selectedDate);
                newEnd = endOfDay(parsedStartDate);
                announcement = announceStart(newStart) + announceRange(newStart, newEnd);
            }
            else {
                newEnd = endOfDay(selectedDate);
                announcement = announceEnd(newEnd) + announceRange(parsedStartDate, newEnd);
            }
        }
        // If only the START date is empty, we fill it (and swap dates if needed)
        else if (!start.date && end.date) {
            var existingEndDate = parseDate(end.date);
            if (isAfter(selectedDate, existingEndDate)) {
                // The user has selected the range backwards, so we swap start and end
                newStart = startOfDay(existingEndDate);
                newEnd = endOfDay(selectedDate);
                announcement = announceEnd(newEnd) + announceRange(newStart, newEnd);
            }
            else {
                newStart = startOfDay(selectedDate);
                announcement = announceStart(newStart) + announceRange(newStart, existingEndDate);
            }
        }
        var formatValue = function (date, previous) {
            if (date === null) {
                // explicitly reset to empty
                return { date: '', time: '' };
            }
            else if (date === undefined) {
                // keep old value
                return previous;
            }
            return splitDateTime(formatDateTime(date));
        };
        setValue({
            start: formatValue(newStart, value.start),
            end: formatValue(newEnd, value.end)
        });
        setAnnouncement(announcement);
    };
    var onHeaderChangeMonthHandler = function (newCurrentMonth) {
        setCurrentMonth(newCurrentMonth);
        var newBaseDateMonth = isSingleGrid ? newCurrentMonth : addMonths(newCurrentMonth, -1);
        var newBaseDate = getBaseDate(newBaseDateMonth, isDateEnabled);
        setFocusedDate(newBaseDate);
    };
    var onChangeStartDate = function (value) {
        setValue(function (oldValue) { return (__assign(__assign({}, oldValue), { start: __assign(__assign({}, oldValue.start), { date: value }) })); });
        updateCurrentMonth(value);
    };
    var interceptedSetValue = function (newValue) {
        setValue(function (oldValue) {
            var updated = typeof newValue === 'function' ? newValue(oldValue) : newValue;
            updateCurrentMonth(updated.start.date);
            return updated;
        });
    };
    var headingIdPrefix = useUniqueId('date-range-picker-calendar-heading');
    return (React.createElement(React.Fragment, null,
        React.createElement("div", { className: clsx(styles['calendar-container'], (_b = {},
                _b[styles['one-grid']] = isSingleGrid,
                _b)) },
            React.createElement(SpaceBetween, { size: "s" },
                React.createElement("div", { className: clsx(styles.calendar, (_c = {},
                        _c[styles['one-grid']] = isSingleGrid,
                        _c)) },
                    React.createElement(CalendarHeader, { baseDate: currentMonth, locale: normalizedLocale, onChangeMonth: onHeaderChangeMonthHandler, previousMonthLabel: i18nStrings.previousMonthAriaLabel, nextMonthLabel: i18nStrings.nextMonthAriaLabel, isSingleGrid: isSingleGrid, headingIdPrefix: headingIdPrefix }),
                    React.createElement(Grids, { isSingleGrid: isSingleGrid, locale: normalizedLocale, baseDate: currentMonth, focusedDate: focusedDate, onFocusedDateChange: setFocusedDate, isDateEnabled: isDateEnabled, onSelectDate: onSelectDateHandler, onChangeMonth: setCurrentMonth, startOfWeek: normalizedStartOfWeek, todayAriaLabel: i18nStrings.todayAriaLabel, selectedStartDate: parseDate(value.start.date, true), selectedEndDate: parseDate(value.end.date, true), headingIdPrefix: headingIdPrefix })),
                React.createElement(RangeInputs, { startDate: value.start.date, onChangeStartDate: onChangeStartDate, startTime: value.start.time, onChangeStartTime: function (value) {
                        return setValue(function (oldValue) { return (__assign(__assign({}, oldValue), { start: __assign(__assign({}, oldValue.start), { time: value }) })); });
                    }, endDate: value.end.date, onChangeEndDate: function (value) { return setValue(function (oldValue) { return (__assign(__assign({}, oldValue), { end: __assign(__assign({}, oldValue.end), { date: value }) })); }); }, endTime: value.end.time, onChangeEndTime: function (value) { return setValue(function (oldValue) { return (__assign(__assign({}, oldValue), { end: __assign(__assign({}, oldValue.end), { time: value }) })); }); }, i18nStrings: i18nStrings, dateOnly: dateOnly, timeInputFormat: timeInputFormat }),
                customAbsoluteRangeControl && React.createElement("div", null, customAbsoluteRangeControl(value, interceptedSetValue)))),
        React.createElement(LiveRegion, { className: styles['calendar-aria-live'] }, announcement)));
}
//# sourceMappingURL=index.js.map