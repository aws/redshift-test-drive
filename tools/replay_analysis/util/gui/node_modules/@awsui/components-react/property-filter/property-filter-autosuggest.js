// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign, __rest } from "tslib";
import React, { useMemo, useRef } from 'react';
import { useAutosuggestItems } from '../autosuggest/options-controller';
import { useDropdownStatus } from '../internal/components/dropdown-status';
import DropdownFooter from '../internal/components/dropdown-footer';
import { generateUniqueId, useUniqueId } from '../internal/hooks/use-unique-id';
import { fireNonCancelableEvent, } from '../internal/events';
import autosuggestStyles from '../autosuggest/styles.css.js';
import styles from './styles.css.js';
import { fireCancelableEvent } from '../internal/events/index';
import AutosuggestOptionsList from '../autosuggest/options-list';
import { useAutosuggestLoadMore } from '../autosuggest/load-more-controller';
import AutosuggestInput from '../internal/components/autosuggest-input';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import clsx from 'clsx';
import { getFirstFocusable } from '../internal/components/focus-lock/utils';
import { filterOptions } from './filter-options';
var DROPDOWN_WIDTH_OPTIONS_LIST = 300;
var DROPDOWN_WIDTH_CUSTOM_FORM = 200;
var PropertyFilterAutosuggest = React.forwardRef(function (props, ref) {
    var _a;
    var value = props.value, onChange = props.onChange, onFocus = props.onFocus, onBlur = props.onBlur, onLoadItems = props.onLoadItems, options = props.options, _b = props.statusType, statusType = _b === void 0 ? 'finished' : _b, placeholder = props.placeholder, disabled = props.disabled, ariaLabel = props.ariaLabel, enteredTextLabel = props.enteredTextLabel, onKeyDown = props.onKeyDown, virtualScroll = props.virtualScroll, expandToViewport = props.expandToViewport, customForm = props.customForm, filterText = props.filterText, onOptionClick = props.onOptionClick, hideEnteredTextOption = props.hideEnteredTextOption, rest = __rest(props, ["value", "onChange", "onFocus", "onBlur", "onLoadItems", "options", "statusType", "placeholder", "disabled", "ariaLabel", "enteredTextLabel", "onKeyDown", "virtualScroll", "expandToViewport", "customForm", "filterText", "onOptionClick", "hideEnteredTextOption"]);
    var highlightText = filterText === undefined ? value : filterText;
    var customFormRef = useRef(null);
    var autosuggestInputRef = useRef(null);
    var mergedRef = useMergeRefs(autosuggestInputRef, ref);
    var filteredOptions = useMemo(function () { return filterOptions(options || [], highlightText); }, [options, highlightText]);
    var _c = useAutosuggestItems({
        options: filteredOptions,
        filterValue: value,
        filterText: highlightText,
        filteringType: 'manual',
        hideEnteredTextLabel: hideEnteredTextOption,
        onSelectItem: function (option) {
            var _a;
            var value = option.value || '';
            fireNonCancelableEvent(onChange, { value: value });
            var selectedCancelled = fireCancelableEvent(onOptionClick, option);
            if (!selectedCancelled) {
                (_a = autosuggestInputRef.current) === null || _a === void 0 ? void 0 : _a.close();
            }
            else {
                autosuggestItemsHandlers.resetHighlightWithKeyboard();
            }
        }
    }), autosuggestItemsState = _c[0], autosuggestItemsHandlers = _c[1];
    var autosuggestLoadMoreHandlers = useAutosuggestLoadMore({
        options: options,
        statusType: statusType,
        onLoadItems: function (detail) { return fireNonCancelableEvent(onLoadItems, detail); }
    });
    var handleChange = function (event) {
        autosuggestItemsHandlers.resetHighlightWithKeyboard();
        fireNonCancelableEvent(onChange, event.detail);
    };
    var handleDelayedInput = function (event) {
        autosuggestLoadMoreHandlers.fireLoadMoreOnInputChange(event.detail.value);
    };
    var handleFocus = function () {
        autosuggestLoadMoreHandlers.fireLoadMoreOnInputFocus();
        fireCancelableEvent(onFocus, null);
    };
    var handleBlur = function () {
        fireCancelableEvent(onBlur, null);
    };
    var handleKeyDown = function (e) {
        fireCancelableEvent(onKeyDown, e.detail);
    };
    var handlePressArrowDown = function () {
        var _a;
        autosuggestItemsHandlers.moveHighlightWithKeyboard(1);
        if (customFormRef.current) {
            (_a = getFirstFocusable(customFormRef.current)) === null || _a === void 0 ? void 0 : _a.focus();
        }
    };
    var handlePressArrowUp = function () {
        autosuggestItemsHandlers.moveHighlightWithKeyboard(-1);
    };
    var handlePressEnter = function () {
        return autosuggestItemsHandlers.selectHighlightedOptionWithKeyboard();
    };
    var handleCloseDropdown = function () {
        autosuggestItemsHandlers.resetHighlightWithKeyboard();
    };
    var handleRecoveryClick = function () {
        var _a;
        autosuggestLoadMoreHandlers.fireLoadMoreOnRecoveryClick();
        (_a = autosuggestInputRef.current) === null || _a === void 0 ? void 0 : _a.focus();
    };
    var selfControlId = useUniqueId('input');
    var controlId = (_a = rest.controlId) !== null && _a !== void 0 ? _a : selfControlId;
    var listId = useUniqueId('list');
    var highlightedOptionId = autosuggestItemsState.highlightedOption ? generateUniqueId() : undefined;
    var isEmpty = !value && !autosuggestItemsState.items.length;
    var dropdownStatus = useDropdownStatus(__assign(__assign({}, props), { isEmpty: isEmpty, onRecoveryClick: handleRecoveryClick }));
    var content = null;
    if (customForm) {
        content = (React.createElement("div", { ref: customFormRef, className: styles['custom-content-wrapper'] }, customForm));
    }
    else if (autosuggestItemsState.items.length > 0) {
        content = (React.createElement(AutosuggestOptionsList, { autosuggestItemsState: autosuggestItemsState, autosuggestItemsHandlers: autosuggestItemsHandlers, highlightedOptionId: highlightedOptionId, highlightText: highlightText, listId: listId, controlId: controlId, enteredTextLabel: enteredTextLabel, handleLoadMore: autosuggestLoadMoreHandlers.fireLoadMoreOnScroll, hasDropdownStatus: dropdownStatus.content !== null, virtualScroll: virtualScroll, listBottom: !dropdownStatus.isSticky ? React.createElement(DropdownFooter, { content: dropdownStatus.content }) : null }));
    }
    return (React.createElement(AutosuggestInput, __assign({ ref: mergedRef }, rest, { className: clsx(autosuggestStyles.root, styles.input), value: value, onChange: handleChange, onFocus: handleFocus, onBlur: handleBlur, onKeyDown: handleKeyDown, controlId: controlId, placeholder: placeholder, disabled: disabled, ariaLabel: ariaLabel, expandToViewport: expandToViewport, ariaControls: listId, ariaActivedescendant: highlightedOptionId, dropdownExpanded: autosuggestItemsState.items.length > 1 || dropdownStatus.content !== null || !!customForm, dropdownContentKey: customForm ? 'custom' : 'options', dropdownContent: content, dropdownFooter: dropdownStatus.isSticky ? (React.createElement(DropdownFooter, { content: dropdownStatus.content, hasItems: autosuggestItemsState.items.length >= 1 })) : null, dropdownWidth: customForm ? DROPDOWN_WIDTH_CUSTOM_FORM : DROPDOWN_WIDTH_OPTIONS_LIST, dropdownContentFocusable: !!customForm, onCloseDropdown: handleCloseDropdown, onDelayedInput: handleDelayedInput, onPressArrowDown: handlePressArrowDown, onPressArrowUp: handlePressArrowUp, onPressEnter: handlePressEnter })));
});
export default PropertyFilterAutosuggest;
//# sourceMappingURL=property-filter-autosuggest.js.map