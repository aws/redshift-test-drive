import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useCallback, useLayoutEffect, useRef, useState } from 'react';
import clsx from 'clsx';
import { getContainingBlock, nodeContains } from '../internal/utils/dom';
import { useResizeObserver } from '../internal/hooks/container-queries';
import { calculatePosition } from './utils/positions';
import styles from './styles.css.js';
import { useVisualRefresh } from '../internal/hooks/use-visual-mode';
var INITIAL_STYLES = { position: 'absolute', top: -9999, left: -9999 };
export default function PopoverContainer(_a) {
    var _b;
    var position = _a.position, trackRef = _a.trackRef, trackKey = _a.trackKey, arrow = _a.arrow, children = _a.children, zIndex = _a.zIndex, renderWithPortal = _a.renderWithPortal, size = _a.size, fixedWidth = _a.fixedWidth, variant = _a.variant;
    var bodyRef = useRef(null);
    var contentRef = useRef(null);
    var popoverRef = useRef(null);
    var arrowRef = useRef(null);
    var _c = useState(INITIAL_STYLES), popoverStyle = _c[0], setPopoverStyle = _c[1];
    var _d = useState(null), internalPosition = _d[0], setInternalPosition = _d[1];
    var isRefresh = useVisualRefresh();
    // Store the handler in a ref so that it can still be replaced from outside of the listener closure.
    var positionHandlerRef = useRef(function () { });
    // Updates the position handler.
    var updatePositionHandler = useCallback(function () {
        if (!trackRef.current || !popoverRef.current || !bodyRef.current || !contentRef.current || !arrowRef.current) {
            return;
        }
        // Get important elements
        var popover = popoverRef.current;
        var body = bodyRef.current;
        var arrow = arrowRef.current;
        var document = popover.ownerDocument;
        var track = trackRef.current;
        // If the popover body isn't being rendered for whatever reason (e.g. "display: none" or JSDOM),
        // or track does not belong to the document - bail on calculating dimensions.
        if (popover.offsetWidth === 0 || popover.offsetHeight === 0 || !nodeContains(document.body, track)) {
            return;
        }
        // Imperatively move body off-screen to give it room to expand.
        // Not doing this in React because this recalculation should happen
        // in the span of a single frame without rerendering anything.
        var prevTop = popover.style.top;
        var prevLeft = popover.style.left;
        popover.style.top = '0';
        popover.style.left = '0';
        // Imperatively remove body styles that can remain from the previous computation.
        body.style.maxHeight = '';
        body.style.overflowX = '';
        body.style.overflowY = '';
        // Get rects representing key elements
        // Use getComputedStyle for arrowRect to avoid modifications made by transform
        var viewportRect = getViewportRect(document.defaultView);
        var trackRect = track.getBoundingClientRect();
        var arrowRect = {
            width: parseFloat(getComputedStyle(arrow).width),
            height: parseFloat(getComputedStyle(arrow).height)
        };
        var containingBlock = getContainingBlock(popover);
        var containingBlockRect = containingBlock ? containingBlock.getBoundingClientRect() : viewportRect;
        var bodyBorderWidth = getBorderWidth(body);
        var contentRect = contentRef.current.getBoundingClientRect();
        var contentBoundingBox = {
            width: contentRect.width + 2 * bodyBorderWidth,
            height: contentRect.height + 2 * bodyBorderWidth
        };
        // Calculate the arrow direction and viewport-relative position of the popover.
        var _a = calculatePosition(position, trackRect, arrowRect, contentBoundingBox, containingBlock ? containingBlockRect : getDocumentRect(document), viewportRect, renderWithPortal), scrollable = _a.scrollable, newInternalPosition = _a.internalPosition, boundingOffset = _a.boundingOffset;
        // Get the position of the popover relative to the offset parent.
        var popoverOffset = toRelativePosition(boundingOffset, containingBlockRect);
        // Cache the distance between the trigger and the popover (which stays the same as you scroll),
        // and use that to recalculate the new popover position.
        var trackRelativeOffset = toRelativePosition(popoverOffset, toRelativePosition(trackRect, containingBlockRect));
        // Bring back the container to its original position to prevent any flashing.
        popover.style.top = prevTop;
        popover.style.left = prevLeft;
        // Allow popover body to scroll if can't fit the popover into the container/viewport otherwise.
        if (scrollable) {
            body.style.maxHeight = boundingOffset.height + 'px';
            body.style.overflowX = 'hidden';
            body.style.overflowY = 'auto';
        }
        // Position the popover
        setInternalPosition(newInternalPosition);
        setPopoverStyle({ top: popoverOffset.top, left: popoverOffset.left });
        positionHandlerRef.current = function () {
            var newTrackOffset = toRelativePosition(track.getBoundingClientRect(), containingBlock ? containingBlock.getBoundingClientRect() : viewportRect);
            setPopoverStyle({
                top: newTrackOffset.top + trackRelativeOffset.top,
                left: newTrackOffset.left + trackRelativeOffset.left
            });
        };
    }, [position, trackRef, renderWithPortal]);
    // Recalculate position when properties change.
    useLayoutEffect(function () {
        updatePositionHandler();
    }, [updatePositionHandler, trackKey]);
    // Recalculate position when content size changes.
    useResizeObserver(contentRef, function () { return updatePositionHandler(); });
    // Recalculate position on DOM events.
    useLayoutEffect(function () {
        /*
          This is a heuristic. Some layout changes are caused by user clicks (e.g. toggling the tools panel, submitting a form),
          and by tracking the click event we can adapt the popover's position to the new layout.
    
          TODO: extend this to Enter and Spacebar?
        */
        var updatePosition = function () { return requestAnimationFrame(function () { return updatePositionHandler(); }); };
        var refreshPosition = function () { return requestAnimationFrame(function () { return positionHandlerRef.current(); }); };
        window.addEventListener('click', updatePosition);
        window.addEventListener('resize', updatePosition);
        window.addEventListener('scroll', refreshPosition, true);
        return function () {
            window.removeEventListener('click', updatePosition);
            window.removeEventListener('resize', updatePosition);
            window.removeEventListener('scroll', refreshPosition, true);
        };
    }, [updatePositionHandler]);
    return (React.createElement("div", { ref: popoverRef, style: __assign(__assign({}, popoverStyle), { zIndex: zIndex }), className: clsx(styles.container, isRefresh && styles.refresh) },
        React.createElement("div", { ref: arrowRef, className: clsx(styles["container-arrow"], styles["container-arrow-position-".concat(internalPosition)]), "aria-hidden": true }, arrow(internalPosition)),
        React.createElement("div", { ref: bodyRef, className: clsx(styles['container-body'], styles["container-body-size-".concat(size)], (_b = {},
                _b[styles['fixed-width']] = fixedWidth,
                _b[styles["container-body-variant-".concat(variant)]] = variant,
                _b)) },
            React.createElement("div", { ref: contentRef }, children))));
}
function getBorderWidth(element) {
    return parseInt(getComputedStyle(element).borderWidth) || 0;
}
/**
 * Convert a viewport-relative offset to an element-relative offset.
 */
function toRelativePosition(element, parent) {
    return {
        top: element.top - parent.top,
        left: element.left - parent.left
    };
}
/**
 * Get a BoundingOffset that represents the visible viewport.
 */
function getViewportRect(window) {
    return {
        top: 0,
        left: 0,
        width: window.innerWidth,
        height: window.innerHeight
    };
}
function getDocumentRect(document) {
    var _a = document.documentElement.getBoundingClientRect(), top = _a.top, left = _a.left;
    return {
        top: top,
        left: left,
        width: document.documentElement.scrollWidth,
        height: document.documentElement.scrollHeight
    };
}
//# sourceMappingURL=container.js.map