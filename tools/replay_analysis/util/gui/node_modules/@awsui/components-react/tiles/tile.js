// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import clsx from 'clsx';
import React, { useRef } from 'react';
import RadioButton from '../radio-group/radio-button';
import styles from './styles.css.js';
import { fireNonCancelableEvent } from '../internal/events';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
export var Tile = React.forwardRef(function (_a, forwardedRef) {
    var _b, _c, _d, _e, _f;
    var item = _a.item, selected = _a.selected, name = _a.name, breakpoint = _a.breakpoint, onChange = _a.onChange;
    var internalRef = useRef(null);
    var controlId = item.controlId || "".concat(name, "-value-").concat(item.value);
    var mergedRef = useMergeRefs(internalRef, forwardedRef);
    return (React.createElement("div", { className: clsx(styles['tile-container'], (_b = {}, _b[styles['has-metadata']] = item.description || item.image, _b), (_c = {}, _c[styles.selected] = selected, _c), (_d = {}, _d[styles.disabled] = !!item.disabled, _d), styles["breakpoint-".concat(breakpoint)]), "data-value": item.value, onClick: function () {
            var _a;
            if (item.disabled) {
                return;
            }
            (_a = internalRef.current) === null || _a === void 0 ? void 0 : _a.focus();
            if (!selected) {
                fireNonCancelableEvent(onChange, { value: item.value });
            }
        } },
        React.createElement("div", { className: clsx(styles.control, (_e = {}, _e[styles['no-image']] = !item.image, _e)) },
            React.createElement(RadioButton, { checked: selected, ref: mergedRef, name: name, value: item.value, label: item.label, description: item.description, disabled: item.disabled, controlId: controlId })),
        item.image && React.createElement("div", { className: clsx(styles.image, (_f = {}, _f[styles.disabled] = !!item.disabled, _f)) }, item.image)));
});
//# sourceMappingURL=tile.js.map