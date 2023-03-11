import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React from 'react';
import { getBaseProps } from '../internal/base-component';
import styles from './styles.css.js';
import { useFormFieldContext } from '../internal/context/form-field-context';
import { useUniqueId } from '../internal/hooks/use-unique-id';
import { useContainerBreakpoints } from '../internal/hooks/container-queries';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import { Tile } from './tile';
import useRadioGroupForwardFocus from '../internal/hooks/forward-focus/radio-group';
var COLUMN_TRIGGERS = ['default', 'xxs', 'xs'];
var InternalTiles = React.forwardRef(function (_a, ref) {
    var value = _a.value, items = _a.items, ariaLabel = _a.ariaLabel, ariaRequired = _a.ariaRequired, columns = _a.columns, onChange = _a.onChange, _b = _a.__internalRootRef, __internalRootRef = _b === void 0 ? null : _b, rest = __rest(_a, ["value", "items", "ariaLabel", "ariaRequired", "columns", "onChange", "__internalRootRef"]);
    var baseProps = getBaseProps(rest);
    var _c = useFormFieldContext(rest), ariaDescribedby = _c.ariaDescribedby, ariaLabelledby = _c.ariaLabelledby;
    var generatedName = useUniqueId('awsui-tiles-');
    var _d = useRadioGroupForwardFocus(ref, items, value), tileRef = _d[0], tileRefIndex = _d[1];
    var _e = useContainerBreakpoints(COLUMN_TRIGGERS), breakpoint = _e[0], breakpointRef = _e[1];
    var mergedRef = useMergeRefs(breakpointRef, __internalRootRef);
    var columnCount = getColumnCount(items, columns);
    return (React.createElement("div", __assign({ role: "radiogroup", "aria-label": ariaLabel, "aria-labelledby": ariaLabelledby, "aria-describedby": ariaDescribedby, "aria-required": ariaRequired }, baseProps, { className: clsx(baseProps.className, styles.root), ref: mergedRef }),
        React.createElement("div", { className: clsx(styles.columns, styles["column-".concat(columnCount)]) }, items &&
            items.map(function (item, index) { return (React.createElement(Tile, { ref: index === tileRefIndex ? tileRef : undefined, key: item.value, item: item, selected: item.value === value, name: generatedName, breakpoint: breakpoint, onChange: onChange })); }))));
});
function getColumnCount(items, columns) {
    if (columns) {
        return columns;
    }
    var nItems = items ? items.length : 0;
    var columnsLookup = {
        0: 1,
        1: 1,
        2: 2,
        4: 2,
        8: 2
    };
    return columnsLookup[nItems] || 3;
}
export default InternalTiles;
//# sourceMappingURL=internal.js.map