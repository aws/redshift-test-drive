import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useRef, memo } from 'react';
import useFocusVisible from '../../hooks/focus-visible';
import InternalBox from '../../../box/internal';
import { KeyCode } from '../../keycode';
import SeriesMarker from '../chart-series-marker';
import styles from './styles.css.js';
export default memo(ChartLegend);
function ChartLegend(_a) {
    var series = _a.series, onHighlightChange = _a.onHighlightChange, highlightedSeries = _a.highlightedSeries, legendTitle = _a.legendTitle, ariaLabel = _a.ariaLabel, plotContainerRef = _a.plotContainerRef;
    var focusVisible = useFocusVisible();
    var containerRef = useRef(null);
    var segmentsRef = useRef([]);
    var highlightedSeriesIndex = findSeriesIndex(series, highlightedSeries);
    var highlightLeft = function () {
        var _a;
        var currentIndex = highlightedSeriesIndex !== null && highlightedSeriesIndex !== void 0 ? highlightedSeriesIndex : 0;
        var nextIndex = currentIndex - 1 >= 0 ? currentIndex - 1 : series.length - 1;
        (_a = segmentsRef.current[nextIndex]) === null || _a === void 0 ? void 0 : _a.focus();
    };
    var highlightRight = function () {
        var _a;
        var currentIndex = highlightedSeriesIndex !== null && highlightedSeriesIndex !== void 0 ? highlightedSeriesIndex : 0;
        var nextIndex = currentIndex + 1 < series.length ? currentIndex + 1 : 0;
        (_a = segmentsRef.current[nextIndex]) === null || _a === void 0 ? void 0 : _a.focus();
    };
    var handleKeyPress = function (event) {
        if (event.keyCode === KeyCode.right || event.keyCode === KeyCode.left) {
            // Preventing default fixes an issue in Safari+VO when VO additionally interprets arrow keys as its commands.
            event.preventDefault();
            switch (event.keyCode) {
                case KeyCode.left:
                    return highlightLeft();
                case KeyCode.right:
                    return highlightRight();
                default:
                    return;
            }
        }
    };
    var handleSelection = function (index) {
        if (series[index].datum !== highlightedSeries) {
            onHighlightChange(series[index].datum);
        }
    };
    var handleBlur = function (event) {
        var _a;
        // We need to check if the next element to be focused inside the plot container or not
        // so we don't clear the selected legend in case we are still focusing elements ( legend elements )
        // inside the plot container
        if (event.relatedTarget === null ||
            (containerRef.current &&
                !containerRef.current.contains(event.relatedTarget) &&
                !((_a = plotContainerRef === null || plotContainerRef === void 0 ? void 0 : plotContainerRef.current) === null || _a === void 0 ? void 0 : _a.contains(event.relatedTarget)))) {
            onHighlightChange(null);
        }
    };
    var handleMouseOver = function (s) {
        if (s !== highlightedSeries) {
            onHighlightChange(s);
        }
    };
    var handleMouseLeave = function () {
        onHighlightChange(null);
    };
    return (React.createElement(React.Fragment, null,
        React.createElement("div", { ref: containerRef, role: "toolbar", "aria-label": legendTitle || ariaLabel, className: styles.root, onKeyDown: handleKeyPress, onBlur: handleBlur },
            legendTitle && (React.createElement(InternalBox, { fontWeight: "bold", className: styles.title }, legendTitle)),
            React.createElement("div", { className: styles.list }, series.map(function (s, index) {
                var _a;
                var someHighlighted = highlightedSeries !== null;
                var isHighlighted = highlightedSeries === s.datum;
                var isDimmed = someHighlighted && !isHighlighted;
                return (React.createElement("div", __assign({}, focusVisible, { role: "button", key: index, "aria-pressed": isHighlighted, className: clsx(styles.marker, (_a = {},
                        _a[styles['marker--dimmed']] = isDimmed,
                        _a[styles['marker--highlighted']] = isHighlighted,
                        _a)), ref: function (elem) {
                        if (elem) {
                            segmentsRef.current[index] = elem;
                        }
                        else {
                            delete segmentsRef.current[index];
                        }
                    }, tabIndex: index === highlightedSeriesIndex || (highlightedSeriesIndex === undefined && index === 0) ? 0 : -1, onFocus: function () { return handleSelection(index); }, onClick: function () { return handleSelection(index); }, onMouseOver: function () { return handleMouseOver(s.datum); }, onMouseLeave: handleMouseLeave }),
                    React.createElement(SeriesMarker, { color: s.color, type: s.type }),
                    " ",
                    s.label));
            })))));
}
function findSeriesIndex(series, targetSeries) {
    for (var index = 0; index < series.length; index++) {
        if (series[index].datum === targetSeries) {
            return index;
        }
    }
    return undefined;
}
//# sourceMappingURL=index.js.map