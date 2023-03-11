// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { nodeContains } from '../../internal/utils/dom';
import styles from '../styles.css.js';
import { isYThreshold } from '../utils';
var MAX_HOVER_MARGIN = 6;
var POPOVER_DEADZONE = 12;
export function useMouseHover(_a) {
    var plotRef = _a.plotRef, popoverRef = _a.popoverRef, scaledSeries = _a.scaledSeries, barGroups = _a.barGroups, highlightPoint = _a.highlightPoint, highlightGroup = _a.highlightGroup, clearHighlightedSeries = _a.clearHighlightedSeries, isGroupNavigation = _a.isGroupNavigation, isHandlersDisabled = _a.isHandlersDisabled, highlightX = _a.highlightX;
    var isMouseOverPopover = function (event) {
        var _a;
        if ((_a = popoverRef.current) === null || _a === void 0 ? void 0 : _a.firstChild) {
            var popoverPosition = popoverRef.current.firstChild.getBoundingClientRect();
            if (event.clientX > popoverPosition.x - POPOVER_DEADZONE &&
                event.clientX < popoverPosition.x + popoverPosition.width + POPOVER_DEADZONE &&
                event.clientY > popoverPosition.y - POPOVER_DEADZONE &&
                event.clientY < popoverPosition.y + popoverPosition.height + POPOVER_DEADZONE) {
                return true;
            }
        }
        return false;
    };
    var onSeriesMouseMove = function (event) {
        var _a, _b;
        var svgRect = event.target.getBoundingClientRect();
        var offsetX = event.clientX - svgRect.left;
        var closestX = scaledSeries
            .map(function (v) { return v.x; })
            .reduce(function (prev, curr) { return (Math.abs(curr - offsetX) < Math.abs(prev - offsetX) ? curr : prev); }, -Infinity);
        if (isFinite(closestX)) {
            var offsetY_1 = event.clientY - svgRect.top;
            var closestY_1 = scaledSeries
                .filter(function (v) { return v.x === closestX || isYThreshold(v.series); })
                .map(function (v) { return v.y; })
                .reduce(function (prev, curr) { return (Math.abs(curr - offsetY_1) < Math.abs(prev - offsetY_1) ? curr : prev); }, -Infinity);
            if (isFinite(closestY_1) &&
                Math.abs(offsetX - closestX) < MAX_HOVER_MARGIN &&
                Math.abs(offsetY_1 - closestY_1) < MAX_HOVER_MARGIN) {
                var _c = scaledSeries.filter(function (s) { return (s.x === closestX || isYThreshold(s.series)) && s.y === closestY_1; })[0], color = _c.color, datum = _c.datum, series = _c.series;
                highlightPoint({ x: closestX, y: closestY_1, color: color, datum: datum, series: series });
            }
            else {
                var datumX = null;
                for (var _i = 0, scaledSeries_1 = scaledSeries; _i < scaledSeries_1.length; _i++) {
                    var point = scaledSeries_1[_i];
                    if (point.x === closestX) {
                        datumX = (_b = (_a = point.datum) === null || _a === void 0 ? void 0 : _a.x) !== null && _b !== void 0 ? _b : null;
                        break;
                    }
                }
                highlightX({ scaledX: closestX, label: datumX });
            }
        }
    };
    var onGroupMouseMove = function (event) {
        var svgRect = event.target.getBoundingClientRect();
        var offsetX = event.clientX - svgRect.left;
        var offsetY = event.clientY - svgRect.top;
        // If hovering over some group - highlight it.
        for (var groupIndex = 0; groupIndex < barGroups.length; groupIndex++) {
            var _a = barGroups[groupIndex].position, x = _a.x, y = _a.y, width = _a.width, height = _a.height;
            if (x <= offsetX && offsetX <= x + width && y <= offsetY && offsetY <= y + height) {
                highlightGroup(groupIndex);
                return;
            }
        }
        // Otherwise - clear the highlight.
        clearHighlightedSeries();
    };
    var onSVGMouseMove = function (event) {
        if (event.target === plotRef.current.svg && !isHandlersDisabled && !isMouseOverPopover(event)) {
            if (isGroupNavigation) {
                onGroupMouseMove(event);
            }
            else if (scaledSeries.length > 0) {
                onSeriesMouseMove(event);
            }
        }
    };
    var onSVGMouseOut = function (event) {
        if (isHandlersDisabled || isMouseOverPopover(event)) {
            return;
        }
        if (!nodeContains(plotRef.current.svg, event.relatedTarget) ||
            (event.relatedTarget && event.relatedTarget.classList.contains(styles.series))) {
            highlightX(null);
            clearHighlightedSeries();
        }
    };
    var onPopoverLeave = function (event) {
        if (!plotRef.current.svg.contains(event.relatedTarget)) {
            highlightX(null);
            clearHighlightedSeries();
        }
    };
    return { onSVGMouseMove: onSVGMouseMove, onSVGMouseOut: onSVGMouseOut, onPopoverLeave: onPopoverLeave };
}
//# sourceMappingURL=use-mouse-hover.js.map