// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useContext, createContext } from 'react';
var SplitPanelContext = createContext(null);
export var SplitPanelContextProvider = SplitPanelContext.Provider;
export function useSplitPanelContext() {
    var ctx = useContext(SplitPanelContext);
    if (!ctx) {
        throw new Error('Split panel can only be used inside app layout');
    }
    return ctx;
}
//# sourceMappingURL=split-panel-context.js.map