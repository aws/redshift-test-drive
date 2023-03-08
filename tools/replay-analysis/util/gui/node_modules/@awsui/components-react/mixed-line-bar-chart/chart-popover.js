// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import clsx from 'clsx';
import ChartPopover from '../internal/components/chart-popover';
import ChartSeriesDetails from '../internal/components/chart-series-details';
import styles from './styles.css.js';
import { Transition } from '../internal/components/transition';
export default React.forwardRef(MixedChartPopover);
function MixedChartPopover(_a, popoverRef) {
    var containerRef = _a.containerRef, trackRef = _a.trackRef, isOpen = _a.isOpen, isPinned = _a.isPinned, highlightDetails = _a.highlightDetails, onDismiss = _a.onDismiss, _b = _a.size, size = _b === void 0 ? 'medium' : _b, dismissAriaLabel = _a.dismissAriaLabel, onMouseEnter = _a.onMouseEnter, onMouseLeave = _a.onMouseLeave;
    return (React.createElement(Transition, { "in": isOpen }, function (state, ref) { return (React.createElement("div", { ref: ref, className: clsx(state === 'exiting' && styles.exiting) }, (isOpen || state !== 'exited') && highlightDetails && (React.createElement(ChartPopover, { ref: popoverRef, title: highlightDetails.position, trackRef: trackRef, trackKey: highlightDetails.position, dismissButton: isPinned, dismissAriaLabel: dismissAriaLabel, onDismiss: onDismiss, container: containerRef.current, size: size, onMouseEnter: onMouseEnter, onMouseLeave: onMouseLeave },
        React.createElement(ChartSeriesDetails, { details: highlightDetails.details }))))); }));
}
//# sourceMappingURL=chart-popover.js.map