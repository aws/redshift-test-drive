// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React from 'react';
import clsx from 'clsx';
import styles from './styles.css.js';
import DropdownStatus from '../dropdown-status/index.js';
import LiveRegion from '../live-region/index.js';
var DropdownFooter = function (_a) {
    var _b;
    var content = _a.content, _c = _a.hasItems, hasItems = _c === void 0 ? true : _c;
    return (React.createElement("div", { className: clsx(styles.root, (_b = {}, _b[styles.hidden] = content === null, _b[styles['no-items']] = !hasItems, _b)) },
        React.createElement(LiveRegion, { visible: true, tagName: "div" }, content && React.createElement(DropdownStatus, null, content))));
};
export default DropdownFooter;
//# sourceMappingURL=index.js.map