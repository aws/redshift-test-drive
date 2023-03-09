// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign } from "tslib";
import React, { useEffect, useRef, useState } from 'react';
import Calendar from './calendar';
import { InternalButton } from '../button/internal';
import FocusLock from '../internal/components/focus-lock';
import InternalBox from '../box/internal';
import SpaceBetween from '../space-between/index.js';
import styles from './styles.css.js';
import RelativeRangePicker from './relative-range';
import ModeSwitcher from './mode-switcher';
import clsx from 'clsx';
import InternalAlert from '../alert/internal';
import LiveRegion from '../internal/components/live-region';
import useFocusVisible from '../internal/hooks/focus-visible';
import { getDefaultMode, joinAbsoluteValue, splitAbsoluteValue } from './utils';
export var VALID_RANGE = { valid: true };
export function DateRangePickerDropdown(_a) {
    var _b, _c;
    var _d = _a.locale, locale = _d === void 0 ? '' : _d, startOfWeek = _a.startOfWeek, isDateEnabled = _a.isDateEnabled, isValidRange = _a.isValidRange, value = _a.value, clearValue = _a.onClear, applyValue = _a.onApply, onDropdownClose = _a.onDropdownClose, relativeOptions = _a.relativeOptions, showClearButton = _a.showClearButton, isSingleGrid = _a.isSingleGrid, i18nStrings = _a.i18nStrings, dateOnly = _a.dateOnly, timeInputFormat = _a.timeInputFormat, rangeSelectorMode = _a.rangeSelectorMode, ariaLabelledby = _a.ariaLabelledby, ariaDescribedby = _a.ariaDescribedby, customAbsoluteRangeControl = _a.customAbsoluteRangeControl;
    var _e = useState(getDefaultMode(value, relativeOptions, rangeSelectorMode)), rangeSelectionMode = _e[0], setRangeSelectionMode = _e[1];
    var _f = useState(function () {
        return splitAbsoluteValue((value === null || value === void 0 ? void 0 : value.type) === 'absolute' ? value : null);
    }), selectedAbsoluteRange = _f[0], setSelectedAbsoluteRange = _f[1];
    var _g = useState((value === null || value === void 0 ? void 0 : value.type) === 'relative' ? value : null), selectedRelativeRange = _g[0], setSelectedRelativeRange = _g[1];
    var focusVisible = useFocusVisible();
    var scrollableContainerRef = useRef(null);
    var applyButtonRef = useRef(null);
    var _h = useState(false), applyClicked = _h[0], setApplyClicked = _h[1];
    var _j = useState(VALID_RANGE), validationResult = _j[0], setValidationResult = _j[1];
    var closeDropdown = function () {
        setApplyClicked(false);
        onDropdownClose();
    };
    var onClear = function () {
        closeDropdown();
        clearValue();
    };
    var onApply = function () {
        var newValue = rangeSelectionMode === 'relative' ? selectedRelativeRange : joinAbsoluteValue(selectedAbsoluteRange);
        var newValidationResult = applyValue(newValue);
        if (newValidationResult.valid === false) {
            setApplyClicked(true);
            setValidationResult(newValidationResult);
        }
        else {
            setApplyClicked(false);
            closeDropdown();
        }
    };
    useEffect(function () {
        if (applyClicked) {
            var visibleRange = rangeSelectionMode === 'relative' ? selectedRelativeRange : joinAbsoluteValue(selectedAbsoluteRange);
            var newValidationResult = isValidRange(visibleRange);
            setValidationResult(newValidationResult || VALID_RANGE);
        }
    }, [
        applyClicked,
        isValidRange,
        rangeSelectionMode,
        selectedRelativeRange,
        selectedAbsoluteRange,
        setValidationResult,
    ]);
    useEffect(function () { var _a; return (_a = scrollableContainerRef.current) === null || _a === void 0 ? void 0 : _a.focus(); }, [scrollableContainerRef]);
    return (React.createElement(React.Fragment, null,
        React.createElement(FocusLock, { className: styles['focus-lock'], autoFocus: true },
            React.createElement("div", __assign({}, focusVisible, { ref: scrollableContainerRef, className: styles.dropdown, tabIndex: 0, role: "dialog", "aria-modal": "true", "aria-label": i18nStrings.ariaLabel, "aria-labelledby": ariaLabelledby !== null && ariaLabelledby !== void 0 ? ariaLabelledby : i18nStrings.ariaLabelledby, "aria-describedby": ariaDescribedby !== null && ariaDescribedby !== void 0 ? ariaDescribedby : i18nStrings.ariaDescribedby }),
                React.createElement("div", { className: clsx(styles['dropdown-content'], (_b = {},
                        _b[styles['one-grid']] = isSingleGrid,
                        _b)) },
                    React.createElement(SpaceBetween, { size: "l" },
                        React.createElement(InternalBox, { padding: { top: 'm', horizontal: 'l' } },
                            React.createElement(SpaceBetween, { direction: "vertical", size: "s" },
                                rangeSelectorMode === 'default' && (React.createElement(ModeSwitcher, { mode: rangeSelectionMode, onChange: function (mode) {
                                        setRangeSelectionMode(mode);
                                        setApplyClicked(false);
                                        setValidationResult(VALID_RANGE);
                                    }, i18nStrings: i18nStrings })),
                                rangeSelectionMode === 'absolute' && (React.createElement(Calendar, { value: selectedAbsoluteRange, setValue: setSelectedAbsoluteRange, locale: locale, startOfWeek: startOfWeek, isDateEnabled: isDateEnabled, i18nStrings: i18nStrings, dateOnly: dateOnly, timeInputFormat: timeInputFormat, customAbsoluteRangeControl: customAbsoluteRangeControl })),
                                rangeSelectionMode === 'relative' && (React.createElement(RelativeRangePicker, { isSingleGrid: isSingleGrid, options: relativeOptions, dateOnly: dateOnly, initialSelection: selectedRelativeRange, onChange: function (range) { return setSelectedRelativeRange(range); }, i18nStrings: i18nStrings }))),
                            React.createElement(InternalBox, { className: styles['validation-section'], margin: !validationResult.valid ? { top: 's' } : undefined }, !validationResult.valid && (React.createElement(React.Fragment, null,
                                React.createElement(InternalAlert, { type: "error", statusIconAriaLabel: i18nStrings.errorIconAriaLabel },
                                    React.createElement("span", { className: styles['validation-error'] }, validationResult.errorMessage)),
                                React.createElement(LiveRegion, null, validationResult.errorMessage))))),
                        React.createElement("div", { className: clsx(styles.footer, (_c = {},
                                _c[styles['one-grid']] = isSingleGrid,
                                _c[styles['has-clear-button']] = showClearButton,
                                _c)) },
                            showClearButton && (React.createElement("div", { className: styles['footer-button-wrapper'] },
                                React.createElement(InternalButton, { onClick: onClear, className: styles['clear-button'], variant: "link", formAction: "none" }, i18nStrings.clearButtonLabel))),
                            React.createElement("div", { className: styles['footer-button-wrapper'] },
                                React.createElement(SpaceBetween, { size: "xs", direction: "horizontal" },
                                    React.createElement(InternalButton, { onClick: closeDropdown, className: styles['cancel-button'], variant: "link", formAction: "none" }, i18nStrings.cancelButtonLabel),
                                    React.createElement(InternalButton, { onClick: onApply, className: styles['apply-button'], ref: applyButtonRef, formAction: "none" }, i18nStrings.applyButtonLabel))))))))));
}
//# sourceMappingURL=dropdown.js.map