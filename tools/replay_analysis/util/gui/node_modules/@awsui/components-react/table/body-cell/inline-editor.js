import { __awaiter, __generator } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useEffect, useState } from 'react';
import Button from '../../button/internal';
import FormField from '../../form-field/internal';
import SpaceBetween from '../../space-between/internal';
import { useClickAway } from './click-away';
import styles from './styles.css.js';
// A function that does nothing
var noop = function () { return undefined; };
export function InlineEditor(_a) {
    var _b, _c;
    var ariaLabels = _a.ariaLabels, item = _a.item, column = _a.column, onEditEnd = _a.onEditEnd, submitEdit = _a.submitEdit, __onRender = _a.__onRender;
    var _d = useState(false), currentEditLoading = _d[0], setCurrentEditLoading = _d[1];
    var _e = useState(), currentEditValue = _e[0], setCurrentEditValue = _e[1];
    var cellContext = {
        currentValue: currentEditValue,
        setValue: setCurrentEditValue
    };
    function finishEdit(cancel) {
        if (cancel === void 0) { cancel = false; }
        if (!cancel) {
            setCurrentEditValue(undefined);
        }
        onEditEnd();
    }
    function onSubmitClick(evt) {
        return __awaiter(this, void 0, void 0, function () {
            var e_1;
            return __generator(this, function (_a) {
                switch (_a.label) {
                    case 0:
                        evt.preventDefault();
                        if (currentEditValue === undefined) {
                            finishEdit();
                            return [2 /*return*/];
                        }
                        setCurrentEditLoading(true);
                        _a.label = 1;
                    case 1:
                        _a.trys.push([1, 3, , 4]);
                        return [4 /*yield*/, submitEdit(item, column, currentEditValue)];
                    case 2:
                        _a.sent();
                        setCurrentEditLoading(false);
                        finishEdit();
                        return [3 /*break*/, 4];
                    case 3:
                        e_1 = _a.sent();
                        setCurrentEditLoading(false);
                        return [3 /*break*/, 4];
                    case 4: return [2 /*return*/];
                }
            });
        });
    }
    function onCancel() {
        if (currentEditLoading) {
            return;
        }
        finishEdit(true);
    }
    function handleEscape(event) {
        if (event.key === 'Escape') {
            onCancel();
        }
    }
    var clickAwayRef = useClickAway(onCancel);
    useEffect(function () {
        if (__onRender) {
            var timer_1 = setTimeout(__onRender, 1);
            return function () { return clearTimeout(timer_1); };
        }
    }, [__onRender]);
    // asserting non-undefined editConfig here because this component is unreachable otherwise
    var _f = column.editConfig, _g = _f.ariaLabel, ariaLabel = _g === void 0 ? undefined : _g, _h = _f.validation, validation = _h === void 0 ? noop : _h, errorIconAriaLabel = _f.errorIconAriaLabel, editingCell = _f.editingCell;
    return (React.createElement("form", { ref: clickAwayRef, onSubmit: onSubmitClick, onKeyDown: handleEscape, className: styles['body-cell-editor-form'] },
        React.createElement(FormField, { stretch: true, label: ariaLabel, __hideLabel: true, __disableGutters: true, __useReactAutofocus: true, i18nStrings: { errorIconAriaLabel: errorIconAriaLabel }, errorText: validation(item, currentEditValue) },
            React.createElement("div", { className: styles['body-cell-editor-row'] },
                editingCell(item, cellContext),
                React.createElement("span", { className: styles['body-cell-editor-controls'] },
                    React.createElement(SpaceBetween, { direction: "horizontal", size: "xxs" },
                        !currentEditLoading ? (React.createElement(Button, { ariaLabel: (_b = ariaLabels === null || ariaLabels === void 0 ? void 0 : ariaLabels.cancelEditLabel) === null || _b === void 0 ? void 0 : _b.call(ariaLabels, column), formAction: "none", iconName: "close", variant: "inline-icon", onClick: onCancel })) : null,
                        React.createElement(Button, { ariaLabel: (_c = ariaLabels === null || ariaLabels === void 0 ? void 0 : ariaLabels.submitEditLabel) === null || _c === void 0 ? void 0 : _c.call(ariaLabels, column), formAction: "submit", iconName: "check", variant: "inline-icon", loading: currentEditLoading })))))));
}
//# sourceMappingURL=inline-editor.js.map