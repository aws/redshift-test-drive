import { __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { nodeContains } from '../internal/utils/dom';
import { useVisualRefresh } from '../internal/hooks/use-visual-mode';
import { getXTickCount, getYTickCount, createXTicks, createYTicks } from '../internal/components/cartesian-chart/ticks';
import ChartPlot from '../internal/components/chart-plot';
import AxisLabel from '../internal/components/cartesian-chart/axis-label';
import LabelsMeasure from '../internal/components/cartesian-chart/labels-measure';
import LeftLabels from '../internal/components/cartesian-chart/left-labels';
import BottomLabels from '../internal/components/cartesian-chart/bottom-labels';
import VerticalGridLines from '../internal/components/cartesian-chart/vertical-grid-lines';
import EmphasizedBaseline from '../internal/components/cartesian-chart/emphasized-baseline';
import HighlightedPoint from '../internal/components/cartesian-chart/highlighted-point';
import VerticalMarker from '../internal/components/cartesian-chart/vertical-marker';
import { ChartScale, NumericChartScale } from '../internal/components/cartesian-chart/scales';
import ChartPopover from './chart-popover';
import { computeDomainX, computeDomainY } from './domain';
import { isXThreshold } from './utils';
import makeScaledSeries from './make-scaled-series';
import makeScaledBarGroups from './make-scaled-bar-groups';
import formatHighlighted from './format-highlighted';
import DataSeries from './data-series';
import BarGroups from './bar-groups';
import { useMouseHover } from './hooks/use-mouse-hover';
import { useNavigation } from './hooks/use-navigation';
import { usePopover } from './hooks/use-popover';
import styles from './styles.css.js';
import useContainerWidth from '../internal/utils/use-container-width';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
var LEFT_LABELS_MARGIN = 16;
var BOTTOM_LABELS_OFFSET = 12;
export default function ChartContainer(_a) {
    var _b, _c;
    var plotHeight = _a.height, series = _a.series, visibleSeries = _a.visibleSeries, highlightedSeries = _a.highlightedSeries, onHighlightChange = _a.onHighlightChange, highlightedPoint = _a.highlightedPoint, setHighlightedPoint = _a.setHighlightedPoint, highlightedGroupIndex = _a.highlightedGroupIndex, setHighlightedGroupIndex = _a.setHighlightedGroupIndex, _d = _a.detailPopoverSize, detailPopoverSize = _d === void 0 ? 'medium' : _d, _e = _a.stackedBars, stackedBars = _e === void 0 ? false : _e, _f = _a.horizontalBars, horizontalBars = _f === void 0 ? false : _f, xScaleType = _a.xScaleType, yScaleType = _a.yScaleType, xTickFormatter = _a.xTickFormatter, yTickFormatter = _a.yTickFormatter, emphasizeBaselineAxis = _a.emphasizeBaselineAxis, xTitle = _a.xTitle, yTitle = _a.yTitle, ariaLabel = _a.ariaLabel, ariaLabelledby = _a.ariaLabelledby, ariaDescription = _a.ariaDescription, _g = _a.i18nStrings, i18nStrings = _g === void 0 ? {} : _g, plotContainerRef = _a.plotContainerRef, props = __rest(_a, ["height", "series", "visibleSeries", "highlightedSeries", "onHighlightChange", "highlightedPoint", "setHighlightedPoint", "highlightedGroupIndex", "setHighlightedGroupIndex", "detailPopoverSize", "stackedBars", "horizontalBars", "xScaleType", "yScaleType", "xTickFormatter", "yTickFormatter", "emphasizeBaselineAxis", "xTitle", "yTitle", "ariaLabel", "ariaLabelledby", "ariaDescription", "i18nStrings", "plotContainerRef"]);
    var plotRef = useRef(null);
    var verticalMarkerRef = useRef(null);
    var _h = useState(0), leftLabelsWidth = _h[0], setLeftLabelsWidth = _h[1];
    var _j = useState(0), bottomLabelsHeight = _j[0], setBottomLabelsHeight = _j[1];
    var _k = useState(null), verticalMarkerX = _k[0], setVerticalMarkerX = _k[1];
    var _l = useContainerWidth(500), containerWidth = _l[0], containerMeasureRef = _l[1];
    var plotWidth = containerWidth ? containerWidth - leftLabelsWidth - LEFT_LABELS_MARGIN : 500;
    var containerRefObject = useRef(null);
    var containerRef = useMergeRefs(containerMeasureRef, containerRefObject);
    var popoverRef = useRef(null);
    var isRefresh = useVisualRefresh();
    var linesOnly = series.every(function (_a) {
        var series = _a.series;
        return series.type === 'line' || series.type === 'threshold';
    });
    var xDomain = (props.xDomain || computeDomainX(series, xScaleType));
    var yDomain = (props.yDomain || computeDomainY(series, yScaleType, stackedBars));
    var xTickCount = getXTickCount(plotWidth);
    var yTickCount = getYTickCount(plotHeight);
    var rangeBottomTop = [0, plotHeight];
    var rangeTopBottom = [plotHeight, 0];
    var rangeLeftRight = [0, plotWidth];
    var xScale = new ChartScale(xScaleType, xDomain, horizontalBars ? rangeBottomTop : rangeLeftRight, linesOnly);
    var yScale = new NumericChartScale(yScaleType, yDomain, horizontalBars ? rangeLeftRight : rangeTopBottom, props.yDomain ? null : yTickCount);
    var xTicks = createXTicks(xScale, xTickCount);
    var yTicks = createYTicks(yScale, yTickCount);
    /**
     * Interactions
     */
    var highlightedPointRef = useRef(null);
    var highlightedGroupRef = useRef(null);
    var _m = useState(false), isPlotFocused = _m[0], setPlotFocused = _m[1];
    // Some chart components are rendered against "x" or "y" axes,
    // When "horizontalBars" is enabled, the axes are inverted.
    var x = !horizontalBars ? 'x' : 'y';
    var y = !horizontalBars ? 'y' : 'x';
    var xy = {
        ticks: { x: xTicks, y: yTicks },
        scale: { x: xScale, y: yScale },
        tickFormatter: { x: xTickFormatter, y: yTickFormatter },
        title: { x: xTitle, y: yTitle },
        ariaRoleDescription: { x: i18nStrings.xAxisAriaRoleDescription, y: i18nStrings.yAxisAriaRoleDescription }
    };
    var scaledSeries = makeScaledSeries(visibleSeries, xScale, yScale);
    var barGroups = makeScaledBarGroups(visibleSeries, xScale, plotWidth, plotHeight, y);
    var _o = usePopover(), isPopoverOpen = _o.isPopoverOpen, isPopoverPinned = _o.isPopoverPinned, showPopover = _o.showPopover, pinPopover = _o.pinPopover, dismissPopover = _o.dismissPopover;
    // Allows to add a delay between popover is dismissed and handlers are enabled to prevent immediate popover reopening.
    var _p = useState(!isPopoverPinned), isHandlersDisabled = _p[0], setHandlersDisabled = _p[1];
    useEffect(function () {
        if (isPopoverPinned) {
            setHandlersDisabled(true);
        }
        else {
            var timeoutId_1 = setTimeout(function () { return setHandlersDisabled(false); }, 25);
            return function () { return clearTimeout(timeoutId_1); };
        }
    }, [isPopoverPinned]);
    var highlightSeries = useCallback(function (series) {
        if (series !== highlightedSeries) {
            onHighlightChange(series);
        }
    }, [highlightedSeries, onHighlightChange]);
    var highlightPoint = useCallback(function (point) {
        var _a, _b;
        setHighlightedGroupIndex(null);
        setHighlightedPoint(point);
        if (point) {
            highlightSeries(point.series);
            setVerticalMarkerX({
                scaledX: point.x,
                label: (_b = (_a = point.datum) === null || _a === void 0 ? void 0 : _a.x) !== null && _b !== void 0 ? _b : null
            });
        }
    }, [setHighlightedGroupIndex, setHighlightedPoint, highlightSeries]);
    var clearAllHighlights = useCallback(function () {
        setHighlightedPoint(null);
        highlightSeries(null);
        setHighlightedGroupIndex(null);
    }, [highlightSeries, setHighlightedGroupIndex, setHighlightedPoint]);
    // Highlight all points at a given X in a line chart
    var highlightX = useCallback(function (marker) {
        if (marker) {
            clearAllHighlights();
        }
        setVerticalMarkerX(marker);
    }, [clearAllHighlights]);
    // Highlight all points and bars at a given X index in a mixed line and bar chart
    var highlightGroup = useCallback(function (groupIndex) {
        highlightSeries(null);
        setHighlightedPoint(null);
        setHighlightedGroupIndex(groupIndex);
    }, [highlightSeries, setHighlightedPoint, setHighlightedGroupIndex]);
    var clearHighlightedSeries = useCallback(function () {
        clearAllHighlights();
        dismissPopover();
    }, [dismissPopover, clearAllHighlights]);
    var _q = useNavigation({
        series: series,
        visibleSeries: visibleSeries,
        scaledSeries: scaledSeries,
        barGroups: barGroups,
        xScale: xScale,
        yScale: yScale,
        highlightedPoint: highlightedPoint,
        highlightedGroupIndex: highlightedGroupIndex,
        highlightedSeries: highlightedSeries,
        isHandlersDisabled: isHandlersDisabled,
        pinPopover: pinPopover,
        highlightSeries: highlightSeries,
        highlightGroup: highlightGroup,
        highlightPoint: highlightPoint,
        highlightX: highlightX,
        clearHighlightedSeries: clearHighlightedSeries,
        verticalMarkerX: verticalMarkerX
    }), isGroupNavigation = _q.isGroupNavigation, handlers = __rest(_q, ["isGroupNavigation"]);
    var _r = useMouseHover({
        scaledSeries: scaledSeries,
        barGroups: barGroups,
        plotRef: plotRef,
        popoverRef: popoverRef,
        highlightPoint: highlightPoint,
        highlightGroup: highlightGroup,
        clearHighlightedSeries: clearHighlightedSeries,
        isGroupNavigation: isGroupNavigation,
        isHandlersDisabled: isHandlersDisabled,
        highlightX: highlightX
    }), onSVGMouseMove = _r.onSVGMouseMove, onSVGMouseOut = _r.onSVGMouseOut, onPopoverLeave = _r.onPopoverLeave;
    // There are multiple ways to indicate what X is selected.
    // TODO: make a uniform verticalMarkerX state to fit all use-cases.
    var highlightedX = useMemo(function () {
        var _a, _b;
        if (highlightedGroupIndex !== null) {
            return barGroups[highlightedGroupIndex].x;
        }
        if (verticalMarkerX !== null) {
            return verticalMarkerX.label;
        }
        return (_b = (_a = highlightedPoint === null || highlightedPoint === void 0 ? void 0 : highlightedPoint.datum) === null || _a === void 0 ? void 0 : _a.x) !== null && _b !== void 0 ? _b : null;
    }, [highlightedPoint, verticalMarkerX, highlightedGroupIndex, barGroups]);
    useEffect(function () {
        var onKeyDown = function (event) {
            if (event.key === 'Escape') {
                dismissPopover();
            }
        };
        document.addEventListener('keydown', onKeyDown);
        return function () { return document.removeEventListener('keydown', onKeyDown); };
    }, [dismissPopover]);
    useLayoutEffect(function () {
        if (highlightedX !== null || highlightedPoint !== null) {
            showPopover();
        }
    }, [highlightedX, highlightedPoint, showPopover]);
    var onPopoverDismiss = function (outsideClick) {
        dismissPopover();
        if (!outsideClick) {
            // The delay is needed to bypass focus events caused by click or keypress needed to unpin the popover.
            setTimeout(function () {
                var _a, _b;
                var isSomeInnerElementFocused = highlightedPoint || highlightedGroupIndex !== null || verticalMarkerX;
                if (isSomeInnerElementFocused) {
                    (_a = plotRef.current) === null || _a === void 0 ? void 0 : _a.focusApplication();
                }
                else {
                    (_b = plotRef.current) === null || _b === void 0 ? void 0 : _b.focusPlot();
                }
            }, 0);
        }
        else {
            clearAllHighlights();
            setVerticalMarkerX(null);
        }
    };
    var onSVGMouseDown = function (e) {
        if (isPopoverOpen) {
            if (isPopoverPinned) {
                dismissPopover();
            }
            else {
                pinPopover();
                e.preventDefault();
            }
        }
        else {
            showPopover();
        }
    };
    var onSVGFocus = function (event, trigger) {
        setPlotFocused(true);
        if (trigger === 'keyboard') {
            handlers.onFocus();
        }
        else {
            // noop: clicks are handled separately
        }
    };
    var onSVGBlur = function (event) {
        var _a;
        setPlotFocused(false);
        var blurTarget = event.relatedTarget || event.target;
        if (blurTarget === null ||
            !(blurTarget instanceof Element) ||
            !nodeContains(containerRefObject.current, blurTarget)) {
            setHighlightedPoint(null);
            setVerticalMarkerX(null);
            if (!((_a = plotContainerRef === null || plotContainerRef === void 0 ? void 0 : plotContainerRef.current) === null || _a === void 0 ? void 0 : _a.contains(blurTarget))) {
                clearHighlightedSeries();
            }
            if (isPopoverOpen && !isPopoverPinned) {
                dismissPopover();
            }
        }
    };
    var onSVGKeyDown = handlers.onKeyDown;
    var xOffset = xScale.isCategorical() ? Math.max(0, xScale.d3Scale.bandwidth() - 1) / 2 : 0;
    var verticalLineX = null;
    if (verticalMarkerX !== null) {
        verticalLineX = verticalMarkerX.scaledX;
    }
    else if (isGroupNavigation && highlightedGroupIndex !== null) {
        var x_1 = (_b = xScale.d3Scale(barGroups[highlightedGroupIndex].x)) !== null && _b !== void 0 ? _b : null;
        if (x_1 !== null) {
            verticalLineX = xOffset + x_1;
        }
    }
    var point = useMemo(function () {
        return highlightedPoint
            ? {
                key: "".concat(highlightedPoint.x, "-").concat(highlightedPoint.y),
                x: highlightedPoint.x,
                y: highlightedPoint.y,
                color: highlightedPoint.color
            }
            : null;
    }, [highlightedPoint]);
    var verticalMarkers = useMemo(function () {
        return verticalLineX !== null
            ? scaledSeries
                .filter(function (_a) {
                var x = _a.x, y = _a.y;
                return (x === verticalLineX || isNaN(x)) && !isNaN(y);
            })
                .map(function (_a, index) {
                var x = _a.x, y = _a.y, color = _a.color;
                return ({
                    key: "".concat(index, "-").concat(x, "-").concat(y),
                    x: !horizontalBars ? verticalLineX || 0 : y,
                    y: !horizontalBars ? y : verticalLineX || 0,
                    color: color
                });
            })
            : [];
    }, [scaledSeries, verticalLineX, horizontalBars]);
    var highlightedElementRef = isGroupNavigation
        ? highlightedGroupRef
        : highlightedPoint
            ? highlightedPointRef
            : verticalMarkerRef;
    var highlightDetails = useMemo(function () {
        if (highlightedX === null) {
            return null;
        }
        // When series point is highlighted show the corresponding series and matching x-thresholds.
        if (highlightedPoint) {
            var seriesToShow = visibleSeries.filter(function (series) { return series.series === (highlightedPoint === null || highlightedPoint === void 0 ? void 0 : highlightedPoint.series) || isXThreshold(series.series); });
            return formatHighlighted(highlightedX, seriesToShow, xTickFormatter);
        }
        // Otherwise - show all visible series details.
        return formatHighlighted(highlightedX, visibleSeries, xTickFormatter);
    }, [highlightedX, highlightedPoint, visibleSeries, xTickFormatter]);
    var activeAriaLabel = useMemo(function () {
        return highlightDetails
            ? "".concat(highlightDetails.position, ", ").concat(highlightDetails.details.map(function (d) { return d.key + ' ' + d.value; }).join(','))
            : '';
    }, [highlightDetails]);
    // Live region is used when nothing is focused e.g. when hovering.
    var activeLiveRegion = activeAriaLabel && !highlightedPoint && highlightedGroupIndex === null ? activeAriaLabel : '';
    var isLineXKeyboardFocused = isPlotFocused && !highlightedPoint && verticalMarkerX;
    return (React.createElement("div", { className: styles['chart-container'], ref: containerRef },
        React.createElement(AxisLabel, { axis: y, position: "left", title: xy.title[y] }),
        React.createElement("div", { className: styles['chart-container__horizontal'] },
            React.createElement(LabelsMeasure, { ticks: xy.ticks[y], scale: xy.scale[y], tickFormatter: xy.tickFormatter[y], autoWidth: setLeftLabelsWidth }),
            React.createElement("div", { className: styles['chart-container__vertical'] },
                React.createElement(ChartPlot, { ref: plotRef, width: plotWidth, height: plotHeight, offsetBottom: bottomLabelsHeight, isClickable: isPopoverOpen && !isPopoverPinned, ariaLabel: ariaLabel, ariaLabelledby: ariaLabelledby, ariaDescription: ariaDescription, ariaRoleDescription: i18nStrings === null || i18nStrings === void 0 ? void 0 : i18nStrings.chartAriaRoleDescription, ariaLiveRegion: activeLiveRegion, activeElementRef: highlightedElementRef, activeElementKey: isPlotFocused &&
                        ((_c = highlightedGroupIndex === null || highlightedGroupIndex === void 0 ? void 0 : highlightedGroupIndex.toString()) !== null && _c !== void 0 ? _c : (isLineXKeyboardFocused ? "point-index-".concat(handlers.xIndex) : point === null || point === void 0 ? void 0 : point.key)), activeElementFocusOffset: isGroupNavigation ? 0 : isLineXKeyboardFocused ? { x: 8, y: 0 } : 3, onMouseMove: onSVGMouseMove, onMouseOut: onSVGMouseOut, onMouseDown: onSVGMouseDown, onFocus: onSVGFocus, onBlur: onSVGBlur, onKeyDown: onSVGKeyDown },
                    React.createElement(LeftLabels, { axis: y, ticks: xy.ticks[y], scale: xy.scale[y], tickFormatter: xy.tickFormatter[y], title: xy.title[y], ariaRoleDescription: xy.ariaRoleDescription[y], width: plotWidth, height: plotHeight }),
                    horizontalBars && React.createElement(VerticalGridLines, { scale: yScale, ticks: yTicks, height: plotHeight }),
                    emphasizeBaselineAxis && linesOnly && (React.createElement(EmphasizedBaseline, { axis: x, scale: yScale, width: plotWidth, height: plotHeight })),
                    React.createElement(DataSeries, { axis: x, plotWidth: plotWidth, plotHeight: plotHeight, highlightedSeries: highlightedSeries !== null && highlightedSeries !== void 0 ? highlightedSeries : null, highlightedGroupIndex: highlightedGroupIndex, stackedBars: stackedBars, isGroupNavigation: isGroupNavigation, visibleSeries: visibleSeries, xScale: xScale, yScale: yScale }),
                    emphasizeBaselineAxis && !linesOnly && (React.createElement(EmphasizedBaseline, { axis: x, scale: yScale, width: plotWidth, height: plotHeight })),
                    React.createElement(VerticalMarker, { key: verticalLineX || '', height: plotHeight, showPoints: highlightedPoint === null, showLine: !isGroupNavigation, points: verticalMarkers, ref: verticalMarkerRef }),
                    highlightedPoint && (React.createElement(HighlightedPoint, { ref: highlightedPointRef, point: point, role: "button", ariaLabel: activeAriaLabel, ariaHasPopup: true, ariaExpanded: isPopoverPinned })),
                    isGroupNavigation && xScale.isCategorical() && (React.createElement(BarGroups, { ariaLabel: activeAriaLabel, isRefresh: isRefresh, isPopoverPinned: isPopoverPinned, barGroups: barGroups, highlightedGroupIndex: highlightedGroupIndex, highlightedGroupRef: highlightedGroupRef })),
                    React.createElement(BottomLabels, { axis: x, ticks: xy.ticks[x], scale: xy.scale[x], tickFormatter: xy.tickFormatter[x], title: xy.title[x], ariaRoleDescription: xy.ariaRoleDescription[x], height: plotHeight, width: plotWidth, offsetLeft: leftLabelsWidth + BOTTOM_LABELS_OFFSET, offsetRight: BOTTOM_LABELS_OFFSET, autoHeight: setBottomLabelsHeight })),
                React.createElement(AxisLabel, { axis: x, position: "bottom", title: xy.title[x] })),
            React.createElement(ChartPopover, { ref: popoverRef, containerRef: containerRefObject, trackRef: highlightedElementRef, isOpen: isPopoverOpen, isPinned: isPopoverPinned, highlightDetails: highlightDetails, onDismiss: onPopoverDismiss, size: detailPopoverSize, dismissAriaLabel: i18nStrings.detailPopoverDismissAriaLabel, onMouseLeave: onPopoverLeave }))));
}
//# sourceMappingURL=chart-container.js.map