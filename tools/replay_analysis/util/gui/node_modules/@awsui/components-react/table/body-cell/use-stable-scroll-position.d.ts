import React from 'react';
export declare function isScrollable(ele: HTMLElement): boolean;
export declare function getScrollableParent(ele: HTMLElement | null): HTMLElement;
export interface UseStableScrollPositionResult {
    /** Stores the current scroll position of the nearest scrollable container. */
    storeScrollPosition: () => void;
    /** Restores the scroll position of the nearest scrollable container to the last stored position. */
    restoreScrollPosition: () => void;
}
/**
 * This hook stores the scroll position of the nearest scrollable parent of the
 * `activeElementRef` when `storeScrollPosition` is called, and restores it when
 * `restoreScrollPosition` is called.
 * @param activeElementRef Ref to an active element in the table. This is used to find the nearest scrollable parent.
 */
export declare function useStableScrollPosition<T extends HTMLElement>(activeElementRef: React.RefObject<T>): UseStableScrollPositionResult;
//# sourceMappingURL=use-stable-scroll-position.d.ts.map