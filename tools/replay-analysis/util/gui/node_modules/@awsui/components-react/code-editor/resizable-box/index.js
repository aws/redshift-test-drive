// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useEffect, useRef, useState } from 'react';
import { useStableEventHandler } from '../../internal/hooks/use-stable-event-handler';
import styles from './styles.css.js';
export function ResizableBox(_a) {
    var children = _a.children, height = _a.height, minHeight = _a.minHeight, onResize = _a.onResize;
    var _b = useState(null), dragOffset = _b[0], setDragOffset = _b[1];
    var onResizeStable = useStableEventHandler(onResize);
    var containerRef = useRef(null);
    var onMouseDown = function (event) {
        if (event.button !== 0 || !containerRef.current) {
            return;
        }
        var containerBottom = containerRef.current.getBoundingClientRect().bottom;
        setDragOffset(containerBottom - event.clientY);
    };
    useEffect(function () {
        if (dragOffset === null || !containerRef.current) {
            return;
        }
        var container = containerRef.current;
        var onMouseMove = function (event) {
            var top = container.getBoundingClientRect().top;
            var cursor = event.clientY;
            onResizeStable(Math.max(cursor + dragOffset - top, minHeight));
        };
        var onMouseUp = function () {
            setDragOffset(null);
        };
        document.body.classList.add(styles['resize-active']);
        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        return function () {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            document.body.classList.remove(styles['resize-active']);
        };
    }, [dragOffset, minHeight, onResizeStable]);
    return (React.createElement("div", { ref: containerRef, className: styles['resizable-box'], style: { height: height } },
        children,
        React.createElement("span", { className: styles['resizable-box-handle'], onMouseDown: onMouseDown })));
}
//# sourceMappingURL=index.js.map