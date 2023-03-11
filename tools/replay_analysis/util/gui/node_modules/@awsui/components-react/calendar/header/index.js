// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import styles from '../styles.css.js';
import { renderMonthAndYear } from '../utils/intl';
import { PrevMonthButton, NextMonthButton } from './header-button';
var CalendarHeader = function (_a) {
    var baseDate = _a.baseDate, locale = _a.locale, onChangeMonth = _a.onChangeMonth, previousMonthLabel = _a.previousMonthLabel, nextMonthLabel = _a.nextMonthLabel, headingId = _a.headingId;
    return (React.createElement("div", { className: styles['calendar-header'] },
        React.createElement(PrevMonthButton, { ariaLabel: previousMonthLabel, baseDate: baseDate, onChangeMonth: onChangeMonth }),
        React.createElement("h2", { className: styles['calendar-header-month'], id: headingId }, renderMonthAndYear(locale, baseDate)),
        React.createElement(NextMonthButton, { ariaLabel: nextMonthLabel, baseDate: baseDate, onChangeMonth: onChangeMonth })));
};
export default CalendarHeader;
//# sourceMappingURL=index.js.map