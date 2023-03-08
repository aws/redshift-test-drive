import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import clsx from 'clsx';
import { getBaseProps } from '../internal/base-component';
import InternalAlert from '../alert/internal';
import InternalBox from '../box/internal';
import styles from './styles.css.js';
import LiveRegion from '../internal/components/live-region';
export default function InternalForm(_a) {
    var children = _a.children, header = _a.header, errorText = _a.errorText, errorIconAriaLabel = _a.errorIconAriaLabel, actions = _a.actions, secondaryActions = _a.secondaryActions, __internalRootRef = _a.__internalRootRef, props = __rest(_a, ["children", "header", "errorText", "errorIconAriaLabel", "actions", "secondaryActions", "__internalRootRef"]);
    var baseProps = getBaseProps(props);
    return (React.createElement("div", __assign({}, baseProps, { ref: __internalRootRef, className: clsx(styles.root, baseProps.className) }),
        header && React.createElement("div", { className: styles.header }, header),
        children && React.createElement("div", { className: styles.content }, children),
        errorText && (React.createElement(InternalBox, { margin: { top: 'l' } },
            React.createElement(InternalAlert, { type: "error", statusIconAriaLabel: errorIconAriaLabel },
                React.createElement("div", { className: styles.error }, errorText)))),
        (actions || secondaryActions) && (React.createElement("div", { className: styles.footer },
            React.createElement("div", { className: styles['actions-section'] },
                actions && React.createElement("div", { className: styles.actions }, actions),
                secondaryActions && React.createElement("div", { className: styles['secondary-actions'] }, secondaryActions)))),
        errorText && (React.createElement(LiveRegion, { assertive: true },
            errorIconAriaLabel,
            ", ",
            errorText))));
}
//# sourceMappingURL=internal.js.map