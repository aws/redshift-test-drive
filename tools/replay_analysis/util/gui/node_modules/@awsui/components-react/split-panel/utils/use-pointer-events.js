// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import { useCallback } from 'react';
import styles from '../styles.css.js';
export var usePointerEvents = function (_a) {
    var position = _a.position, splitPanelRef = _a.splitPanelRef, handleRef = _a.handleRef, setSidePanelWidth = _a.setSidePanelWidth, setBottomPanelHeight = _a.setBottomPanelHeight;
    var onDocumentPointerMove = useCallback(function (event) {
        if (!splitPanelRef || !splitPanelRef.current || !handleRef || !handleRef.current) {
            return;
        }
        if (position === 'side') {
            var mouseClientX = event.clientX;
            // The handle offset aligns the cursor with the middle of the resize handle.
            var handleOffset = handleRef.current.getBoundingClientRect().width / 2;
            var width = splitPanelRef.current.getBoundingClientRect().right - mouseClientX + handleOffset;
            setSidePanelWidth(width);
        }
        else {
            var mouseClientY = event.clientY;
            // The handle offset aligns the cursor with the middle of the resize handle.
            var handleOffset = handleRef.current.getBoundingClientRect().height / 2;
            var height = splitPanelRef.current.getBoundingClientRect().bottom - mouseClientY + handleOffset;
            setBottomPanelHeight(height);
        }
    }, [position, splitPanelRef, handleRef, setSidePanelWidth, setBottomPanelHeight]);
    var onDocumentPointerUp = useCallback(function () {
        document.body.classList.remove(styles['resize-active']);
        document.body.classList.remove(styles["resize-".concat(position)]);
        document.removeEventListener('pointerup', onDocumentPointerUp);
        document.removeEventListener('pointermove', onDocumentPointerMove);
    }, [onDocumentPointerMove, position]);
    var onSliderPointerDown = useCallback(function () {
        document.body.classList.add(styles['resize-active']);
        document.body.classList.add(styles["resize-".concat(position)]);
        document.addEventListener('pointerup', onDocumentPointerUp);
        document.addEventListener('pointermove', onDocumentPointerMove);
    }, [onDocumentPointerMove, onDocumentPointerUp, position]);
    return onSliderPointerDown;
};
//# sourceMappingURL=use-pointer-events.js.map