// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useContext, createContext } from 'react';
export var AppLayoutContext = createContext({
    stickyOffsetTop: 0,
    stickyOffsetBottom: 0,
    hasBreadcrumbs: false
});
export function useAppLayoutContext() {
    return useContext(AppLayoutContext);
}
//# sourceMappingURL=app-layout-context.js.map