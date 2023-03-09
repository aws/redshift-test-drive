import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useMemo, useRef } from 'react';
import styles from '../styles.css.js';
import { KeyCode } from '../../internal/keycode';
import { isSameDay, isSameMonth } from 'date-fns';
import { getCalendarMonth } from 'mnth';
import { getDateLabel, renderDayName } from '../utils/intl';
import useFocusVisible from '../../internal/hooks/focus-visible/index.js';
import clsx from 'clsx';
import { useEffectOnUpdate } from '../../internal/hooks/use-effect-on-update.js';
import ScreenreaderOnly from '../../internal/components/screenreader-only/index.js';
import { moveNextDay, movePrevDay, moveNextWeek, movePrevWeek } from '../utils/navigation';
export default function Grid(_a) {
    var locale = _a.locale, baseDate = _a.baseDate, isDateEnabled = _a.isDateEnabled, focusedDate = _a.focusedDate, focusableDate = _a.focusableDate, onSelectDate = _a.onSelectDate, onFocusDate = _a.onFocusDate, onChangeMonth = _a.onChangeMonth, startOfWeek = _a.startOfWeek, todayAriaLabel = _a.todayAriaLabel, selectedDate = _a.selectedDate, ariaLabelledby = _a.ariaLabelledby;
    var focusedDateRef = useRef(null);
    var onGridKeyDownHandler = function (event) {
        var updatedFocusDate;
        if (focusableDate === null) {
            return;
        }
        switch (event.keyCode) {
            case KeyCode.space:
            case KeyCode.enter:
                event.preventDefault();
                if (focusableDate) {
                    onFocusDate(null);
                    onSelectDate(focusableDate);
                }
                return;
            case KeyCode.right:
                event.preventDefault();
                updatedFocusDate = moveNextDay(focusableDate, isDateEnabled);
                break;
            case KeyCode.left:
                event.preventDefault();
                updatedFocusDate = movePrevDay(focusableDate, isDateEnabled);
                break;
            case KeyCode.up:
                event.preventDefault();
                updatedFocusDate = movePrevWeek(focusableDate, isDateEnabled);
                break;
            case KeyCode.down:
                event.preventDefault();
                updatedFocusDate = moveNextWeek(focusableDate, isDateEnabled);
                break;
            default:
                return;
        }
        if (!isSameMonth(updatedFocusDate, baseDate)) {
            onChangeMonth(updatedFocusDate);
        }
        onFocusDate(updatedFocusDate);
    };
    // The focused date changes as a feedback to keyboard navigation in the grid.
    // Once changed, the corresponding day button needs to receive the actual focus.
    useEffectOnUpdate(function () {
        if (focusedDate && focusedDateRef.current) {
            focusedDateRef.current.focus();
        }
    }, [focusedDate]);
    var weeks = useMemo(function () { return getCalendarMonth(baseDate, { firstDayOfWeek: startOfWeek }); }, [baseDate, startOfWeek]);
    var weekdays = weeks[0].map(function (date) { return date.getDay(); });
    var focusVisible = useFocusVisible();
    return (React.createElement("table", { role: "grid", className: styles['calendar-grid'], "aria-labelledby": ariaLabelledby },
        React.createElement("thead", null,
            React.createElement("tr", null, weekdays.map(function (dayIndex) { return (React.createElement("th", { key: dayIndex, scope: "col", className: clsx(styles['calendar-grid-cell'], styles['calendar-day-header']) },
                React.createElement("span", { "aria-hidden": "true" }, renderDayName(locale, dayIndex, 'short')),
                React.createElement(ScreenreaderOnly, null, renderDayName(locale, dayIndex, 'long')))); }))),
        React.createElement("tbody", { onKeyDown: onGridKeyDownHandler }, weeks.map(function (week, weekIndex) { return (React.createElement("tr", { key: weekIndex, className: styles['calendar-week'] }, week.map(function (date, dateIndex) {
            var _a;
            var isFocusable = !!focusableDate && isSameDay(date, focusableDate);
            var isSelected = !!selectedDate && isSameDay(date, selectedDate);
            var isEnabled = !isDateEnabled || isDateEnabled(date);
            var isDateOnSameDay = isSameDay(date, new Date());
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
            if (isDateOnSameDay) {
                dayAnnouncement += '. ' + todayAriaLabel;
            }
            return (React.createElement("td", __assign({ key: "".concat(weekIndex, ":").concat(dateIndex), ref: tabIndex === 0 ? focusedDateRef : undefined, tabIndex: tabIndex, "aria-current": isDateOnSameDay ? 'date' : undefined, "aria-selected": isEnabled ? isSelected : undefined, "aria-disabled": !isEnabled, 
                // Do not attach click event when the date is disabled, otherwise VO+safari announces clickable
                onClick: isEnabled ? function () { return onSelectDate(date); } : undefined, className: clsx(styles['calendar-grid-cell'], styles['calendar-day'], (_a = {},
                    _a[styles['calendar-day-current-month']] = isSameMonth(date, baseDate),
                    _a[styles['calendar-day-enabled']] = isEnabled,
                    _a[styles['calendar-day-selected']] = isSelected,
                    _a[styles['calendar-day-today']] = isDateOnSameDay,
                    _a)) }, focusVisible),
                React.createElement("span", { className: styles['day-inner'], "aria-hidden": "true" }, date.getDate()),
                React.createElement(ScreenreaderOnly, null, dayAnnouncement)));
        }))); }))));
}
//# sourceMappingURL=index.js.map