import { useEffect, useMemo, useRef } from 'react';
import { findClosest, circleIndex } from './utils';
import { nodeContains } from '../../internal/utils/dom';
import { KeyCode } from '../../internal/keycode';
import { useReaction } from './async-store';
import computeChartProps from './compute-chart-props';
import createSeriesDecorator from './create-series-decorator';
import InteractionsStore from './interactions-store';
import { useStableEventHandler } from '../../internal/hooks/use-stable-event-handler';
import { throttle } from '../../internal/utils/throttle';
var MAX_HOVER_MARGIN = 6;
var SVG_HOVER_THROTTLE = 25;
var POPOVER_DEADZONE = 12;
// Represents the core the chart logic, including the model of all allowed user interactions.
export default function useChartModel(_a) {
    var allSeries = _a.externalSeries, series = _a.visibleSeries, setVisibleSeries = _a.setVisibleSeries, highlightedSeries = _a.highlightedSeries, setHighlightedSeries = _a.setHighlightedSeries, xDomain = _a.xDomain, yDomain = _a.yDomain, xScaleType = _a.xScaleType, yScaleType = _a.yScaleType, height = _a.height, width = _a.width, popoverRef = _a.popoverRef;
    // Chart elements refs used in handlers.
    var plotRef = useRef(null);
    var containerRef = useRef(null);
    var verticalMarkerRef = useRef(null);
    var stableSetVisibleSeries = useStableEventHandler(setVisibleSeries);
    var model = useMemo(function () {
        // Compute scales, ticks and two-dimensional plots.
        var computed = computeChartProps({
            series: series,
            xDomain: xDomain,
            yDomain: yDomain,
            xScaleType: xScaleType,
            yScaleType: yScaleType,
            height: height,
            width: width
        });
        // A store for chart interactions that don't require plot recomputation.
        var interactions = new InteractionsStore(series, computed.plot);
        var containsMultipleSeries = interactions.series.length > 1;
        // A series decorator to provide extra props such as color and marker type.
        var getInternalSeries = createSeriesDecorator(allSeries);
        var isMouseOverPopover = function (clientX, clientY) {
            var _a;
            if ((_a = popoverRef.current) === null || _a === void 0 ? void 0 : _a.firstChild) {
                var popoverPosition = popoverRef.current.firstChild.getBoundingClientRect();
                if (clientX > popoverPosition.x - POPOVER_DEADZONE &&
                    clientX < popoverPosition.x + popoverPosition.width + POPOVER_DEADZONE &&
                    clientY > popoverPosition.y - POPOVER_DEADZONE &&
                    clientY < popoverPosition.y + popoverPosition.height + POPOVER_DEADZONE) {
                    return true;
                }
            }
            return false;
        };
        // A Callback for svg mouseover to hover the plot points.
        // Throttling is necessary for a substantially smoother customer experience.
        var onSVGMouseMoveThrottled = throttle(function (clientX, clientY) {
            // No hover logic when the popover is pinned or no data available.
            if (interactions.get().isPopoverPinned ||
                !plotRef.current ||
                interactions.plot.xy.length === 0 ||
                isMouseOverPopover(clientX, clientY)) {
                return;
            }
            var svgRect = plotRef.current.svg.getBoundingClientRect();
            var offsetX = clientX - svgRect.left;
            var offsetY = clientY - svgRect.top;
            var closestX = findClosest(interactions.plot.xy, offsetX, function (xPoints) { return xPoints[0].scaled.x; });
            var closestPoint = findClosest(closestX, offsetY, function (point) { return point.scaled.y1; });
            // If close enough to the point - highlight the point and its column.
            // If not - only highlight the closest column.
            if (Math.abs(offsetX - closestPoint.scaled.x) < MAX_HOVER_MARGIN &&
                Math.abs(offsetY - closestPoint.scaled.y1) < MAX_HOVER_MARGIN) {
                interactions.highlightPoint(closestPoint);
            }
            else {
                interactions.highlightX(closestX);
            }
        }, SVG_HOVER_THROTTLE);
        var onSVGMouseMove = function (_a) {
            var clientX = _a.clientX, clientY = _a.clientY;
            return onSVGMouseMoveThrottled(clientX, clientY);
        };
        // A callback for svg mouseout to clear all highlights.
        var onSVGMouseOut = function (event) {
            // Because the mouseover is throttled, in can occur slightly after the mouseout,
            // neglecting its effect; cancelling the throttled function prevents that.
            onSVGMouseMoveThrottled.cancel();
            // No hover logic when the popover is pinned or mouse is over popover
            if (interactions.get().isPopoverPinned || isMouseOverPopover(event.clientX, event.clientY)) {
                return;
            }
            // Check if the target is contained within svg to allow hovering on the popover body.
            if (!nodeContains(plotRef.current.svg, event.relatedTarget)) {
                interactions.clearHighlightedLegend();
                interactions.clearHighlight();
            }
        };
        // A callback for svg click to pin/unpin the popover.
        var onSVGMouseDown = function (event) {
            interactions.togglePopoverPin();
            event.preventDefault();
        };
        var moveWithinXAxis = function (direction) {
            if (interactions.get().highlightedPoint) {
                return moveWithinSeries(direction);
            }
            else if (containsMultipleSeries) {
                var highlightedX = interactions.get().highlightedX;
                if (highlightedX) {
                    var currentXIndex = highlightedX[0].index.x;
                    var nextXIndex = circleIndex(currentXIndex + direction, [0, interactions.plot.xy.length - 1]);
                    interactions.highlightX(interactions.plot.xy[nextXIndex]);
                }
            }
        };
        // A helper function to highlight the next or previous point within selected series.
        var moveWithinSeries = function (direction) {
            // Can only use motion when a particular point is highlighted.
            var point = interactions.get().highlightedPoint;
            if (!point) {
                return;
            }
            // Take the index of the currently highlighted series.
            var sIndex = point.index.s;
            // Take the incremented(circularly) x-index of the currently highlighted point.
            var xIndex = circleIndex(point.index.x + direction, [0, interactions.plot.xs.length - 1]);
            // Highlight the next point using x:s grouped data.
            interactions.highlightPoint(interactions.plot.xs[xIndex][sIndex]);
        };
        // A helper function to highlight the next or previous point within the selected column.
        var moveBetweenSeries = function (direction) {
            var point = interactions.get().highlightedPoint;
            if (!point) {
                var highlightedX = interactions.get().highlightedX;
                if (highlightedX) {
                    var xIndex_1 = highlightedX[0].index.x;
                    var points = interactions.plot.xy[xIndex_1];
                    var yIndex = direction === 1 ? 0 : points.length - 1;
                    interactions.highlightPoint(points[yIndex]);
                }
                return;
            }
            // Take the index of the currently highlighted column.
            var xIndex = point.index.x;
            var currentYIndex = point.index.y;
            if (containsMultipleSeries &&
                ((currentYIndex === 0 && direction === -1) ||
                    (currentYIndex === interactions.plot.xy[xIndex].length - 1 && direction === 1))) {
                interactions.highlightX(interactions.plot.xy[xIndex]);
            }
            else {
                // Take the incremented(circularly) y-index of the currently highlighted point.
                var nextYIndex = circleIndex(currentYIndex + direction, [0, interactions.plot.xy[xIndex].length - 1]);
                // Highlight the next point using x:y grouped data.
                interactions.highlightPoint(interactions.plot.xy[xIndex][nextYIndex]);
            }
        };
        // A callback for svg keydown to enable motions and popover pin with the keyboard.
        var onSVGKeyDown = function (event) {
            var keyCode = event.keyCode;
            if (keyCode !== KeyCode.up &&
                keyCode !== KeyCode.right &&
                keyCode !== KeyCode.down &&
                keyCode !== KeyCode.left &&
                keyCode !== KeyCode.space &&
                keyCode !== KeyCode.enter) {
                return;
            }
            // Preventing default fixes an issue in Safari+VO when VO additionally interprets arrow keys as its commands.
            event.preventDefault();
            // No keydown logic when the popover is pinned.
            if (interactions.get().isPopoverPinned) {
                return;
            }
            // Move up/down.
            if (keyCode === KeyCode.down || keyCode === KeyCode.up) {
                moveBetweenSeries(keyCode === KeyCode.down ? -1 : 1);
            }
            // Move left/right.
            else if (keyCode === KeyCode.left || keyCode === KeyCode.right) {
                moveWithinXAxis(keyCode === KeyCode.right ? 1 : -1);
            }
            // Pin popover.
            else if (keyCode === KeyCode.enter || keyCode === KeyCode.space) {
                interactions.pinPopover();
            }
        };
        var highlightFirstX = function () {
            interactions.highlightX(interactions.plot.xy[0]);
        };
        // A callback for svg focus to highlight series.
        var onSVGFocus = function (_event, trigger) {
            // When focus is caused by a click event nothing is expected as clicks are handled separately.
            if (trigger === 'keyboard') {
                var _a = interactions.get(), highlightedX = _a.highlightedX, highlightedPoint = _a.highlightedPoint, highlightedSeries_1 = _a.highlightedSeries, legendSeries = _a.legendSeries;
                if (containsMultipleSeries && !highlightedX && !highlightedPoint && !highlightedSeries_1 && !legendSeries) {
                    highlightFirstX();
                }
                else if (!highlightedX) {
                    interactions.highlightFirstPoint();
                }
            }
        };
        // A callback for svg blur to clear all highlights unless the popover is pinned.
        var onSVGBlur = function () {
            // Pinned popover stays pinned even if the focus is lost.
            // If blur is not caused by the popover, forget the previously highlighted point.
            if (!interactions.get().isPopoverPinned) {
                interactions.clearHighlight();
            }
        };
        var onFilterSeries = function (series) {
            stableSetVisibleSeries(series);
        };
        var onLegendHighlight = function (series) {
            interactions.highlightSeries(series);
        };
        var onPopoverDismiss = function (outsideClick) {
            interactions.unpinPopover();
            // Return focus back to the application or plot (when no point is highlighted).
            if (!outsideClick) {
                // The delay is needed to bypass focus events caused by click or keypress needed to unpin the popover.
                setTimeout(function () {
                    if (interactions.get().highlightedPoint || interactions.get().highlightedX) {
                        plotRef.current.focusApplication();
                    }
                    else {
                        interactions.clearHighlight();
                        plotRef.current.focusPlot();
                    }
                }, 0);
            }
        };
        var onContainerBlur = function () {
            interactions.clearState();
        };
        var onDocumentKeyDown = function (event) {
            if (event.key === 'Escape') {
                interactions.clearHighlight();
                interactions.clearHighlightedLegend();
            }
        };
        var onPopoverLeave = function (event) {
            if (plotRef.current.svg.contains(event.relatedTarget) || interactions.get().isPopoverPinned) {
                return;
            }
            interactions.clearHighlight();
            interactions.clearHighlightedLegend();
        };
        return {
            width: width,
            height: height,
            series: series,
            allSeries: allSeries,
            getInternalSeries: getInternalSeries,
            computed: computed,
            interactions: interactions,
            handlers: {
                onSVGMouseMove: onSVGMouseMove,
                onSVGMouseOut: onSVGMouseOut,
                onSVGMouseDown: onSVGMouseDown,
                onSVGKeyDown: onSVGKeyDown,
                onSVGFocus: onSVGFocus,
                onSVGBlur: onSVGBlur,
                onFilterSeries: onFilterSeries,
                onLegendHighlight: onLegendHighlight,
                onPopoverDismiss: onPopoverDismiss,
                onContainerBlur: onContainerBlur,
                onDocumentKeyDown: onDocumentKeyDown,
                onPopoverLeave: onPopoverLeave
            },
            refs: {
                plot: plotRef,
                container: containerRef,
                verticalMarker: verticalMarkerRef,
                popoverRef: popoverRef
            }
        };
    }, [allSeries, series, xDomain, yDomain, xScaleType, yScaleType, height, width, stableSetVisibleSeries, popoverRef]);
    // Notify client when series highlight change.
    useReaction(model.interactions, function (state) { return state.highlightedSeries; }, setHighlightedSeries);
    // Update interactions store when series highlight in a controlled way.
    useEffect(function () {
        if (highlightedSeries !== model.interactions.get().highlightedSeries) {
            model.interactions.highlightSeries(highlightedSeries);
        }
    }, [model, highlightedSeries]);
    return model;
}
//# sourceMappingURL=use-chart-model.js.map