import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useEffect, useRef } from 'react';
import clsx from 'clsx';
import { getBaseProps } from '../../base-component';
import PopoverContainer from '../../../popover/container';
import PopoverBody from '../../../popover/body';
import popoverStyles from '../../../popover/styles.css.js';
import { nodeContains } from '../../utils/dom';
import { useMergeRefs } from '../../hooks/use-merge-refs';
import styles from './styles.css.js';
export default React.forwardRef(ChartPopover);
function ChartPopover(_a, ref) {
    var _b;
    var _c = _a.position, position = _c === void 0 ? 'right' : _c, _d = _a.size, size = _d === void 0 ? 'medium' : _d, _e = _a.fixedWidth, fixedWidth = _e === void 0 ? false : _e, _f = _a.dismissButton, dismissButton = _f === void 0 ? false : _f, dismissAriaLabel = _a.dismissAriaLabel, children = _a.children, title = _a.title, trackRef = _a.trackRef, trackKey = _a.trackKey, onDismiss = _a.onDismiss, container = _a.container, onMouseEnter = _a.onMouseEnter, onMouseLeave = _a.onMouseLeave, restProps = __rest(_a, ["position", "size", "fixedWidth", "dismissButton", "dismissAriaLabel", "children", "title", "trackRef", "trackKey", "onDismiss", "container", "onMouseEnter", "onMouseLeave"]);
    var baseProps = getBaseProps(restProps);
    var popoverObjectRef = useRef(null);
    var popoverRef = useMergeRefs(popoverObjectRef, ref);
    useEffect(function () {
        var onDocumentClick = function (event) {
            if (event.target &&
                !nodeContains(popoverObjectRef.current, event.target) && // click not in popover
                !nodeContains(container, event.target) // click not in segment
            ) {
                onDismiss(true);
            }
        };
        document.addEventListener('mousedown', onDocumentClick, { capture: true });
        return function () {
            document.removeEventListener('mousedown', onDocumentClick, { capture: true });
        };
    }, [container, onDismiss]);
    return (React.createElement("div", __assign({}, baseProps, { className: clsx(popoverStyles.root, styles.root, baseProps.className, (_b = {}, _b[styles.dismissable] = dismissButton, _b)), ref: popoverRef, onMouseEnter: onMouseEnter, onMouseLeave: onMouseLeave }),
        React.createElement(PopoverContainer, { size: size, fixedWidth: fixedWidth, position: position, trackRef: trackRef, trackKey: trackKey, arrow: function (position) { return (React.createElement("div", { className: clsx(popoverStyles.arrow, popoverStyles["arrow-position-".concat(position)]) },
                React.createElement("div", { className: popoverStyles['arrow-outer'] }),
                React.createElement("div", { className: popoverStyles['arrow-inner'] }))); } },
            React.createElement("div", { className: styles['hover-area'] },
                React.createElement(PopoverBody, { dismissButton: dismissButton, dismissAriaLabel: dismissAriaLabel, header: title, onDismiss: onDismiss, className: styles['popover-body'] }, children)))));
}
//# sourceMappingURL=index.js.map