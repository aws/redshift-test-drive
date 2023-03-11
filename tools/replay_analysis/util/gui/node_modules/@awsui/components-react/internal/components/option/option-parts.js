import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import styles from './styles.css.js';
import clsx from 'clsx';
import React from 'react';
import InternalIcon from '../../../icon/internal';
import HighlightMatch from './highlight-match';
export var Label = function (_a) {
    var label = _a.label, prefix = _a.prefix, highlightText = _a.highlightText, triggerVariant = _a.triggerVariant;
    return (React.createElement("span", { className: clsx(styles.label, triggerVariant && styles['trigger-variant']) },
        prefix && (React.createElement("span", { className: clsx(styles['label-prefix'], triggerVariant && styles['trigger-variant']) },
            prefix,
            " ")),
        React.createElement(HighlightMatch, { str: label, highlightText: highlightText })));
};
export var LabelTag = function (_a) {
    var labelTag = _a.labelTag, highlightText = _a.highlightText, triggerVariant = _a.triggerVariant;
    return labelTag ? (React.createElement("span", { className: clsx(styles['label-tag'], triggerVariant && styles['trigger-variant']) },
        React.createElement(HighlightMatch, { str: labelTag, highlightText: highlightText }))) : null;
};
export var Description = function (_a) {
    var _b;
    var description = _a.description, highlightedOption = _a.highlightedOption, highlightText = _a.highlightText, selectedOption = _a.selectedOption, triggerVariant = _a.triggerVariant;
    return description ? (React.createElement("span", { className: clsx(styles.description, (_b = {},
            _b[styles['trigger-variant']] = triggerVariant,
            _b[styles.highlighted] = highlightedOption,
            _b[styles.selected] = selectedOption,
            _b)) },
        React.createElement(HighlightMatch, { str: description, highlightText: highlightText }))) : null;
};
export var Tags = function (_a) {
    var _b;
    var tags = _a.tags, highlightedOption = _a.highlightedOption, highlightText = _a.highlightText, selectedOption = _a.selectedOption, triggerVariant = _a.triggerVariant;
    return tags ? (React.createElement("span", { className: clsx(styles.tags, (_b = {},
            _b[styles.highlighted] = highlightedOption,
            _b[styles.selected] = selectedOption,
            _b)) }, tags.map(function (tag, idx) { return (React.createElement("span", { key: idx, className: clsx(styles.tag, triggerVariant && styles['trigger-variant']) },
        React.createElement(HighlightMatch, { str: tag, highlightText: highlightText }))); }))) : null;
};
export var FilteringTags = function (_a) {
    var _b;
    var filteringTags = _a.filteringTags, highlightedOption = _a.highlightedOption, highlightText = _a.highlightText, selectedOption = _a.selectedOption, triggerVariant = _a.triggerVariant;
    if (!highlightText || !filteringTags) {
        return null;
    }
    var searchElement = highlightText.toLowerCase();
    return (React.createElement("span", { className: clsx(styles.tags, (_b = {},
            _b[styles.highlighted] = highlightedOption,
            _b[styles.selected] = selectedOption,
            _b)) }, filteringTags.map(function (filteringTag, key) {
        var match = filteringTag.toLowerCase().indexOf(searchElement) !== -1;
        if (match) {
            return (React.createElement("span", { className: clsx(styles.tag, triggerVariant && styles['trigger-variant']), key: key, "aria-disabled": true },
                React.createElement(HighlightMatch, { str: filteringTag, highlightText: highlightText })));
        }
        return null;
    })));
};
export var OptionIcon = function (props) {
    if (!props.name && !props.url && !props.svg) {
        return null;
    }
    return (React.createElement("span", { className: clsx(styles.icon, props.size === 'big' && [styles["icon-size-big"]]) },
        React.createElement(InternalIcon, __assign({}, props))));
};
//# sourceMappingURL=option-parts.js.map