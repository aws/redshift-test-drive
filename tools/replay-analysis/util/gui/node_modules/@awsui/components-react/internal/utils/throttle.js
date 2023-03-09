// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
export function throttle(func, delay, _a) {
    var _b = _a === void 0 ? {} : _a, _c = _b.trailing, trailing = _c === void 0 ? true : _c;
    var pending = null;
    var lastInvokeTime = null;
    var timerId = null;
    // Runs on every animation frame until timer stopped.
    function pendingFunc() {
        if (pending === null || lastInvokeTime === null) {
            return;
        }
        var invokeTime = Date.now();
        var shouldInvoke = invokeTime - lastInvokeTime >= delay;
        if (shouldInvoke) {
            func.apply(pending["this"], pending.args);
            lastInvokeTime = invokeTime;
            pending = null;
            timerId = null;
        }
        else if (trailing) {
            startTimer();
        }
    }
    function startTimer() {
        if (timerId) {
            cancelAnimationFrame(timerId);
        }
        timerId = requestAnimationFrame(pendingFunc);
    }
    // Decorated client function with delay mechanism.
    function throttled() {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (lastInvokeTime === null) {
            lastInvokeTime = Date.now();
            func.apply(this, args);
        }
        else {
            pending = { "this": this, args: args };
            startTimer();
        }
    }
    // Prevents delayed function from execution when no longer needed.
    throttled.cancel = function () {
        if (timerId) {
            cancelAnimationFrame(timerId);
        }
        pending = null;
        lastInvokeTime = null;
        timerId = null;
    };
    return throttled;
}
//# sourceMappingURL=throttle.js.map