// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign, __rest } from "tslib";
import React from 'react';
import useBaseComponent from '../internal/hooks/use-base-component';
import { applyDisplayName } from '../internal/utils/apply-display-name';
import InternalCalendar from './internal';
export default function Calendar(_a) {
    var _b = _a.locale, locale = _b === void 0 ? '' : _b, _c = _a.isDateEnabled, isDateEnabled = _c === void 0 ? function () { return true; } : _c, props = __rest(_a, ["locale", "isDateEnabled"]);
    var baseComponentProps = useBaseComponent('Calendar');
    return React.createElement(InternalCalendar, __assign({}, props, baseComponentProps, { locale: locale, isDateEnabled: isDateEnabled }));
}
applyDisplayName(Calendar, 'Calendar');
//# sourceMappingURL=index.js.map