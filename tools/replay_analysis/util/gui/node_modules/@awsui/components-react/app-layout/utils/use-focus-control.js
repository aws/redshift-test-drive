// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useCallback, useLayoutEffect, useRef } from 'react';
export function useFocusControl(isOpen, restoreFocus) {
    if (restoreFocus === void 0) { restoreFocus = false; }
    var refs = {
        toggle: useRef(null),
        close: useRef(null)
    };
    var previousFocusedElement = useRef();
    var setFocus = useCallback(function () {
        var _a, _b;
        // due to mounting/remounting, this hook gets called multiple times for a single change,
        // so we ignore any calls where the refs are undefined
        if (!(refs.toggle.current || refs.close.current)) {
            return;
        }
        if (isOpen) {
            previousFocusedElement.current = document.activeElement;
            (_a = refs.close.current) === null || _a === void 0 ? void 0 : _a.focus();
        }
        else {
            if (restoreFocus && previousFocusedElement.current && document.contains(previousFocusedElement.current)) {
                previousFocusedElement.current.focus();
                previousFocusedElement.current = undefined;
            }
            else {
                (_b = refs.toggle.current) === null || _b === void 0 ? void 0 : _b.focus();
            }
        }
    }, [isOpen, restoreFocus, refs.close, refs.toggle]);
    var loseFocus = useCallback(function () {
        previousFocusedElement.current = undefined;
    }, []);
    // eslint-disable-next-line react-hooks/exhaustive-deps
    useLayoutEffect(setFocus, [isOpen, restoreFocus]);
    return { refs: refs, setFocus: setFocus, loseFocus: loseFocus };
}
//# sourceMappingURL=use-focus-control.js.map