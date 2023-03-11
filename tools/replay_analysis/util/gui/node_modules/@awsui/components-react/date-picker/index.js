import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useCallback, useRef, useState } from 'react';
import styles from './styles.css.js';
import InternalCalendar from '../calendar/internal';
import { normalizeLocale } from '../internal/utils/locale';
import { getDateLabel, renderMonthAndYear } from '../calendar/utils/intl';
import { KeyCode } from '../internal/keycode';
import { fireNonCancelableEvent } from '../internal/events';
import Dropdown from '../internal/components/dropdown';
import InternalDateInput from '../date-input/internal';
import { getBaseProps } from '../internal/base-component';
import { applyDisplayName } from '../internal/utils/apply-display-name.js';
import checkControlled from '../internal/hooks/check-controlled';
import { useFocusTracker } from '../internal/hooks/use-focus-tracker.js';
import useForwardFocus from '../internal/hooks/forward-focus';
import { InternalButton } from '../button/internal';
import useBaseComponent from '../internal/hooks/use-base-component';
import { useUniqueId } from '../internal/hooks/use-unique-id';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import FocusLock from '../internal/components/focus-lock';
import useFocusVisible from '../internal/hooks/focus-visible/index.js';
import { parseDate } from '../internal/utils/date-time';
import LiveRegion from '../internal/components/live-region';
import { useFormFieldContext } from '../contexts/form-field.js';
var DatePicker = React.forwardRef(function (_a, ref) {
    var _b = _a.locale, locale = _b === void 0 ? '' : _b, startOfWeek = _a.startOfWeek, isDateEnabled = _a.isDateEnabled, nextMonthAriaLabel = _a.nextMonthAriaLabel, previousMonthAriaLabel = _a.previousMonthAriaLabel, todayAriaLabel = _a.todayAriaLabel, _c = _a.placeholder, placeholder = _c === void 0 ? '' : _c, _d = _a.value, value = _d === void 0 ? '' : _d, _e = _a.readOnly, readOnly = _e === void 0 ? false : _e, _f = _a.disabled, disabled = _f === void 0 ? false : _f, onBlur = _a.onBlur, _g = _a.autoFocus, autoFocus = _g === void 0 ? false : _g, onChange = _a.onChange, onFocus = _a.onFocus, name = _a.name, ariaLabel = _a.ariaLabel, ariaRequired = _a.ariaRequired, controlId = _a.controlId, invalid = _a.invalid, openCalendarAriaLabel = _a.openCalendarAriaLabel, expandToViewport = _a.expandToViewport, rest = __rest(_a, ["locale", "startOfWeek", "isDateEnabled", "nextMonthAriaLabel", "previousMonthAriaLabel", "todayAriaLabel", "placeholder", "value", "readOnly", "disabled", "onBlur", "autoFocus", "onChange", "onFocus", "name", "ariaLabel", "ariaRequired", "controlId", "invalid", "openCalendarAriaLabel", "expandToViewport"]);
    var __internalRootRef = useBaseComponent('DatePicker').__internalRootRef;
    checkControlled('DatePicker', 'value', value, 'onChange', onChange);
    var baseProps = getBaseProps(rest);
    var _h = useState(false), isDropDownOpen = _h[0], setIsDropDownOpen = _h[1];
    var normalizedLocale = normalizeLocale('DatePicker', locale);
    var focusVisible = useFocusVisible();
    var _j = useFormFieldContext(rest), ariaLabelledby = _j.ariaLabelledby, ariaDescribedby = _j.ariaDescribedby;
    var internalInputRef = useRef(null);
    var buttonRef = useRef(null);
    useForwardFocus(ref, internalInputRef);
    var rootRef = useRef(null);
    var dropdownId = useUniqueId('calender');
    var calendarDescriptionId = useUniqueId('calendar-description-');
    var mergedRef = useMergeRefs(rootRef, __internalRootRef);
    useFocusTracker({ rootRef: rootRef, onBlur: onBlur, onFocus: onFocus, viewportId: expandToViewport ? dropdownId : '' });
    var onDropdownCloseHandler = useCallback(function () { return setIsDropDownOpen(false); }, [setIsDropDownOpen]);
    var onButtonClickHandler = function () {
        if (!isDropDownOpen) {
            setIsDropDownOpen(true);
        }
    };
    var onWrapperKeyDownHandler = function (event) {
        var _a;
        if (event.keyCode === KeyCode.escape && isDropDownOpen) {
            (_a = buttonRef.current) === null || _a === void 0 ? void 0 : _a.focus();
            setIsDropDownOpen(false);
        }
    };
    var onInputChangeHandler = function (event) {
        fireNonCancelableEvent(onChange, { value: event.detail.value });
    };
    var onInputBlurHandler = function () {
        if (!isDropDownOpen) {
            setIsDropDownOpen(false);
        }
    };
    // Set displayed date to value if defined or to current date otherwise.
    var parsedValue = value && value.length >= 4 ? parseDate(value) : null;
    var baseDate = parsedValue || new Date();
    var trigger = (React.createElement("div", { className: styles['date-picker-trigger'] },
        React.createElement("div", { className: styles['date-picker-input'] },
            React.createElement(InternalDateInput, { name: name, invalid: invalid, controlId: controlId, ariaLabelledby: ariaLabelledby, ariaDescribedby: ariaDescribedby, ariaLabel: ariaLabel, ariaRequired: ariaRequired, value: value, disabled: disabled, readOnly: readOnly, onChange: onInputChangeHandler, onBlur: onInputBlurHandler, placeholder: placeholder, ref: internalInputRef, autoFocus: autoFocus, onFocus: onDropdownCloseHandler })),
        React.createElement("div", null,
            React.createElement(InternalButton, { iconName: "calendar", className: styles['open-calendar-button'], onClick: onButtonClickHandler, ref: buttonRef, ariaLabel: openCalendarAriaLabel &&
                    openCalendarAriaLabel(value.length === 10 ? getDateLabel(normalizedLocale, parsedValue) : null), disabled: disabled || readOnly, formAction: "none" }))));
    baseProps.className = clsx(baseProps.className, styles.root, styles['date-picker-container']);
    var handleMouseDown = function (event) {
        // prevent currently focused element from losing it
        event.preventDefault();
    };
    return (React.createElement("div", __assign({}, baseProps, { ref: mergedRef, onKeyDown: !disabled && !readOnly ? onWrapperKeyDownHandler : undefined }), disabled || readOnly ? (trigger) : (React.createElement(Dropdown, { stretchWidth: true, stretchHeight: true, open: isDropDownOpen, onDropdownClose: onDropdownCloseHandler, onMouseDown: handleMouseDown, trigger: trigger, expandToViewport: expandToViewport, scrollable: false, dropdownId: dropdownId }, isDropDownOpen && (React.createElement(FocusLock, { className: styles['focus-lock'], autoFocus: true },
        React.createElement("div", __assign({}, focusVisible, { tabIndex: 0, className: styles.calendar, role: "dialog", "aria-modal": "true" }),
            React.createElement(InternalCalendar, { value: value, onChange: function (e) {
                    var _a;
                    fireNonCancelableEvent(onChange, e.detail);
                    (_a = buttonRef === null || buttonRef === void 0 ? void 0 : buttonRef.current) === null || _a === void 0 ? void 0 : _a.focus();
                    setIsDropDownOpen(false);
                }, locale: normalizedLocale, startOfWeek: startOfWeek, ariaDescribedby: calendarDescriptionId, ariaLabel: ariaLabel, ariaLabelledby: ariaLabelledby, isDateEnabled: isDateEnabled, todayAriaLabel: todayAriaLabel, nextMonthAriaLabel: nextMonthAriaLabel, previousMonthAriaLabel: previousMonthAriaLabel }),
            React.createElement(LiveRegion, { id: calendarDescriptionId }, renderMonthAndYear(normalizedLocale, baseDate)))))))));
});
applyDisplayName(DatePicker, 'DatePicker');
export default DatePicker;
//# sourceMappingURL=index.js.map