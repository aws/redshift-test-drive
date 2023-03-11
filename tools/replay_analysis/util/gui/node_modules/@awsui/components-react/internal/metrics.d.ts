export interface MetricsLogItem {
    source: string;
    action: string;
    version: string;
}
export interface MetricsV2EventItem {
    eventType?: string;
    eventContext?: string;
    eventDetail?: string | Record<string, string | number | boolean>;
    eventValue?: string | Record<string, string | number | boolean>;
}
export declare const Metrics: {
    initMetrics(theme: string): void;
    /**
     * Calls Console Platform's client logging JS API with provided metric name, value, and detail.
     * Does nothing if Console Platform client logging JS is not present in page.
     */
    sendMetric(metricName: string, value: number, detail?: string): void;
    /**
     * Calls Console Platform's client v2 logging JS API with provided metric name and detail.
     * Does nothing if Console Platform client logging JS is not present in page.
     */
    sendPanoramaMetric(metric: MetricsV2EventItem): void;
    sendMetricObject(metric: MetricsLogItem, value: number): void;
    sendMetricObjectOnce(metric: MetricsLogItem, value: number): void;
    sendMetricOnce(metricName: string, value: number, detail?: string): void;
    logComponentLoaded(): void;
    logComponentUsed(componentName: string): void;
};
export declare const MetricsTestHelper: {
    resetOneTimeMetricsCache: () => void;
    formatMajorVersionForMetricDetail: (version: string) => string;
    formatVersionForMetricName: (theme: string, version: string) => string;
};
//# sourceMappingURL=metrics.d.ts.map