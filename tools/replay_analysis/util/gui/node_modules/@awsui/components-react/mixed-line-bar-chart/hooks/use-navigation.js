import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useCallback, useMemo, useState } from 'react';
import { KeyCode } from '../../internal/keycode';
import { findNavigableSeries, isXThreshold, isYThreshold, nextValidDomainIndex } from '../utils';
export function useNavigation(_a) {
    var series = _a.series, visibleSeries = _a.visibleSeries, scaledSeries = _a.scaledSeries, barGroups = _a.barGroups, xScale = _a.xScale, yScale = _a.yScale, highlightedPoint = _a.highlightedPoint, highlightedGroupIndex = _a.highlightedGroupIndex, highlightedSeries = _a.highlightedSeries, isHandlersDisabled = _a.isHandlersDisabled, pinPopover = _a.pinPopover, highlightSeries = _a.highlightSeries, highlightGroup = _a.highlightGroup, highlightPoint = _a.highlightPoint, highlightX = _a.highlightX, verticalMarkerX = _a.verticalMarkerX;
    var _b = useState(null), targetX = _b[0], setTargetX = _b[1];
    var _c = useState(0), xIndex = _c[0], setXIndex = _c[1];
    // There are two different types of navigation:
    // 1) Group navigation for any chart that contains a bar series
    // 2) Line navigation for any chart that only contains lines and thresholds
    var isGroupNavigation = useMemo(function () { return visibleSeries.some(function (_a) {
        var series = _a.series;
        return series.type === 'bar';
    }); }, [visibleSeries]);
    // Make a list of series that can be navigated between. Bar series are treated as one.
    var navigableSeries = useMemo(function () { return findNavigableSeries(visibleSeries); }, [visibleSeries]).navigableSeries;
    var containsMultipleSeries = navigableSeries.length > 1;
    var onBarGroupFocus = function () {
        var groupIndex = highlightedGroupIndex !== null && highlightedGroupIndex !== void 0 ? highlightedGroupIndex : 0;
        setTargetX(xScale.domain[groupIndex]);
        highlightGroup(groupIndex);
    };
    var onLineFocus = function () {
        if (verticalMarkerX === null) {
            if (containsMultipleSeries) {
                moveToLineGroupIndex(0);
            }
            else {
                moveBetweenSeries(0);
            }
        }
    };
    var onFocus = function () {
        if (isGroupNavigation) {
            onBarGroupFocus();
        }
        else {
            onLineFocus();
        }
    };
    // Returns all the unique X coordinates in scaledSeries.
    // Assumes scaledSeries is sorted by `x`.
    var allUniqueX = useMemo(function () {
        var result = [];
        for (var i = 0; i < scaledSeries.length; i += 1) {
            var point = scaledSeries[i];
            if (point !== undefined && (!result.length || result[result.length - 1].scaledX !== point.x)) {
                result.push({ scaledX: point.x, datum: point.datum });
            }
        }
        return result;
    }, [scaledSeries]);
    var moveBetweenSeries = useCallback(function (direction) {
        var _a, _b, _c, _d;
        if (isGroupNavigation) {
            return;
        }
        var xOffset = xScale.isCategorical() ? Math.max(0, xScale.d3Scale.bandwidth() - 1) / 2 : 0;
        var MAX_SERIES_INDEX = navigableSeries.length - 1;
        // Find the index of the currently highlighted series (if any)
        var previousSeriesIndex = -1;
        if (highlightedSeries) {
            previousSeriesIndex = navigableSeries.indexOf(highlightedSeries);
        }
        // Move forwards or backwards to the new series
        // If index === -1, show all data points from all series at the given X instead of one single series
        var firstPossibleIndex = containsMultipleSeries ? -1 : 0;
        var nextSeriesIndex = 0;
        if (previousSeriesIndex !== null) {
            nextSeriesIndex = previousSeriesIndex + direction;
            if (nextSeriesIndex > MAX_SERIES_INDEX) {
                nextSeriesIndex = firstPossibleIndex;
            }
            else if (nextSeriesIndex < firstPossibleIndex) {
                nextSeriesIndex = MAX_SERIES_INDEX;
            }
        }
        if (nextSeriesIndex === -1) {
            highlightSeries(null);
            highlightPoint(null);
            return;
        }
        var nextSeries = navigableSeries[nextSeriesIndex];
        var nextInternalSeries = series.filter(function (_a) {
            var series = _a.series;
            return series === nextSeries;
        })[0];
        // 2. Find point in the next series
        var targetXPoint = ((_a = xScale.d3Scale(targetX)) !== null && _a !== void 0 ? _a : NaN) + xOffset;
        if (!isFinite(targetXPoint)) {
            targetXPoint = 0;
        }
        if (nextSeries.type === 'line') {
            var nextScaledSeries = scaledSeries.filter(function (it) { return it.series === nextSeries; });
            var closestNextSeriesPoint = nextScaledSeries.reduce(function (prev, curr) { return (Math.abs(curr.x - targetXPoint) < Math.abs(prev.x - targetXPoint) ? curr : prev); }, { x: -Infinity, y: -Infinity });
            highlightPoint(__assign(__assign({}, closestNextSeriesPoint), { color: nextInternalSeries.color, series: nextSeries }));
        }
        else if (isYThreshold(nextSeries)) {
            var scaledTargetIndex = scaledSeries.map(function (it) { var _a; return ((_a = it.datum) === null || _a === void 0 ? void 0 : _a.x) || null; }).indexOf(targetX);
            highlightPoint({
                x: targetXPoint,
                y: (_b = yScale.d3Scale(nextSeries.y)) !== null && _b !== void 0 ? _b : NaN,
                color: nextInternalSeries.color,
                series: nextSeries,
                datum: (_c = scaledSeries[scaledTargetIndex]) === null || _c === void 0 ? void 0 : _c.datum
            });
        }
        else if (isXThreshold(nextSeries)) {
            highlightPoint({
                x: (_d = xScale.d3Scale(nextSeries.x)) !== null && _d !== void 0 ? _d : NaN,
                y: yScale.d3Scale.range()[0],
                color: nextInternalSeries.color,
                series: nextSeries,
                datum: { x: nextSeries.x, y: NaN }
            });
        }
    }, [
        isGroupNavigation,
        xScale,
        navigableSeries,
        highlightedSeries,
        containsMultipleSeries,
        highlightSeries,
        highlightPoint,
        series,
        targetX,
        scaledSeries,
        yScale,
    ]);
    var moveWithinSeries = useCallback(function (direction) {
        var _a;
        var series = highlightedSeries || visibleSeries[0].series;
        if (series.type === 'line' || isYThreshold(series)) {
            var targetScaledSeries = scaledSeries.filter(function (it) { return it.series === series; });
            var previousPoint = highlightedPoint || targetScaledSeries[0];
            var indexOfPreviousPoint = targetScaledSeries.map(function (it) { return it.x; }).indexOf(previousPoint.x);
            var nextPointIndex = circleIndex(indexOfPreviousPoint + direction, [0, targetScaledSeries.length - 1]);
            var nextPoint = targetScaledSeries[nextPointIndex];
            setTargetX(((_a = nextPoint.datum) === null || _a === void 0 ? void 0 : _a.x) || null);
            setXIndex(nextPointIndex);
            highlightPoint(nextPoint);
        }
        else if (series.type === 'bar') {
            var xDomain = xScale.domain;
            var MAX_GROUP_INDEX = xDomain.length - 1;
            var nextGroupIndex = 0;
            if (highlightedGroupIndex !== null) {
                // find next group
                nextGroupIndex = highlightedGroupIndex + direction;
                if (nextGroupIndex > MAX_GROUP_INDEX) {
                    nextGroupIndex = 0;
                }
                else if (nextGroupIndex < 0) {
                    nextGroupIndex = MAX_GROUP_INDEX;
                }
            }
            var nextDomainIndex = nextValidDomainIndex(nextGroupIndex, barGroups, direction);
            setTargetX(xDomain[nextDomainIndex]);
            highlightGroup(nextDomainIndex);
        }
    }, [
        highlightedSeries,
        visibleSeries,
        scaledSeries,
        highlightedPoint,
        highlightPoint,
        xScale.domain,
        highlightedGroupIndex,
        barGroups,
        highlightGroup,
    ]);
    var moveToLineGroupIndex = useCallback(function (index) {
        var _a, _b, _c, _d;
        var point = allUniqueX[index];
        setXIndex(index);
        setTargetX(((_a = point.datum) === null || _a === void 0 ? void 0 : _a.x) || null);
        highlightX({ scaledX: (_b = point === null || point === void 0 ? void 0 : point.scaledX) !== null && _b !== void 0 ? _b : null, label: (_d = (_c = point.datum) === null || _c === void 0 ? void 0 : _c.x) !== null && _d !== void 0 ? _d : null });
    }, [allUniqueX, highlightX]);
    var moveWithinXAxis = useCallback(function (direction) {
        if (highlightedSeries || isGroupNavigation) {
            moveWithinSeries(direction);
        }
        else {
            var nextPointGroupIndex = circleIndex(xIndex + direction, [0, allUniqueX.length - 1]);
            moveToLineGroupIndex(nextPointGroupIndex);
        }
    }, [highlightedSeries, isGroupNavigation, moveWithinSeries, xIndex, allUniqueX.length, moveToLineGroupIndex]);
    var onKeyDown = useCallback(function (event) {
        var keyCode = event.keyCode;
        if (keyCode !== KeyCode.up &&
            keyCode !== KeyCode.right &&
            keyCode !== KeyCode.down &&
            keyCode !== KeyCode.left &&
            keyCode !== KeyCode.space &&
            keyCode !== KeyCode.enter) {
            return;
        }
        event.preventDefault();
        if (isHandlersDisabled) {
            return;
        }
        if (keyCode === KeyCode.down || keyCode === KeyCode.up) {
            moveBetweenSeries(keyCode === KeyCode.down ? 1 : -1);
        }
        else if (keyCode === KeyCode.left || keyCode === KeyCode.right) {
            moveWithinXAxis(keyCode === KeyCode.right ? 1 : -1);
        }
        else if (keyCode === KeyCode.enter || keyCode === KeyCode.space) {
            pinPopover();
        }
    }, [isHandlersDisabled, moveBetweenSeries, moveWithinXAxis, pinPopover]);
    return { isGroupNavigation: isGroupNavigation, onFocus: onFocus, onKeyDown: onKeyDown, xIndex: xIndex };
}
// Returns given index if it is in range or the opposite range boundary otherwise.
function circleIndex(index, _a) {
    var from = _a[0], to = _a[1];
    if (index < from) {
        return to;
    }
    if (index > to) {
        return from;
    }
    return index;
}
//# sourceMappingURL=use-navigation.js.map