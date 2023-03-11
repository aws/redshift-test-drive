// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useLayoutEffect } from 'react';
import { useAppLayoutContext } from '../../context/app-layout-context';
import { useContainerQuery } from '../container-queries';
/**
 * Observes the height of an element referenced by the returning ref and sets the value as overlapping
 * height for the surrounding AppLayout component.
 * @param props.disabled disables hook if not applicable
 * @returns ref to be measured as overlapping height
 */
export function useDynamicOverlap(props) {
    var _a;
    var disabled = (_a = props === null || props === void 0 ? void 0 : props.disabled) !== null && _a !== void 0 ? _a : false;
    var setDynamicOverlapHeight = useAppLayoutContext().setDynamicOverlapHeight;
    var _b = useContainerQuery(function (rect) { return rect.height; }), overlapContainerQuery = _b[0], overlapElementRef = _b[1];
    useLayoutEffect(function handleDynamicOverlapHeight() {
        if (!disabled) {
            setDynamicOverlapHeight === null || setDynamicOverlapHeight === void 0 ? void 0 : setDynamicOverlapHeight(overlapContainerQuery !== null && overlapContainerQuery !== void 0 ? overlapContainerQuery : 0);
        }
        return function () {
            if (!disabled) {
                setDynamicOverlapHeight === null || setDynamicOverlapHeight === void 0 ? void 0 : setDynamicOverlapHeight(0);
            }
        };
    }, [disabled, overlapContainerQuery, setDynamicOverlapHeight]);
    return overlapElementRef;
}
//# sourceMappingURL=index.js.map