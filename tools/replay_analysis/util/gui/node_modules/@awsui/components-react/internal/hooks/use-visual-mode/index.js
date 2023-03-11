// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useState } from 'react';
import { ALWAYS_VISUAL_REFRESH } from '../../environment';
import { isMotionDisabled } from '../../motion';
import { findUpUntil } from '../../utils/dom';
import { useMutationObserver } from '../use-mutation-observer';
import { isDevelopment } from '../../is-development';
import { warnOnce } from '../../logging';
export function useCurrentMode(elementRef) {
    var _a = useState('light'), value = _a[0], setValue = _a[1];
    useMutationObserver(elementRef, function (node) {
        var darkModeParent = findUpUntil(node, function (node) { return node.classList.contains('awsui-polaris-dark-mode') || node.classList.contains('awsui-dark-mode'); });
        setValue(darkModeParent ? 'dark' : 'light');
    });
    return value;
}
export function useDensityMode(elementRef) {
    var _a = useState('comfortable'), value = _a[0], setValue = _a[1];
    useMutationObserver(elementRef, function (node) {
        var compactModeParent = findUpUntil(node, function (node) { return node.classList.contains('awsui-polaris-compact-mode') || node.classList.contains('awsui-compact-mode'); });
        setValue(compactModeParent ? 'compact' : 'comfortable');
    });
    return value;
}
export var useVisualRefresh = ALWAYS_VISUAL_REFRESH ? function () { return true; } : useVisualRefreshDynamic;
// We expect VR is to be set only once and before the application is rendered.
var visualRefreshState = undefined;
// for testing
export function clearVisualRefreshState() {
    visualRefreshState = undefined;
}
function detectVisualRefresh() {
    return typeof document !== 'undefined' && !!document.querySelector('.awsui-visual-refresh');
}
export function useVisualRefreshDynamic() {
    if (visualRefreshState === undefined) {
        visualRefreshState = detectVisualRefresh();
    }
    if (isDevelopment) {
        var newVisualRefreshState = detectVisualRefresh();
        if (newVisualRefreshState !== visualRefreshState) {
            warnOnce('Visual Refresh', 'Dynamic visual refresh change detected. This is not supported. ' +
                'Make sure `awsui-visual-refresh` is attached to the `<body>` element before initial React render');
        }
    }
    return visualRefreshState;
}
export function useReducedMotion(elementRef) {
    var _a = useState(false), value = _a[0], setValue = _a[1];
    useMutationObserver(elementRef, function (node) {
        setValue(isMotionDisabled(node));
    });
    return value;
}
//# sourceMappingURL=index.js.map