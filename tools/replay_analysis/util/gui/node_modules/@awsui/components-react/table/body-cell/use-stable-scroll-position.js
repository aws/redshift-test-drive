// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useCallback, useRef } from 'react';
export function isScrollable(ele) {
    var overflowXStyle = window.getComputedStyle(ele).overflowX;
    var isOverflowHidden = overflowXStyle.indexOf('hidden') !== -1;
    return ele.scrollWidth > ele.clientWidth && !isOverflowHidden;
}
export function getScrollableParent(ele) {
    return !ele || ele === document.body
        ? document.body
        : isScrollable(ele)
            ? ele
            : getScrollableParent(ele.parentElement);
}
var shouldScroll = function (_a, _b) {
    var cx = _a[0], cy = _a[1];
    var px = _b[0], py = _b[1];
    return cx - px > 5 || cy - py > 5;
};
/**
 * This hook stores the scroll position of the nearest scrollable parent of the
 * `activeElementRef` when `storeScrollPosition` is called, and restores it when
 * `restoreScrollPosition` is called.
 * @param activeElementRef Ref to an active element in the table. This is used to find the nearest scrollable parent.
 */
export function useStableScrollPosition(activeElementRef) {
    var scrollRef = useRef();
    var storeScrollPosition = useCallback(function () {
        var _a;
        var scrollableParent = getScrollableParent((_a = activeElementRef.current) !== null && _a !== void 0 ? _a : document.body);
        if (scrollableParent) {
            scrollRef.current = [scrollableParent.scrollLeft, scrollableParent.scrollTop];
        }
    }, [activeElementRef]);
    var restoreScrollPosition = useCallback(function () {
        var _a;
        var _b;
        var scrollableParent = getScrollableParent((_b = activeElementRef.current) !== null && _b !== void 0 ? _b : document.body);
        if (scrollRef.current &&
            scrollRef.current.toString() !== '0,0' &&
            shouldScroll(scrollRef.current, [scrollableParent.scrollLeft, scrollableParent.scrollTop])) {
            _a = scrollRef.current, scrollableParent.scrollLeft = _a[0], scrollableParent.scrollTop = _a[1];
        }
    }, [activeElementRef]);
    return { storeScrollPosition: storeScrollPosition, restoreScrollPosition: restoreScrollPosition };
}
//# sourceMappingURL=use-stable-scroll-position.js.map