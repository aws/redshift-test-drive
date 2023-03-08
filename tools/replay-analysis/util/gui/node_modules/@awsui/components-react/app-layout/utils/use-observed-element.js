// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useResizeObserver } from '../../internal/hooks/container-queries';
import { useCallback, useState } from 'react';
export function useObservedElement(selector) {
    var getElement = useCallback(function () {
        return document.querySelector(selector);
    }, [selector]);
    var _a = useState(0), height = _a[0], setHeight = _a[1];
    useResizeObserver(getElement, function (entry) { return setHeight(entry.borderBoxHeight); });
    return height;
}
//# sourceMappingURL=use-observed-element.js.map