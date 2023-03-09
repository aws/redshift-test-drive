// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useMergeRefs } from '../../hooks/use-merge-refs';
import TabTrap from '../tab-trap/index';
import { getFirstFocusable, getLastFocusable } from './utils';
export default function FocusLock(_a) {
    var className = _a.className, disabled = _a.disabled, autoFocus = _a.autoFocus, restoreFocus = _a.restoreFocus, children = _a.children;
    var returnFocusToRef = useRef(null);
    var containerRef = useRef(null);
    // Using a callback ref to detect component unmounts, which is safer than using useEffect.
    var restoreFocusHandler = useCallback(function (elem) {
        var _a;
        if (elem === null && restoreFocus) {
            (_a = returnFocusToRef.current) === null || _a === void 0 ? void 0 : _a.focus();
        }
    }, [restoreFocus]);
    var mergedRef = useMergeRefs(containerRef, restoreFocusHandler);
    var focusFirst = function () {
        var _a;
        if (containerRef.current) {
            (_a = getFirstFocusable(containerRef.current)) === null || _a === void 0 ? void 0 : _a.focus();
        }
    };
    var focusLast = function () {
        var _a;
        if (containerRef.current) {
            (_a = getLastFocusable(containerRef.current)) === null || _a === void 0 ? void 0 : _a.focus();
        }
    };
    useEffect(function () {
        if (autoFocus && !disabled) {
            returnFocusToRef.current = document.activeElement;
            focusFirst();
        }
    }, [autoFocus, disabled]);
    // Returns focus when disabled changes from false to true.
    var _b = useState(!!disabled), prevDisabled = _b[0], setPrevDisabled = _b[1];
    useEffect(function () {
        var _a;
        if (prevDisabled !== !!disabled) {
            setPrevDisabled(!!disabled);
            if (disabled && restoreFocus) {
                (_a = returnFocusToRef.current) === null || _a === void 0 ? void 0 : _a.focus();
                returnFocusToRef.current = null;
            }
        }
    }, [prevDisabled, disabled, restoreFocus]);
    return (React.createElement(React.Fragment, null,
        React.createElement(TabTrap, { disabled: disabled, focusNextCallback: focusLast }),
        React.createElement("div", { className: className, ref: mergedRef }, children),
        React.createElement(TabTrap, { disabled: disabled, focusNextCallback: focusFirst })));
}
//# sourceMappingURL=index.js.map