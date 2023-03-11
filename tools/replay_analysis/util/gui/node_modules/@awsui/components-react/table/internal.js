import { __assign, __awaiter, __generator, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useImperativeHandle, useRef, useState } from 'react';
import InternalContainer from '../container/internal';
import { getBaseProps } from '../internal/base-component';
import ToolsHeader from './tools-header';
import Thead from './thead';
import { TableBodyCell } from './body-cell';
import InternalStatusIndicator from '../status-indicator/internal';
import { useContainerQuery } from '../internal/hooks/container-queries';
import { supportsStickyPosition } from '../internal/utils/dom';
import SelectionControl from './selection-control';
import { checkSortingState, getColumnKey, getItemKey, toContainerVariant } from './utils';
import { useRowEvents } from './use-row-events';
import { focusMarkers, useFocusMove, useSelection } from './use-selection';
import { fireCancelableEvent, fireNonCancelableEvent } from '../internal/events';
import { isDevelopment } from '../internal/is-development';
import { checkColumnWidths, ColumnWidthsProvider, DEFAULT_WIDTH } from './use-column-widths';
import { useScrollSync } from '../internal/hooks/use-scroll-sync';
import { ResizeTracker } from './resizer';
import styles from './styles.css.js';
import { useVisualRefresh } from '../internal/hooks/use-visual-mode';
import StickyHeader from './sticky-header';
import StickyScrollbar from './sticky-scrollbar';
import useFocusVisible from '../internal/hooks/focus-visible';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import useMouseDownTarget from '../internal/hooks/use-mouse-down-target';
import { useDynamicOverlap } from '../internal/hooks/use-dynamic-overlap';
import LiveRegion from '../internal/components/live-region';
import useTableFocusNavigation from './use-table-focus-navigation';
import { TableTdElement } from './body-cell/td-element';
var InternalTable = React.forwardRef(function (_a, ref) {
    var _b;
    var header = _a.header, footer = _a.footer, empty = _a.empty, filter = _a.filter, pagination = _a.pagination, preferences = _a.preferences, items = _a.items, columnDefinitions = _a.columnDefinitions, trackBy = _a.trackBy, loading = _a.loading, loadingText = _a.loadingText, selectionType = _a.selectionType, selectedItems = _a.selectedItems, isItemDisabled = _a.isItemDisabled, ariaLabels = _a.ariaLabels, onSelectionChange = _a.onSelectionChange, onSortingChange = _a.onSortingChange, sortingColumn = _a.sortingColumn, sortingDescending = _a.sortingDescending, sortingDisabled = _a.sortingDisabled, visibleColumns = _a.visibleColumns, stickyHeader = _a.stickyHeader, stickyHeaderVerticalOffset = _a.stickyHeaderVerticalOffset, onRowClick = _a.onRowClick, onRowContextMenu = _a.onRowContextMenu, wrapLines = _a.wrapLines, stripedRows = _a.stripedRows, submitEdit = _a.submitEdit, onEditCancel = _a.onEditCancel, resizableColumns = _a.resizableColumns, onColumnWidthsChange = _a.onColumnWidthsChange, variant = _a.variant, __internalRootRef = _a.__internalRootRef, totalItemsCount = _a.totalItemsCount, firstIndex = _a.firstIndex, renderAriaLive = _a.renderAriaLive, rest = __rest(_a, ["header", "footer", "empty", "filter", "pagination", "preferences", "items", "columnDefinitions", "trackBy", "loading", "loadingText", "selectionType", "selectedItems", "isItemDisabled", "ariaLabels", "onSelectionChange", "onSortingChange", "sortingColumn", "sortingDescending", "sortingDisabled", "visibleColumns", "stickyHeader", "stickyHeaderVerticalOffset", "onRowClick", "onRowContextMenu", "wrapLines", "stripedRows", "submitEdit", "onEditCancel", "resizableColumns", "onColumnWidthsChange", "variant", "__internalRootRef", "totalItemsCount", "firstIndex", "renderAriaLive"]);
    var baseProps = getBaseProps(rest);
    stickyHeader = stickyHeader && supportsStickyPosition();
    var _c = useContainerQuery(function (_a) {
        var width = _a.width;
        return width;
    }), containerWidth = _c[0], wrapperMeasureRef = _c[1];
    var wrapperRefObject = useRef(null);
    var wrapperRef = useMergeRefs(wrapperMeasureRef, wrapperRefObject);
    var _d = useContainerQuery(function (_a) {
        var width = _a.width;
        return width;
    }), tableWidth = _d[0], tableMeasureRef = _d[1];
    var tableRefObject = useRef(null);
    var tableRef = useMergeRefs(tableMeasureRef, tableRefObject);
    var secondaryWrapperRef = React.useRef(null);
    var theadRef = useRef(null);
    var stickyHeaderRef = React.useRef(null);
    var scrollbarRef = React.useRef(null);
    var _e = useState(null), currentEditCell = _e[0], setCurrentEditCell = _e[1];
    var _f = useState(false), currentEditLoading = _f[0], setCurrentEditLoading = _f[1];
    useImperativeHandle(ref, function () {
        var _a;
        return ({
            scrollToTop: ((_a = stickyHeaderRef.current) === null || _a === void 0 ? void 0 : _a.scrollToTop) || (function () { return undefined; }),
            cancelEdit: function () { return setCurrentEditCell(null); }
        });
    }, []);
    var handleScroll = useScrollSync([wrapperRefObject, scrollbarRef, secondaryWrapperRef], !supportsStickyPosition());
    var _g = useFocusMove(selectionType, items.length), moveFocusDown = _g.moveFocusDown, moveFocusUp = _g.moveFocusUp, moveFocus = _g.moveFocus;
    var _h = useRowEvents({ onRowClick: onRowClick, onRowContextMenu: onRowContextMenu }), onRowClickHandler = _h.onRowClickHandler, onRowContextMenuHandler = _h.onRowContextMenuHandler;
    var visibleColumnDefinitions = visibleColumns
        ? columnDefinitions.filter(function (column) { return column.id && visibleColumns.indexOf(column.id) !== -1; })
        : columnDefinitions;
    var _j = useSelection({
        items: items,
        trackBy: trackBy,
        selectedItems: selectedItems,
        selectionType: selectionType,
        isItemDisabled: isItemDisabled,
        onSelectionChange: onSelectionChange,
        ariaLabels: ariaLabels
    }), isItemSelected = _j.isItemSelected, selectAllProps = _j.selectAllProps, getItemSelectionProps = _j.getItemSelectionProps, updateShiftToggle = _j.updateShiftToggle;
    if (loading) {
        selectAllProps.disabled = true;
    }
    if (isDevelopment) {
        if (resizableColumns) {
            checkColumnWidths(columnDefinitions);
        }
        if (sortingColumn === null || sortingColumn === void 0 ? void 0 : sortingColumn.sortingComparator) {
            checkSortingState(columnDefinitions, sortingColumn.sortingComparator);
        }
    }
    var isVisualRefresh = useVisualRefresh();
    var computedVariant = isVisualRefresh
        ? variant
        : ['embedded', 'full-page'].indexOf(variant) > -1
            ? 'container'
            : variant;
    var hasHeader = !!(header || filter || pagination || preferences);
    var hasSelection = !!selectionType;
    var hasFooter = !!footer;
    var theadProps = {
        containerWidth: containerWidth,
        selectionType: selectionType,
        selectAllProps: selectAllProps,
        columnDefinitions: visibleColumnDefinitions,
        variant: computedVariant,
        wrapLines: wrapLines,
        resizableColumns: resizableColumns,
        sortingColumn: sortingColumn,
        sortingDisabled: sortingDisabled,
        sortingDescending: sortingDescending,
        onSortingChange: onSortingChange,
        onFocusMove: moveFocus,
        onResizeFinish: function (newWidth) {
            var widthsDetail = columnDefinitions.map(function (column, index) { return newWidth[getColumnKey(column, index)] || column.width || DEFAULT_WIDTH; });
            var widthsChanged = widthsDetail.some(function (width, index) { return columnDefinitions[index].width !== width; });
            if (widthsChanged) {
                fireNonCancelableEvent(onColumnWidthsChange, { widths: widthsDetail });
            }
        },
        singleSelectionHeaderAriaLabel: ariaLabels === null || ariaLabels === void 0 ? void 0 : ariaLabels.selectionGroupLabel,
        stripedRows: stripedRows
    };
    // Allows keyboard users to scroll horizontally with arrow keys by making the wrapper part of the tab sequence
    var isWrapperScrollable = tableWidth && containerWidth && tableWidth > containerWidth;
    var wrapperProps = isWrapperScrollable
        ? { role: 'region', tabIndex: 0, 'aria-label': ariaLabels === null || ariaLabels === void 0 ? void 0 : ariaLabels.tableLabel }
        : {};
    var focusVisibleProps = useFocusVisible();
    var getMouseDownTarget = useMouseDownTarget();
    var wrapWithInlineLoadingState = function (submitEdit) {
        if (!submitEdit) {
            return undefined;
        }
        return function () {
            var args = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                args[_i] = arguments[_i];
            }
            return __awaiter(void 0, void 0, void 0, function () {
                return __generator(this, function (_a) {
                    switch (_a.label) {
                        case 0:
                            setCurrentEditLoading(true);
                            _a.label = 1;
                        case 1:
                            _a.trys.push([1, , 3, 4]);
                            return [4 /*yield*/, submitEdit.apply(void 0, args)];
                        case 2:
                            _a.sent();
                            return [3 /*break*/, 4];
                        case 3:
                            setCurrentEditLoading(false);
                            return [7 /*endfinally*/];
                        case 4: return [2 /*return*/];
                    }
                });
            });
        };
    };
    var hasDynamicHeight = computedVariant === 'full-page';
    var overlapElement = useDynamicOverlap({ disabled: !hasDynamicHeight });
    useTableFocusNavigation(selectionType, tableRefObject, visibleColumnDefinitions, items === null || items === void 0 ? void 0 : items.length);
    return (React.createElement(ColumnWidthsProvider, { tableRef: tableRefObject, visibleColumnDefinitions: visibleColumnDefinitions, resizableColumns: resizableColumns, hasSelection: hasSelection },
        React.createElement(InternalContainer, __assign({}, baseProps, { __internalRootRef: __internalRootRef, className: clsx(baseProps.className, styles.root), header: React.createElement(React.Fragment, null,
                hasHeader && (React.createElement("div", { ref: overlapElement, className: clsx(hasDynamicHeight && [styles['dark-header'], 'awsui-context-content-header']) },
                    React.createElement("div", { className: clsx(styles['header-controls'], styles["variant-".concat(computedVariant)]) },
                        React.createElement(ToolsHeader, { header: header, filter: filter, pagination: pagination, preferences: preferences })))),
                stickyHeader && (React.createElement(StickyHeader, { ref: stickyHeaderRef, variant: computedVariant, theadProps: theadProps, wrapperRef: wrapperRefObject, theadRef: theadRef, secondaryWrapperRef: secondaryWrapperRef, tableRef: tableRefObject, onScroll: handleScroll, tableHasHeader: hasHeader }))), disableHeaderPaddings: true, disableContentPaddings: true, variant: toContainerVariant(computedVariant), __disableFooterPaddings: true, __disableFooterDivider: true, footer: footer && (React.createElement("div", { className: clsx(styles['footer-wrapper'], styles["variant-".concat(computedVariant)]) },
                React.createElement("div", { className: styles.footer }, footer))), __stickyHeader: stickyHeader, __stickyOffset: stickyHeaderVerticalOffset }, focusMarkers.root),
            React.createElement("div", __assign({ ref: wrapperRef, className: clsx(styles.wrapper, styles["variant-".concat(computedVariant)], (_b = {},
                    _b[styles['has-footer']] = hasFooter,
                    _b[styles['has-header']] = hasHeader,
                    _b)), onScroll: handleScroll }, wrapperProps, focusVisibleProps),
                !!renderAriaLive && !!firstIndex && (React.createElement(LiveRegion, null,
                    React.createElement("span", null, renderAriaLive({ totalItemsCount: totalItemsCount, firstIndex: firstIndex, lastIndex: firstIndex + items.length })))),
                React.createElement("table", { ref: tableRef, className: clsx(styles.table, resizableColumns && styles['table-layout-fixed']), 
                    // Browsers have weird mechanism to guess whether it's a data table or a layout table.
                    // If we state explicitly, they get it always correctly even with low number of rows.
                    role: "table", "aria-label": ariaLabels === null || ariaLabels === void 0 ? void 0 : ariaLabels.tableLabel, "aria-rowcount": totalItemsCount ? totalItemsCount + 1 : -1 },
                    React.createElement(Thead, __assign({ ref: theadRef, hidden: stickyHeader, onCellFocus: function (colIndex) { var _a; return (_a = stickyHeaderRef.current) === null || _a === void 0 ? void 0 : _a.setFocusedColumn(colIndex); }, onCellBlur: function () { var _a; return (_a = stickyHeaderRef.current) === null || _a === void 0 ? void 0 : _a.setFocusedColumn(null); } }, theadProps)),
                    React.createElement("tbody", null, loading || items.length === 0 ? (React.createElement("tr", null,
                        React.createElement("td", { colSpan: selectionType ? visibleColumnDefinitions.length + 1 : visibleColumnDefinitions.length, className: clsx(styles['cell-merged'], hasFooter && styles['has-footer']) },
                            React.createElement("div", { className: styles['cell-merged-content'], style: {
                                    width: (supportsStickyPosition() && containerWidth && Math.floor(containerWidth)) || undefined
                                } }, loading ? (React.createElement(InternalStatusIndicator, { type: "loading", className: styles.loading, wrapText: true },
                                React.createElement(LiveRegion, { visible: true }, loadingText))) : (React.createElement("div", { className: styles.empty }, empty)))))) : (items.map(function (item, rowIndex) {
                        var firstVisible = rowIndex === 0;
                        var lastVisible = rowIndex === items.length - 1;
                        var isEven = rowIndex % 2 === 0;
                        var isSelected = !!selectionType && isItemSelected(item);
                        var isPrevSelected = !!selectionType && !firstVisible && isItemSelected(items[rowIndex - 1]);
                        var isNextSelected = !!selectionType && !lastVisible && isItemSelected(items[rowIndex + 1]);
                        return (React.createElement("tr", __assign({ key: getItemKey(trackBy, item, rowIndex), className: clsx(styles.row, isSelected && styles['row-selected']), onFocus: function (_a) {
                                var _b;
                                var currentTarget = _a.currentTarget;
                                // When an element inside table row receives focus we want to adjust the scroll.
                                // However, that behaviour is unwanted when the focus is received as result of a click
                                // as it causes the click to never reach the target element.
                                if (!currentTarget.contains(getMouseDownTarget())) {
                                    (_b = stickyHeaderRef.current) === null || _b === void 0 ? void 0 : _b.scrollToRow(currentTarget);
                                }
                            } }, focusMarkers.item, { onClick: onRowClickHandler && onRowClickHandler.bind(null, rowIndex, item), onContextMenu: onRowContextMenuHandler && onRowContextMenuHandler.bind(null, rowIndex, item), "aria-rowindex": firstIndex ? firstIndex + rowIndex + 1 : undefined }),
                            selectionType !== undefined && (React.createElement(TableTdElement, { className: clsx(styles['selection-control']), isVisualRefresh: isVisualRefresh, isFirstRow: firstVisible, isLastRow: lastVisible, isSelected: isSelected, isNextSelected: isNextSelected, isPrevSelected: isPrevSelected, wrapLines: false, isEvenRow: isEven, stripedRows: stripedRows, hasSelection: hasSelection, hasFooter: hasFooter },
                                React.createElement(SelectionControl, __assign({ onFocusDown: moveFocusDown, onFocusUp: moveFocusUp, onShiftToggle: updateShiftToggle }, getItemSelectionProps(item))))),
                            visibleColumnDefinitions.map(function (column, colIndex) {
                                var isEditing = !!currentEditCell && currentEditCell[0] === rowIndex && currentEditCell[1] === colIndex;
                                var isEditable = !!column.editConfig && !currentEditLoading;
                                return (React.createElement(TableBodyCell, { key: getColumnKey(column, colIndex), style: resizableColumns
                                        ? {}
                                        : {
                                            width: column.width,
                                            minWidth: column.minWidth,
                                            maxWidth: column.maxWidth
                                        }, ariaLabels: ariaLabels, column: column, item: item, wrapLines: wrapLines, isEditable: isEditable, isEditing: isEditing, isFirstRow: firstVisible, isLastRow: lastVisible, isSelected: isSelected, isNextSelected: isNextSelected, isPrevSelected: isPrevSelected, onEditStart: function () { return setCurrentEditCell([rowIndex, colIndex]); }, onEditEnd: function () {
                                        var wasCancelled = fireCancelableEvent(onEditCancel, {});
                                        if (!wasCancelled) {
                                            setCurrentEditCell(null);
                                        }
                                    }, submitEdit: wrapWithInlineLoadingState(submitEdit), hasFooter: hasFooter, stripedRows: stripedRows, isEvenRow: isEven, isVisualRefresh: isVisualRefresh }));
                            })));
                    })))),
                resizableColumns && React.createElement(ResizeTracker, null)),
            React.createElement(StickyScrollbar, { ref: scrollbarRef, wrapperRef: wrapperRefObject, tableRef: tableRefObject, onScroll: handleScroll }))));
});
export default InternalTable;
//# sourceMappingURL=internal.js.map