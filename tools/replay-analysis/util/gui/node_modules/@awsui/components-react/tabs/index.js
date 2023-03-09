import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useState } from 'react';
import { getBaseProps } from '../internal/base-component';
import { fireNonCancelableEvent } from '../internal/events';
import InternalContainer from '../container/internal';
import clsx from 'clsx';
import styles from './styles.css.js';
import { getTabElementId, TabHeaderBar } from './tab-header-bar';
import { useControllable } from '../internal/hooks/use-controllable';
import { applyDisplayName } from '../internal/utils/apply-display-name';
import useBaseComponent from '../internal/hooks/use-base-component';
import { checkSafeUrl } from '../internal/utils/check-safe-url';
import useFocusVisible from '../internal/hooks/focus-visible';
var lastGeneratedId = 0;
export var nextGeneratedId = function () { return "awsui-tabs-".concat(lastGeneratedId++, "-").concat(Math.round(Math.random() * 10000)); };
function firstEnabledTab(tabs) {
    var enabledTabs = tabs.filter(function (tab) { return !tab.disabled; });
    if (enabledTabs.length > 0) {
        return enabledTabs[0];
    }
    return null;
}
export default function Tabs(_a) {
    var _b, _c;
    var tabs = _a.tabs, _d = _a.variant, variant = _d === void 0 ? 'default' : _d, onChange = _a.onChange, controlledTabId = _a.activeTabId, ariaLabel = _a.ariaLabel, ariaLabelledby = _a.ariaLabelledby, _e = _a.disableContentPaddings, disableContentPaddings = _e === void 0 ? false : _e, i18nStrings = _a.i18nStrings, rest = __rest(_a, ["tabs", "variant", "onChange", "activeTabId", "ariaLabel", "ariaLabelledby", "disableContentPaddings", "i18nStrings"]);
    for (var _i = 0, tabs_1 = tabs; _i < tabs_1.length; _i++) {
        var tab = tabs_1[_i];
        checkSafeUrl('Tabs', tab.href);
    }
    var __internalRootRef = useBaseComponent('Tabs').__internalRootRef;
    var idNamespace = useState(function () { return nextGeneratedId(); })[0];
    var _f = useControllable(controlledTabId, onChange, (_c = (_b = firstEnabledTab(tabs)) === null || _b === void 0 ? void 0 : _b.id) !== null && _c !== void 0 ? _c : '', {
        componentName: 'Tabs',
        controlledProp: 'activeTabId',
        changeHandler: 'onChange'
    }), activeTabId = _f[0], setActiveTabId = _f[1];
    var baseProps = getBaseProps(rest);
    var focusVisible = useFocusVisible();
    var content = function () {
        var _a;
        var selectedTab = tabs.filter(function (tab) { return tab.id === activeTabId; })[0];
        var renderContent = function (tab) {
            var _a;
            var isTabSelected = tab === selectedTab;
            var classes = clsx((_a = {},
                _a[styles['tabs-content']] = true,
                _a[styles['tabs-content-active']] = isTabSelected,
                _a));
            var contentAttributes = __assign(__assign({}, focusVisible), { className: classes, role: 'tabpanel', id: "".concat(idNamespace, "-").concat(tab.id, "-panel"), key: "".concat(idNamespace, "-").concat(tab.id, "-panel"), tabIndex: 0, 'aria-labelledby': getTabElementId({ namespace: idNamespace, tabId: tab.id }) });
            var isContentShown = isTabSelected && !selectedTab.disabled;
            return React.createElement("div", __assign({}, contentAttributes), isContentShown && selectedTab.content);
        };
        return (React.createElement("div", { className: clsx(variant === 'container' ? styles['tabs-container-content-wrapper'] : styles['tabs-content-wrapper'], (_a = {},
                _a[styles['with-paddings']] = !disableContentPaddings,
                _a)) }, tabs.map(renderContent)));
    };
    var header = (React.createElement(TabHeaderBar, { activeTabId: activeTabId, variant: variant, idNamespace: idNamespace, ariaLabel: ariaLabel, ariaLabelledby: ariaLabelledby, tabs: tabs, onChange: function (changeDetail) {
            setActiveTabId(changeDetail.activeTabId);
            fireNonCancelableEvent(onChange, changeDetail);
        }, i18nStrings: i18nStrings }));
    if (variant === 'container') {
        return (React.createElement(InternalContainer, __assign({ header: header, disableHeaderPaddings: true }, baseProps, { className: clsx(baseProps.className, styles.root), __internalRootRef: __internalRootRef, disableContentPaddings: true }), content()));
    }
    return (React.createElement("div", __assign({}, baseProps, { className: clsx(baseProps.className, styles.root, styles.tabs), ref: __internalRootRef }),
        header,
        content()));
}
applyDisplayName(Tabs, 'Tabs');
//# sourceMappingURL=index.js.map