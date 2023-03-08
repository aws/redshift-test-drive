// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useCallback, useEffect, useRef } from 'react';
import clsx from 'clsx';
import { KeyCode } from '../internal/keycode';
import { useUniqueId } from '../internal/hooks/use-unique-id';
import { InternalButton } from '../button/internal';
import FocusLock from '../internal/components/focus-lock';
import styles from './styles.css.js';
export default function PopoverBody(_a) {
    var _b, _c;
    var showDismissButton = _a.dismissButton, dismissAriaLabel = _a.dismissAriaLabel, header = _a.header, children = _a.children, onDismiss = _a.onDismiss, variant = _a.variant, overflowVisible = _a.overflowVisible, className = _a.className, ariaLabelledby = _a.ariaLabelledby;
    var labelledById = useUniqueId('awsui-popover-');
    var dismissButtonFocused = useRef(false);
    var dismissButtonRef = useRef(null);
    var onKeyDown = useCallback(function (event) {
        if (event.keyCode === KeyCode.escape) {
            onDismiss();
        }
    }, [onDismiss]);
    // Implement our own auto-focus rather than using FocusLock's,
    // because we also want to focus the dismiss button when it
    // is added dyamically (e.g. in chart popovers)
    useEffect(function () {
        var _a;
        if (showDismissButton && !dismissButtonFocused.current) {
            (_a = dismissButtonRef.current) === null || _a === void 0 ? void 0 : _a.focus({ preventScroll: true });
        }
        dismissButtonFocused.current = showDismissButton;
    }, [showDismissButton]);
    var dismissButton = (showDismissButton !== null && showDismissButton !== void 0 ? showDismissButton : null) && (React.createElement("div", { className: styles.dismiss },
        React.createElement(InternalButton, { variant: "icon", formAction: "none", iconName: "close", className: styles['dismiss-control'], ariaLabel: dismissAriaLabel, onClick: function () { return onDismiss(); }, ref: dismissButtonRef })));
    return (React.createElement("div", { className: clsx(styles.body, className, (_b = {},
            _b[styles['body-overflow-visible']] = overflowVisible === 'both',
            _b)), role: header ? 'dialog' : undefined, onKeyDown: onKeyDown, "aria-modal": showDismissButton && variant !== 'annotation' ? true : undefined, "aria-labelledby": ariaLabelledby !== null && ariaLabelledby !== void 0 ? ariaLabelledby : (header ? labelledById : undefined) },
        React.createElement(FocusLock, { disabled: variant === 'annotation' || !showDismissButton, autoFocus: false },
            header && (React.createElement("div", { className: clsx(styles['header-row'], showDismissButton && styles['has-dismiss']) },
                dismissButton,
                React.createElement("div", { className: styles.header, id: labelledById },
                    React.createElement("h2", null, header)))),
            React.createElement("div", { className: !header && showDismissButton ? styles['has-dismiss'] : undefined },
                !header && dismissButton,
                React.createElement("div", { className: clsx(styles.content, (_c = {}, _c[styles['content-overflow-visible']] = !!overflowVisible, _c)) }, children)))));
}
//# sourceMappingURL=body.js.map