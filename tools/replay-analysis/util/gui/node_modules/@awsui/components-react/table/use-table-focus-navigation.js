// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useCallback, useEffect, useMemo, useRef } from 'react';
function iterateTableCells(table, func) {
    table.querySelectorAll('tr').forEach(function (row, rowIndex) {
        row.querySelectorAll('td').forEach(function (cell, cellIndex) {
            func(cell, rowIndex, cellIndex);
        });
    });
}
/**
 * This hook is used to navigate between table cells using the keyboard arrow keys.
 * All the functionality is implemented in the hook, so the table component does not
 * need to implement any keyboard event handlers.
 * @param enable - Toggle functionality of the hook
 * @param tableRoot - A ref to a table container. Ideally the root element of the table (<table>); tbody is also acceptable.
 * @param columnDefinitions - The column definitions for the table.
 * @param numRows - The number of rows in the table.
 */
function useTableFocusNavigation(selectionType, tableRoot, columnDefinitions, numRows) {
    if (selectionType === void 0) { selectionType = 'none'; }
    var currentFocusCell = useRef(null);
    var focusableColumns = useMemo(function () {
        var cols = columnDefinitions.map(function (column) { return !!column.editConfig; });
        if (selectionType !== 'none') {
            cols.unshift(false);
        }
        return cols;
    }, [columnDefinitions, selectionType]);
    var maxColumnIndex = useMemo(function () { return focusableColumns.length - 1; }, [focusableColumns]);
    var minColumnIndex = useMemo(function () { return (selectionType !== 'none' ? 1 : 0); }, [selectionType]);
    var focusCell = useCallback(function (rowIndex, columnIndex) {
        if (tableRoot === null || tableRoot === void 0 ? void 0 : tableRoot.current) {
            iterateTableCells(tableRoot.current, function (cell, rIndex, cIndex) {
                var _a;
                if (rIndex === rowIndex && cIndex === columnIndex) {
                    var editButton = cell.querySelector('button:last-child');
                    (_a = editButton === null || editButton === void 0 ? void 0 : editButton.focus) === null || _a === void 0 ? void 0 : _a.call(editButton, { preventScroll: true });
                }
            });
        }
    }, [tableRoot]);
    var shiftFocus = useCallback(function (vertical, horizontal) {
        // istanbul ignore if next
        if (!currentFocusCell.current) {
            return;
        }
        var _a = currentFocusCell.current.slice(), rowIndex = _a[0], columnIndex = _a[1];
        var newRowIndex = rowIndex;
        var newColumnIndex = columnIndex;
        if (vertical !== 0) {
            newRowIndex = Math.min(numRows, Math.max(rowIndex + vertical, 0));
        }
        if (horizontal !== 0) {
            while (newColumnIndex <= maxColumnIndex && newColumnIndex >= minColumnIndex) {
                newColumnIndex += horizontal;
                if (focusableColumns[newColumnIndex]) {
                    break;
                }
            }
        }
        if ((rowIndex !== newRowIndex || columnIndex !== newColumnIndex) &&
            currentFocusCell.current &&
            tableRoot.current) {
            focusCell(newRowIndex, newColumnIndex);
        }
    }, [focusCell, focusableColumns, maxColumnIndex, minColumnIndex, numRows, tableRoot]);
    var handleArrowKeyEvents = useCallback(function (event) {
        var _a, _b;
        var abort = !!((_a = tableRoot.current) === null || _a === void 0 ? void 0 : _a.querySelector('[data-inline-editing-active = "true"]')) ||
            !((_b = document.activeElement) === null || _b === void 0 ? void 0 : _b.closest('[data-inline-editing-active]'));
        if (abort) {
            return;
        }
        switch (event.key) {
            case 'ArrowUp':
                event.preventDefault();
                shiftFocus(-1, 0);
                break;
            case 'ArrowDown':
                event.preventDefault();
                shiftFocus(1, 0);
                break;
            case 'ArrowLeft':
                event.preventDefault();
                shiftFocus(0, -1);
                break;
            case 'ArrowRight':
                event.preventDefault();
                shiftFocus(0, 1);
                break;
            // istanbul ignore next (default case = do nothing, not testable)
            default:
                return;
        }
    }, [shiftFocus, tableRoot]);
    useEffect(function () {
        var eventListeners = new Map();
        // istanbul ignore if
        if (!tableRoot.current) {
            return;
        }
        var tableElement = tableRoot.current;
        // istanbul ignore next (tested in use-focus-navigation.test.tsx#L210)
        function cleanUpListeners() {
            iterateTableCells(tableElement, function (cell, rowIndex, columnIndex) {
                var listeners = eventListeners.get([rowIndex, columnIndex]);
                if (listeners === null || listeners === void 0 ? void 0 : listeners.focusin) {
                    cell.removeEventListener('focusin', listeners.focusin);
                }
            });
            tableElement.removeEventListener('keydown', handleArrowKeyEvents);
        }
        iterateTableCells(tableElement, function (cell, rowIndex, cellIndex) {
            if (!focusableColumns[cellIndex]) {
                return;
            }
            var listenerFns = {
                focusin: function () {
                    currentFocusCell.current = [rowIndex, cellIndex];
                }
            };
            eventListeners.set([rowIndex, cellIndex], listenerFns);
            cell.addEventListener('focusin', listenerFns.focusin, { passive: true });
        });
        tableElement.addEventListener('keydown', handleArrowKeyEvents);
        return function () { return tableElement && cleanUpListeners(); };
    }, [focusableColumns, handleArrowKeyEvents, tableRoot]);
}
export default useTableFocusNavigation;
//# sourceMappingURL=use-table-focus-navigation.js.map