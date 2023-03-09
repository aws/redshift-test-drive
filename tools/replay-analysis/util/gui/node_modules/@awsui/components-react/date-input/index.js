// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { __assign } from "tslib";
import React from 'react';
import { applyDisplayName } from '../internal/utils/apply-display-name';
import useBaseComponent from '../internal/hooks/use-base-component';
import InternalDateInput from './internal';
var DateInput = React.forwardRef(function (props, ref) {
    var baseComponentProps = useBaseComponent('DateInput');
    return React.createElement(InternalDateInput, __assign({}, props, baseComponentProps, { ref: ref }));
});
applyDisplayName(DateInput, 'DateInput');
export default DateInput;
//# sourceMappingURL=index.js.map