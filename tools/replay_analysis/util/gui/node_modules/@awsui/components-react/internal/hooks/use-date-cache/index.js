// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useRef } from 'react';
export function useDateCache() {
    var cacheRef = useRef({});
    return function (date) {
        if (cacheRef.current[date.getTime()]) {
            return cacheRef.current[date.getTime()];
        }
        cacheRef.current[date.getTime()] = date;
        return date;
    };
}
//# sourceMappingURL=index.js.map