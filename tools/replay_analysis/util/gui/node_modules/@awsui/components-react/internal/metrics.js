import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { PACKAGE_VERSION } from './environment';
var oneTimeMetrics = {};
// In case we need to override the theme for VR
var theme = '';
function setTheme(newTheme) {
    theme = newTheme;
}
// react is the only framework we're using
var framework = 'react';
var buildMetricHash = function (_a) {
    var source = _a.source, action = _a.action;
    return ["src".concat(source), "action".concat(action)].join('_');
};
var getMajorVersion = function (versionString) {
    var majorVersionMatch = versionString.match(/^(\d+\.\d+)/);
    return majorVersionMatch ? majorVersionMatch[1] : '';
};
var formatMajorVersionForMetricDetail = function (version) {
    return version.replace(/\s/g, '');
};
var formatVersionForMetricName = function (theme, version) {
    return "".concat(theme.charAt(0)).concat(getMajorVersion(version).replace('.', ''));
};
var buildMetricDetail = function (_a) {
    var source = _a.source, action = _a.action, version = _a.version;
    var metricOrigin = typeof AWSUI_METRIC_ORIGIN !== 'undefined' ? AWSUI_METRIC_ORIGIN : 'main';
    var detailObject = {
        o: metricOrigin,
        s: source,
        t: theme,
        a: action,
        f: framework,
        v: formatMajorVersionForMetricDetail(version)
    };
    return JSON.stringify(detailObject);
};
var buildMetricName = function (_a) {
    var source = _a.source, version = _a.version;
    return ['awsui', source, "".concat(formatVersionForMetricName(theme, version))].join('_');
};
var findPanorama = function (currentWindow) {
    try {
        if (typeof (currentWindow === null || currentWindow === void 0 ? void 0 : currentWindow.panorama) === 'function') {
            return currentWindow === null || currentWindow === void 0 ? void 0 : currentWindow.panorama;
        }
        if (!currentWindow || currentWindow.parent === currentWindow) {
            // When the window has no more parents, it references itself
            return undefined;
        }
        return findPanorama(currentWindow.parent);
    }
    catch (ex) {
        // Most likely a cross-origin access error
        return undefined;
    }
};
var findAWSC = function (currentWindow) {
    try {
        if (typeof (currentWindow === null || currentWindow === void 0 ? void 0 : currentWindow.AWSC) === 'object') {
            return currentWindow === null || currentWindow === void 0 ? void 0 : currentWindow.AWSC;
        }
        if (!currentWindow || currentWindow.parent === currentWindow) {
            // When the window has no more parents, it references itself
            return undefined;
        }
        return findAWSC(currentWindow.parent);
    }
    catch (ex) {
        // Most likely a cross-origin access error
        return undefined;
    }
};
export var Metrics = {
    initMetrics: function (theme) {
        setTheme(theme);
    },
    /**
     * Calls Console Platform's client logging JS API with provided metric name, value, and detail.
     * Does nothing if Console Platform client logging JS is not present in page.
     */
    sendMetric: function (metricName, value, detail) {
        if (!theme) {
            // Metrics need to be initialized first (initMetrics)
            console.error('Metrics need to be initalized first.');
            return;
        }
        if (!metricName || !/^[a-zA-Z0-9_-]{1,32}$/.test(metricName)) {
            console.error("Invalid metric name: ".concat(metricName));
            return;
        }
        if (detail && detail.length > 200) {
            console.error("Detail for metric ".concat(metricName, " is too long: ").concat(detail));
            return;
        }
        var AWSC = findAWSC(window);
        if (typeof AWSC === 'object' && typeof AWSC.Clog === 'object' && typeof AWSC.Clog.log === 'function') {
            AWSC.Clog.log(metricName, value, detail);
        }
    },
    /**
     * Calls Console Platform's client v2 logging JS API with provided metric name and detail.
     * Does nothing if Console Platform client logging JS is not present in page.
     */
    sendPanoramaMetric: function (metric) {
        if (typeof metric.eventDetail === 'object') {
            metric.eventDetail = JSON.stringify(metric.eventDetail);
        }
        if (metric.eventDetail && metric.eventDetail.length > 200) {
            console.error("Detail for metric is too long: ".concat(metric.eventDetail));
            return;
        }
        if (typeof metric.eventValue === 'object') {
            metric.eventValue = JSON.stringify(metric.eventValue);
        }
        var panorama = findPanorama(window);
        if (typeof panorama === 'function') {
            panorama('trackCustomEvent', __assign(__assign({}, metric), { timestamp: Date.now() }));
        }
    },
    sendMetricObject: function (metric, value) {
        this.sendMetric(buildMetricName(metric), value, buildMetricDetail(metric));
    },
    sendMetricObjectOnce: function (metric, value) {
        var metricHash = buildMetricHash(metric);
        if (!oneTimeMetrics[metricHash]) {
            this.sendMetricObject(metric, value);
            oneTimeMetrics[metricHash] = true;
        }
    },
    /*
     * Calls Console Platform's client logging only the first time the provided metricName is used.
     * Subsequent calls with the same metricName are ignored.
     */
    sendMetricOnce: function (metricName, value, detail) {
        if (!oneTimeMetrics[metricName]) {
            this.sendMetric(metricName, value, detail);
            oneTimeMetrics[metricName] = true;
        }
    },
    /*
     * Reports a metric value 1 to Console Platform's client logging service to indicate that the
     * component was loaded. The component load event will only be reported as used to client logging
     * service once per page view.
     */
    logComponentLoaded: function () {
        this.sendMetricObjectOnce({
            source: 'components',
            action: 'loaded',
            version: PACKAGE_VERSION
        }, 1);
    },
    /*
     * Reports a metric value 1 to Console Platform's client logging service to indicate that the
     * component was used in the page.  A component will only be reported as used to client logging
     * service once per page view.
     */
    logComponentUsed: function (componentName) {
        this.sendMetricObjectOnce({
            source: componentName,
            action: 'used',
            version: PACKAGE_VERSION
        }, 1);
    }
};
export var MetricsTestHelper = {
    resetOneTimeMetricsCache: function () {
        for (var prop in oneTimeMetrics) {
            delete oneTimeMetrics[prop];
        }
    },
    formatMajorVersionForMetricDetail: formatMajorVersionForMetricDetail,
    formatVersionForMetricName: formatVersionForMetricName
};
//# sourceMappingURL=metrics.js.map