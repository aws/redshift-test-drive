// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { add } from 'date-fns';
import React from 'react';
import styles from '../../styles.css.js';
import { renderMonthAndYear } from '../../../calendar/utils/intl';
import { PrevMonthButton, NextMonthButton } from './header-button';
import LiveRegion from '../../../internal/components/live-region';
export default function CalendarHeader(_a) {
    var baseDate = _a.baseDate, locale = _a.locale, onChangeMonth = _a.onChangeMonth, previousMonthLabel = _a.previousMonthLabel, nextMonthLabel = _a.nextMonthLabel, isSingleGrid = _a.isSingleGrid, headingIdPrefix = _a.headingIdPrefix;
    var prevMonthLabel = renderMonthAndYear(locale, add(baseDate, { months: -1 }));
    var currentMonthLabel = renderMonthAndYear(locale, baseDate);
    return (React.createElement(React.Fragment, null,
        React.createElement("div", { className: styles['calendar-header'] },
            React.createElement(PrevMonthButton, { ariaLabel: previousMonthLabel, baseDate: baseDate, onChangeMonth: onChangeMonth }),
            React.createElement("h2", { className: styles['calendar-header-months-wrapper'] },
                !isSingleGrid && (React.createElement("span", { className: styles['calendar-header-month'], id: "".concat(headingIdPrefix, "-prevmonth") }, prevMonthLabel)),
                React.createElement("span", { className: styles['calendar-header-month'], id: "".concat(headingIdPrefix, "-currentmonth") }, currentMonthLabel)),
            React.createElement(NextMonthButton, { ariaLabel: nextMonthLabel, baseDate: baseDate, onChangeMonth: onChangeMonth })),
        React.createElement(LiveRegion, null, isSingleGrid ? currentMonthLabel : "".concat(prevMonthLabel, ", ").concat(currentMonthLabel))));
}
//# sourceMappingURL=index.js.map