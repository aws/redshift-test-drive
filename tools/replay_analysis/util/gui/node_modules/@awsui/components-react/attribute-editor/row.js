// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import InternalBox from '../box/internal';
import styles from './styles.css.js';
import React, { useCallback } from 'react';
import InternalFormField from '../form-field/internal';
import InternalColumnLayout from '../column-layout/internal';
import { fireNonCancelableEvent } from '../internal/events';
import InternalGrid from '../grid/internal';
import { InternalButton } from '../button/internal';
import clsx from 'clsx';
import { generateUniqueId } from '../internal/hooks/use-unique-id';
var Divider = function () { return React.createElement(InternalBox, { className: styles.divider, padding: { top: 'l' } }); };
function render(item, itemIndex, slot) {
    return typeof slot === 'function' ? slot(item, itemIndex) : slot;
}
var GRID_DEFINITION = [{ colspan: { "default": 12, xs: 9 } }];
var REMOVABLE_GRID_DEFINITION = [{ colspan: { "default": 12, xs: 9 } }, { colspan: { "default": 12, xs: 3 } }];
export var Row = React.memo(function (_a) {
    var breakpoint = _a.breakpoint, item = _a.item, definition = _a.definition, _b = _a.i18nStrings, i18nStrings = _b === void 0 ? {} : _b, index = _a.index, removable = _a.removable, removeButtonText = _a.removeButtonText, removeButtonRefs = _a.removeButtonRefs, onRemoveButtonClick = _a.onRemoveButtonClick;
    var isNarrowViewport = breakpoint === 'default' || breakpoint === 'xxs';
    var isWideViewport = !isNarrowViewport;
    var handleRemoveClick = useCallback(function () {
        fireNonCancelableEvent(onRemoveButtonClick, { itemIndex: index });
    }, [onRemoveButtonClick, index]);
    var firstControlId = generateUniqueId('first-control-id-');
    return (React.createElement(InternalBox, { className: styles.row, margin: { bottom: 's' } },
        React.createElement("div", { role: "group", "aria-labelledby": "".concat(firstControlId, "-label ").concat(firstControlId) },
            React.createElement(InternalGrid, { __breakpoint: breakpoint, gridDefinition: removable ? REMOVABLE_GRID_DEFINITION : GRID_DEFINITION },
                React.createElement(InternalColumnLayout, { className: styles['row-control'], columns: definition.length, __breakpoint: breakpoint }, definition.map(function (_a, defIndex) {
                    var info = _a.info, label = _a.label, constraintText = _a.constraintText, errorText = _a.errorText, control = _a.control;
                    return (React.createElement(InternalFormField, { key: defIndex, className: styles.field, label: label, info: info, constraintText: render(item, index, constraintText), errorText: render(item, index, errorText), stretch: true, i18nStrings: { errorIconAriaLabel: i18nStrings.errorIconAriaLabel }, __hideLabel: isWideViewport && index > 0, controlId: defIndex === 0 ? firstControlId : undefined }, render(item, index, control)));
                })),
                removable && (React.createElement(ButtonContainer, { index: index, isNarrowViewport: isNarrowViewport, hasLabel: definition.some(function (row) { return row.label; }) },
                    React.createElement(InternalButton, { className: styles['remove-button'], formAction: "none", ref: function (ref) {
                            removeButtonRefs[index] = ref !== null && ref !== void 0 ? ref : undefined;
                        }, onClick: handleRemoveClick }, removeButtonText))))),
        isNarrowViewport && React.createElement(Divider, null)));
});
var ButtonContainer = function (_a) {
    var _b;
    var index = _a.index, children = _a.children, isNarrowViewport = _a.isNarrowViewport, hasLabel = _a.hasLabel;
    return (React.createElement("div", { className: clsx((_b = {},
            _b[styles['button-container-haslabel']] = !isNarrowViewport && index === 0 && hasLabel,
            _b[styles['button-container-nolabel']] = !isNarrowViewport && index === 0 && !hasLabel,
            _b[styles['right-align']] = isNarrowViewport,
            _b)) }, children));
};
//# sourceMappingURL=row.js.map