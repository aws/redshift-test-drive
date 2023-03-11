// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import InternalSegmentedControl from '../segmented-control/internal';
import styles from './styles.css.js';
export default function ModeSwitcher(_a) {
    var i18nStrings = _a.i18nStrings, mode = _a.mode, onChange = _a.onChange;
    return (React.createElement(InternalSegmentedControl, { className: styles['mode-switch'], selectedId: mode, options: [
            { id: 'relative', text: i18nStrings.relativeModeTitle },
            { id: 'absolute', text: i18nStrings.absoluteModeTitle },
        ], onChange: function (e) { return onChange(e.detail.selectedId); } }));
}
//# sourceMappingURL=mode-switcher.js.map