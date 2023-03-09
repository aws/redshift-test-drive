// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
function setDayIndex(date, dayIndex) {
    var diff = dayIndex - date.getDay();
    date.setDate(date.getDate() + diff);
}
export function renderDayName(locale, dayIndex, mode) {
    var tempDate = new Date();
    setDayIndex(tempDate, dayIndex);
    return tempDate.toLocaleDateString(locale, { weekday: mode });
}
export function renderMonthAndYear(locale, baseDate) {
    var result = baseDate.toLocaleDateString(locale, {
        year: 'numeric',
        month: 'long'
    });
    return result;
}
/*
 `toLocaleDateString` is expensive (10+ ms) to calculate in IE11.
*/
var dayLabelCache = new Map();
export function getDateLabel(locale, date, mode) {
    if (mode === void 0) { mode = 'full'; }
    var cacheKey = locale + date.getTime() + mode;
    var cachedValue = dayLabelCache.get(cacheKey);
    if (cachedValue) {
        return cachedValue;
    }
    var value = date.toLocaleDateString(locale, {
        weekday: mode === 'full' ? 'long' : undefined,
        month: 'long',
        day: 'numeric',
        year: 'numeric'
    });
    dayLabelCache.set(cacheKey, value);
    return value;
}
export function renderTimeLabel(locale, date, format) {
    var options = {};
    if (format === 'hh') {
        options = { hour: '2-digit' };
    }
    if (format === 'hh:mm') {
        options = { hour: '2-digit', minute: '2-digit' };
    }
    var value = date.toLocaleTimeString(locale, options);
    return value;
}
//# sourceMappingURL=intl.js.map