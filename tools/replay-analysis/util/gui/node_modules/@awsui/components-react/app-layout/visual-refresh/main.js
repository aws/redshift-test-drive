// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import clsx from 'clsx';
import { useAppLayoutInternals } from './context';
import customCssProps from '../../internal/generated/custom-css-properties';
import styles from './styles.css.js';
import testutilStyles from '../test-classes/styles.css.js';
export default function Main() {
    var _a, _b;
    var _c = useAppLayoutInternals(), breadcrumbs = _c.breadcrumbs, content = _c.content, contentHeader = _c.contentHeader, contentType = _c.contentType, disableContentPaddings = _c.disableContentPaddings, dynamicOverlapHeight = _c.dynamicOverlapHeight, hasNotificationsContent = _c.hasNotificationsContent, isNavigationOpen = _c.isNavigationOpen, isSplitPanelOpen = _c.isSplitPanelOpen, isToolsOpen = _c.isToolsOpen, isMobile = _c.isMobile, isAnyPanelOpen = _c.isAnyPanelOpen, mainElement = _c.mainElement, splitPanelDisplayed = _c.splitPanelDisplayed, offsetBottom = _c.offsetBottom, footerHeight = _c.footerHeight, splitPanelPosition = _c.splitPanelPosition;
    var isUnfocusable = isMobile && isAnyPanelOpen;
    var splitPanelHeight = offsetBottom - footerHeight;
    return (React.createElement("div", { className: clsx(styles.container, styles["content-type-".concat(contentType)], styles["split-panel-position-".concat(splitPanelPosition !== null && splitPanelPosition !== void 0 ? splitPanelPosition : 'bottom')], (_a = {},
            _a[styles['disable-content-paddings']] = disableContentPaddings,
            _a[styles['has-breadcrumbs']] = breadcrumbs,
            _a[styles['has-dynamic-overlap-height']] = dynamicOverlapHeight > 0,
            _a[styles['has-header']] = contentHeader,
            _a[styles['has-notifications-content']] = hasNotificationsContent,
            _a[styles['has-split-panel']] = splitPanelDisplayed,
            _a[styles['is-navigation-open']] = isNavigationOpen,
            _a[styles['is-tools-open']] = isToolsOpen,
            _a[styles['is-split-panel-open']] = isSplitPanelOpen,
            _a[styles.unfocusable] = isUnfocusable,
            _a), testutilStyles.content), ref: mainElement, style: (_b = {},
            _b[customCssProps.splitPanelHeight] = "".concat(splitPanelHeight, "px"),
            _b) }, content));
}
//# sourceMappingURL=main.js.map