import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useEffect, useRef } from 'react';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import styles from './styles.css.js';
import { useSplitPanelContext } from '../internal/context/split-panel-context';
import { useVisualRefresh } from '../internal/hooks/use-visual-mode';
import { useResizeObserver } from '../internal/hooks/container-queries';
export function SplitPanelContentBottom(_a) {
    var _b, _c, _d;
    var baseProps = _a.baseProps, isOpen = _a.isOpen, state = _a.state, transitioningElementRef = _a.transitioningElementRef, splitPanelRef = _a.splitPanelRef, cappedSize = _a.cappedSize, header = _a.header, resizeHandle = _a.resizeHandle, children = _a.children, appLayoutMaxWidth = _a.appLayoutMaxWidth, panelHeaderId = _a.panelHeaderId, onToggle = _a.onToggle;
    var isRefresh = useVisualRefresh();
    var _e = useSplitPanelContext(), bottomOffset = _e.bottomOffset, leftOffset = _e.leftOffset, rightOffset = _e.rightOffset, disableContentPaddings = _e.disableContentPaddings, contentWrapperPaddings = _e.contentWrapperPaddings, isMobile = _e.isMobile, reportHeaderHeight = _e.reportHeaderHeight;
    var transitionContentBottomRef = useMergeRefs(splitPanelRef || null, transitioningElementRef);
    var headerRef = useRef(null);
    useResizeObserver(headerRef, function (entry) { return reportHeaderHeight(entry.borderBoxHeight); });
    useEffect(function () {
        // report empty height when unmounting the panel
        return function () { return reportHeaderHeight(0); };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);
    var centeredMaxWidthClasses = clsx((_b = {},
        _b[styles['pane-bottom-center-align']] = isRefresh,
        _b[styles['pane-bottom-content-nav-padding']] = contentWrapperPaddings === null || contentWrapperPaddings === void 0 ? void 0 : contentWrapperPaddings.closedNav,
        _b[styles['pane-bottom-content-tools-padding']] = contentWrapperPaddings === null || contentWrapperPaddings === void 0 ? void 0 : contentWrapperPaddings.closedTools,
        _b));
    return (React.createElement("div", __assign({}, baseProps, { className: clsx(baseProps.className, styles.root, styles.drawer, styles['position-bottom'], (_c = {},
            _c[styles['drawer-closed']] = !isOpen,
            _c[styles['drawer-mobile']] = isMobile,
            _c[styles['drawer-disable-content-paddings']] = disableContentPaddings,
            _c[styles.animating] = isRefresh && (state === 'entering' || state === 'exiting'),
            _c[styles.refresh] = isRefresh,
            _c)), onClick: function () { return !isOpen && onToggle(); }, style: {
            bottom: bottomOffset,
            left: leftOffset,
            right: rightOffset,
            height: isOpen ? cappedSize : undefined
        }, ref: transitionContentBottomRef }),
        isOpen && React.createElement("div", { className: styles['slider-wrapper-bottom'] }, resizeHandle),
        React.createElement("div", { className: styles['drawer-content-bottom'], "aria-labelledby": panelHeaderId, role: "region" },
            React.createElement("div", { className: clsx(styles['pane-header-wrapper-bottom'], centeredMaxWidthClasses), ref: headerRef }, header),
            React.createElement("div", { className: clsx(styles['content-bottom'], centeredMaxWidthClasses), "aria-hidden": !isOpen },
                React.createElement("div", { className: clsx((_d = {}, _d[styles['content-bottom-max-width']] = isRefresh, _d)), style: appLayoutMaxWidth }, children)))));
}
//# sourceMappingURL=bottom.js.map