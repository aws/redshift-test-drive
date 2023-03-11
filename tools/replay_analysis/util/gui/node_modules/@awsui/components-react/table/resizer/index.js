// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useEffect, useRef, useState } from 'react';
import { useStableEventHandler } from '../../internal/hooks/use-stable-event-handler';
import { getOverflowParents } from '../../internal/utils/scrollable-containers';
import { findUpUntil } from '../../internal/utils/dom';
import tableStyles from '../styles.css.js';
import styles from './styles.css.js';
import { KeyCode } from '../../internal/keycode';
import { DEFAULT_WIDTH } from '../use-column-widths';
var AUTO_GROW_START_TIME = 10;
var AUTO_GROW_INTERVAL = 10;
var AUTO_GROW_INCREMENT = 5;
export function Resizer(_a) {
    var onDragMove = _a.onDragMove, onFinish = _a.onFinish, ariaLabelledby = _a.ariaLabelledby, _b = _a.minWidth, minWidth = _b === void 0 ? DEFAULT_WIDTH : _b;
    var _c = useState(false), isDragging = _c[0], setIsDragging = _c[1];
    var _d = useState(), headerCell = _d[0], setHeaderCell = _d[1];
    var autoGrowTimeout = useRef();
    var onFinishStable = useStableEventHandler(onFinish);
    var onDragStable = useStableEventHandler(onDragMove);
    var _e = useState(false), resizerHasFocus = _e[0], setResizerHasFocus = _e[1];
    var _f = useState(0), headerCellWidth = _f[0], setHeaderCellWidth = _f[1];
    useEffect(function () {
        if ((!isDragging && !resizerHasFocus) || !headerCell) {
            return;
        }
        var rootElement = findUpUntil(headerCell, function (element) { return element.className.indexOf(tableStyles.root) > -1; });
        var tableElement = rootElement.querySelector("table");
        // tracker is rendered inside table wrapper to align with its size
        var tracker = rootElement.querySelector(".".concat(styles.tracker));
        var scrollParent = getOverflowParents(headerCell)[0];
        var _a = scrollParent.getBoundingClientRect(), leftEdge = _a.left, rightEdge = _a.right;
        var updateTrackerPosition = function (newOffset) {
            var scrollParentLeft = tableElement.getBoundingClientRect().left;
            tracker.style.top = headerCell.getBoundingClientRect().height + 'px';
            // minus one pixel to offset the cell border
            tracker.style.left = newOffset - scrollParentLeft - 1 + 'px';
        };
        var updateColumnWidth = function (newWidth) {
            var _a = headerCell.getBoundingClientRect(), right = _a.right, width = _a.width;
            var updatedWidth = newWidth < minWidth ? minWidth : newWidth;
            updateTrackerPosition(right + updatedWidth - width);
            setHeaderCellWidth(newWidth);
            // callbacks must be the last calls in the handler, because they may cause an extra update
            onDragStable(newWidth);
        };
        var resizeColumn = function (offset) {
            if (offset > leftEdge) {
                var cellLeft = headerCell.getBoundingClientRect().left;
                var newWidth = offset - cellLeft;
                // callbacks must be the last calls in the handler, because they may cause an extra update
                updateColumnWidth(newWidth);
            }
        };
        var onAutoGrow = function () {
            var width = headerCell.getBoundingClientRect().width;
            autoGrowTimeout.current = setTimeout(onAutoGrow, AUTO_GROW_INTERVAL);
            // callbacks must be the last calls in the handler, because they may cause an extra update
            updateColumnWidth(width + AUTO_GROW_INCREMENT);
            scrollParent.scrollLeft += AUTO_GROW_INCREMENT;
        };
        var onMouseMove = function (event) {
            clearTimeout(autoGrowTimeout.current);
            var offset = event.pageX;
            if (offset > rightEdge) {
                autoGrowTimeout.current = setTimeout(onAutoGrow, AUTO_GROW_START_TIME);
            }
            else {
                resizeColumn(offset);
            }
        };
        var onMouseUp = function (event) {
            resizeColumn(event.pageX);
            setIsDragging(false);
            onFinishStable();
            clearTimeout(autoGrowTimeout.current);
        };
        var onKeyDown = function (event) {
            // prevent screenreader cursor move
            if (event.keyCode === KeyCode.left || event.keyCode === KeyCode.right) {
                event.preventDefault();
            }
            // update width
            if (event.keyCode === KeyCode.left) {
                updateColumnWidth(headerCell.getBoundingClientRect().width - 10);
            }
            if (event.keyCode === KeyCode.right) {
                updateColumnWidth(headerCell.getBoundingClientRect().width + 10);
            }
        };
        updateTrackerPosition(headerCell.getBoundingClientRect().right);
        document.body.classList.add(styles['resize-active']);
        document.body.classList.remove(styles['resize-active-with-focus']);
        if (isDragging) {
            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        }
        if (resizerHasFocus) {
            document.body.classList.add(styles['resize-active-with-focus']);
            headerCell.addEventListener('keydown', onKeyDown);
        }
        return function () {
            clearTimeout(autoGrowTimeout.current);
            document.body.classList.remove(styles['resize-active']);
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            headerCell.removeEventListener('keydown', onKeyDown);
        };
    }, [headerCell, isDragging, onDragStable, onFinishStable, resizerHasFocus, minWidth]);
    return (React.createElement("span", { className: clsx(styles.resizer, isDragging && styles['resizer-active'], resizerHasFocus && styles['has-focus']), onMouseDown: function (event) {
            if (event.button !== 0) {
                return;
            }
            event.preventDefault();
            var headerCell = findUpUntil(event.currentTarget, function (element) { return element.tagName.toLowerCase() === 'th'; });
            setIsDragging(true);
            setHeaderCell(headerCell);
        }, onFocus: function (event) {
            var headerCell = findUpUntil(event.currentTarget, function (element) { return element.tagName.toLowerCase() === 'th'; });
            setHeaderCellWidth(headerCell.getBoundingClientRect().width);
            setResizerHasFocus(true);
            setHeaderCell(headerCell);
        }, onBlur: function () {
            setResizerHasFocus(false);
        }, role: "separator", "aria-orientation": "vertical", "aria-labelledby": ariaLabelledby, "aria-valuenow": headerCellWidth, "aria-valuetext": headerCellWidth.toString(), "aria-valuemin": minWidth, tabIndex: 0 }));
}
export function ResizeTracker() {
    return React.createElement("span", { className: styles.tracker });
}
//# sourceMappingURL=index.js.map