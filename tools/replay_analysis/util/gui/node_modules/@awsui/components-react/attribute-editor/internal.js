import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useImperativeHandle, useRef } from 'react';
import clsx from 'clsx';
import { getBaseProps } from '../internal/base-component';
import { InternalButton } from '../button/internal';
import { AdditionalInfo } from './additional-info';
import { Row } from './row';
import styles from './styles.css.js';
import { useContainerBreakpoints } from '../internal/hooks/container-queries';
import InternalBox from '../box/internal';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import { useUniqueId } from '../internal/hooks/use-unique-id';
var InternalAttributeEditor = React.forwardRef(function (_a, ref) {
    var additionalInfo = _a.additionalInfo, disableAddButton = _a.disableAddButton, definition = _a.definition, items = _a.items, _b = _a.isItemRemovable, isItemRemovable = _b === void 0 ? function () { return true; } : _b, empty = _a.empty, addButtonText = _a.addButtonText, removeButtonText = _a.removeButtonText, i18nStrings = _a.i18nStrings, onAddButtonClick = _a.onAddButtonClick, onRemoveButtonClick = _a.onRemoveButtonClick, _c = _a.__internalRootRef, __internalRootRef = _c === void 0 ? null : _c, props = __rest(_a, ["additionalInfo", "disableAddButton", "definition", "items", "isItemRemovable", "empty", "addButtonText", "removeButtonText", "i18nStrings", "onAddButtonClick", "onRemoveButtonClick", "__internalRootRef"]);
    var _d = useContainerBreakpoints(['default', 'xxs', 'xs']), breakpoint = _d[0], breakpointRef = _d[1];
    var removeButtonRefs = useRef([]);
    var wasNonEmpty = useRef(false);
    var baseProps = getBaseProps(props);
    var isEmpty = items && items.length === 0;
    wasNonEmpty.current = wasNonEmpty.current || !isEmpty;
    useImperativeHandle(ref, function () { return ({
        focusRemoveButton: function (rowIndex) {
            var _a;
            (_a = removeButtonRefs.current[rowIndex]) === null || _a === void 0 ? void 0 : _a.focus();
        }
    }); });
    var mergedRef = useMergeRefs(breakpointRef, __internalRootRef);
    var additionalInfoId = useUniqueId('attribute-editor-info');
    var infoAriaDescribedBy = additionalInfo ? additionalInfoId : undefined;
    return (React.createElement("div", __assign({}, baseProps, { ref: mergedRef, className: clsx(baseProps.className, styles.root) }),
        React.createElement(InternalBox, { margin: { bottom: 'l' } },
            isEmpty && React.createElement("div", { className: clsx(styles.empty, wasNonEmpty.current && styles['empty-appear']) }, empty),
            items.map(function (item, index) { return (React.createElement(Row, { key: index, index: index, breakpoint: breakpoint, item: item, definition: definition, i18nStrings: i18nStrings, removable: isItemRemovable(item), removeButtonText: removeButtonText, removeButtonRefs: removeButtonRefs.current, onRemoveButtonClick: onRemoveButtonClick })); })),
        React.createElement(InternalButton, { className: styles['add-button'], disabled: disableAddButton, onClick: onAddButtonClick, formAction: "none", __nativeAttributes: { 'aria-describedby': infoAriaDescribedBy } }, addButtonText),
        additionalInfo && React.createElement(AdditionalInfo, { id: infoAriaDescribedBy }, additionalInfo)));
});
export default InternalAttributeEditor;
//# sourceMappingURL=internal.js.map