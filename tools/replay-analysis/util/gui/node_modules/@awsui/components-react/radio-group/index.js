import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import { applyDisplayName } from '../internal/utils/apply-display-name';
import useBaseComponent from '../internal/hooks/use-base-component';
import InternalRadioGroup from './internal';
var RadioGroup = React.forwardRef(function (props, ref) {
    var baseComponentProps = useBaseComponent('RadioGroup');
    return React.createElement(InternalRadioGroup, __assign({ ref: ref }, props, baseComponentProps));
});
applyDisplayName(RadioGroup, 'RadioGroup');
export default RadioGroup;
//# sourceMappingURL=index.js.map