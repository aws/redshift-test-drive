// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import clsx from 'clsx';
import { useAppLayoutInternals } from './context';
import styles from './styles.css.js';
/**
 * The CSS class 'awsui-context-content-header' needs to be added to the root element so
 * that the design tokens used are overridden with the appropriate values.
 */
export default function Background() {
    var _a, _b;
    var _c = useAppLayoutInternals(), hasNotificationsContent = _c.hasNotificationsContent, hasStickyBackground = _c.hasStickyBackground, stickyNotifications = _c.stickyNotifications;
    return (React.createElement("div", { className: clsx(styles.background, 'awsui-context-content-header') },
        React.createElement("div", { className: clsx(styles['notifications-appbar-header'], (_a = {},
                _a[styles['has-notifications-content']] = hasNotificationsContent,
                _a[styles['has-sticky-background']] = hasStickyBackground,
                _a[styles['sticky-notifications']] = stickyNotifications,
                _a)) }),
        React.createElement("div", { className: clsx(styles.overlap, (_b = {},
                _b[styles['has-sticky-background']] = hasStickyBackground,
                _b)) })));
}
//# sourceMappingURL=background.js.map