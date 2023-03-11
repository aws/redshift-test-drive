import { setTimeOffset } from './time-offset';
import { joinDateTime, splitDateTime } from '../internal/utils/date-time';
export function formatValue(value, _a) {
    var timeOffset = _a.timeOffset, dateOnly = _a.dateOnly;
    if (!value || value.type === 'relative') {
        return value;
    }
    if (dateOnly) {
        return {
            type: 'absolute',
            startDate: value.startDate.split('T')[0],
            endDate: value.endDate.split('T')[0]
        };
    }
    return setTimeOffset(value, timeOffset);
}
export function getDefaultMode(value, relativeOptions, rangeSelectorMode) {
    if (value && value.type) {
        return value.type;
    }
    if (rangeSelectorMode === 'relative-only') {
        return 'relative';
    }
    if (rangeSelectorMode === 'absolute-only') {
        return 'absolute';
    }
    return relativeOptions.length > 0 ? 'relative' : 'absolute';
}
export function splitAbsoluteValue(value) {
    if (!value) {
        return {
            start: { date: '', time: '' },
            end: { date: '', time: '' }
        };
    }
    return { start: splitDateTime(value.startDate), end: splitDateTime(value.endDate) };
}
export function joinAbsoluteValue(value) {
    return {
        type: 'absolute',
        startDate: joinDateTime(value.start.date, value.start.time || '00:00:00'),
        endDate: joinDateTime(value.end.date, value.end.time || '23:59:59')
    };
}
//# sourceMappingURL=utils.js.map