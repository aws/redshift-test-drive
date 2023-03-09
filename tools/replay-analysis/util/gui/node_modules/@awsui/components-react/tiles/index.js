import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import { applyDisplayName } from '../internal/utils/apply-display-name';
import useBaseComponent from '../internal/hooks/use-base-component';
import InternalTiles from './internal';
var Tiles = React.forwardRef(function (props, ref) {
    var baseComponentProps = useBaseComponent('Tiles');
    return React.createElement(InternalTiles, __assign({ ref: ref }, props, baseComponentProps));
});
applyDisplayName(Tiles, 'Tiles');
export default Tiles;
//# sourceMappingURL=index.js.map