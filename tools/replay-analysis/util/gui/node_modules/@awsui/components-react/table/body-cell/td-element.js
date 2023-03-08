import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React from 'react';
import styles from './styles.css.js';
export var TableTdElement = React.forwardRef(function (_a, ref) {
    var className = _a.className, style = _a.style, children = _a.children, wrapLines = _a.wrapLines, isFirstRow = _a.isFirstRow, isLastRow = _a.isLastRow, isSelected = _a.isSelected, isNextSelected = _a.isNextSelected, isPrevSelected = _a.isPrevSelected, nativeAttributes = _a.nativeAttributes, onClick = _a.onClick, isEvenRow = _a.isEvenRow, stripedRows = _a.stripedRows, isVisualRefresh = _a.isVisualRefresh, hasSelection = _a.hasSelection, hasFooter = _a.hasFooter;
    return (React.createElement("td", __assign({ style: style, className: clsx(className, styles['body-cell'], wrapLines && styles['body-cell-wrap'], isFirstRow && styles['body-cell-first-row'], isLastRow && styles['body-cell-last-row'], isSelected && styles['body-cell-selected'], isNextSelected && styles['body-cell-next-selected'], isPrevSelected && styles['body-cell-prev-selected'], !isEvenRow && stripedRows && styles['body-cell-shaded'], stripedRows && styles['has-striped-rows'], isVisualRefresh && styles['is-visual-refresh'], hasSelection && styles['has-selection'], hasFooter && styles['has-footer']), onClick: onClick, ref: ref }, nativeAttributes), children));
});
//# sourceMappingURL=td-element.js.map