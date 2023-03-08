// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign } from "tslib";
import { Metrics } from '../../internal/metrics';
var prefix = 'csa_wizard';
var createEventType = function (eventType) { return "".concat(prefix, "_").concat(eventType); };
var createEventContext = function (stepIndex) {
    if (stepIndex === void 0) { stepIndex = 0; }
    return "".concat(prefix, "_step").concat(stepIndex + 1);
};
var createEventDetail = function (stepIndex) {
    if (stepIndex === void 0) { stepIndex = 0; }
    return "step".concat(stepIndex + 1);
};
// A custom time cache is used to not clear the timer between navigation attempts
// This allows us the ability to track time to attempt each step as well as the time to complete
// each step
var timeCache = {};
var timeStart = function (key) {
    if (key === void 0) { key = 'current'; }
    timeCache[key] = Date.now();
};
var timeEnd = function (key, clear) {
    if (key === void 0) { key = 'current'; }
    if (clear === void 0) { clear = false; }
    var start = timeCache[key];
    // No start time is available when starting the first step
    if (!start) {
        return undefined;
    }
    if (clear) {
        delete timeCache[key];
    }
    return (Date.now() - start) / 1000; // Convert to seconds
};
export var trackStartStep = function (stepIndex) {
    var eventContext = createEventContext(stepIndex);
    // Track the starting time of the wizard
    if (stepIndex === undefined) {
        timeStart(prefix);
    }
    // End the timer of the previous step
    var time = timeEnd();
    // Start a new timer of the current step
    timeStart();
    Metrics.sendPanoramaMetric(__assign({ eventContext: eventContext, eventDetail: createEventDetail(stepIndex), eventType: createEventType('step') }, (time !== undefined && { eventValue: time.toString() })));
};
export var trackNavigate = function (activeStepIndex, requestedStepIndex, reason) {
    var eventContext = createEventContext(activeStepIndex);
    var time = timeEnd();
    Metrics.sendPanoramaMetric({
        eventContext: eventContext,
        eventDetail: createEventDetail(requestedStepIndex),
        eventType: createEventType('navigate'),
        eventValue: __assign({ reason: reason }, (time !== undefined && { time: time }))
    });
};
export var trackSubmit = function (stepIndex) {
    var eventContext = createEventContext(stepIndex);
    // End the timer of the wizard
    var time = timeEnd(prefix);
    Metrics.sendPanoramaMetric(__assign({ eventContext: eventContext, eventDetail: createEventDetail(stepIndex), eventType: createEventType('submit') }, (time !== undefined && { eventValue: time.toString() })));
};
//# sourceMappingURL=analytics.js.map