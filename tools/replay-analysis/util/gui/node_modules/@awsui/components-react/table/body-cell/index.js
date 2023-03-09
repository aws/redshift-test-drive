import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import styles from './styles.css.js';
import React, { useCallback, useRef } from 'react';
import useFocusVisible from '../../internal/hooks/focus-visible';
import { useEffectOnUpdate } from '../../internal/hooks/use-effect-on-update';
import Button from '../../button/internal';
import { TableTdElement } from './td-element';
import { InlineEditor } from './inline-editor';
import { useStableScrollPosition } from './use-stable-scroll-position';
var submitHandlerFallback = function () {
    throw new Error('The function `handleSubmit` is required for editable columns');
};
function TableCellEditable(_a) {
    var _b;
    var className = _a.className, item = _a.item, column = _a.column, isEditing = _a.isEditing, onEditStart = _a.onEditStart, onEditEnd = _a.onEditEnd, submitEdit = _a.submitEdit, ariaLabels = _a.ariaLabels, isVisualRefresh = _a.isVisualRefresh, rest = __rest(_a, ["className", "item", "column", "isEditing", "onEditStart", "onEditEnd", "submitEdit", "ariaLabels", "isVisualRefresh"]);
    var editActivateRef = useRef(null);
    var cellRef = useRef(null);
    var focusVisible = useFocusVisible();
    var _c = useStableScrollPosition(cellRef), storeScrollPosition = _c.storeScrollPosition, restoreScrollPosition = _c.restoreScrollPosition;
    var handleEditStart = function () {
        storeScrollPosition();
        if (!isEditing) {
            onEditStart();
        }
    };
    var scheduleRestoreScrollPosition = useCallback(function () { return setTimeout(restoreScrollPosition, 0); }, [restoreScrollPosition]);
    var tdNativeAttributes = __assign(__assign({}, focusVisible), { onFocus: scheduleRestoreScrollPosition, 'data-inline-editing-active': isEditing.toString() });
    useEffectOnUpdate(function () {
        if (!isEditing && editActivateRef.current) {
            editActivateRef.current.focus({ preventScroll: true });
        }
        var timer = scheduleRestoreScrollPosition();
        return function () { return clearTimeout(timer); };
    }, [isEditing, scheduleRestoreScrollPosition]);
    return (React.createElement(TableTdElement, __assign({}, rest, { nativeAttributes: tdNativeAttributes, className: clsx(className, styles['body-cell-editable'], isEditing && styles['body-cell-edit-active'], isVisualRefresh && styles['is-visual-refresh']), onClick: handleEditStart, ref: cellRef }), isEditing ? (React.createElement(InlineEditor, { ariaLabels: ariaLabels, column: column, item: item, onEditEnd: onEditEnd, submitEdit: submitEdit !== null && submitEdit !== void 0 ? submitEdit : submitHandlerFallback, __onRender: restoreScrollPosition })) : (React.createElement(React.Fragment, null,
        column.cell(item),
        React.createElement("span", { className: styles['body-cell-editor'] },
            React.createElement(Button, { __hideFocusOutline: true, __internalRootRef: editActivateRef, ariaLabel: (_b = ariaLabels === null || ariaLabels === void 0 ? void 0 : ariaLabels.activateEditLabel) === null || _b === void 0 ? void 0 : _b.call(ariaLabels, column), formAction: "none", iconName: "edit", variant: "inline-icon" }))))));
}
export function TableBodyCell(_a) {
    var isEditable = _a.isEditable, rest = __rest(_a, ["isEditable"]);
    if (isEditable || rest.isEditing) {
        return React.createElement(TableCellEditable, __assign({}, rest));
    }
    var column = rest.column, item = rest.item;
    return React.createElement(TableTdElement, __assign({}, rest), column.cell(item));
}
//# sourceMappingURL=index.js.map