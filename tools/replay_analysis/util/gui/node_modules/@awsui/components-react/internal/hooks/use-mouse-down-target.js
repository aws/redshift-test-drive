// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useRef } from 'react';
import { createSingletonHandler } from './use-singleton-handler';
var useEventListenersSingleton = createSingletonHandler(function (setTarget) {
    function handleMouseDown(event) {
        setTarget(event.target);
    }
    function handleKeyDown() {
        setTarget(null);
    }
    window.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('keydown', handleKeyDown);
    return function () {
        window.removeEventListener('mousedown', handleMouseDown);
        window.removeEventListener('keydown', handleKeyDown);
    };
});
/**
 * Captures last mouse down target and clears it on keydown.
 * @returns a callback to get the last detected mouse down target.
 */
export default function useMouseDownTarget() {
    var mouseDownTargetRef = useRef(null);
    useEventListenersSingleton(function (target) {
        mouseDownTargetRef.current = target;
    });
    return function () { return mouseDownTargetRef.current; };
}
//# sourceMappingURL=use-mouse-down-target.js.map