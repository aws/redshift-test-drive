import { __spreadArray } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useState } from 'react';
import InternalBox from '../box/internal';
import { InternalButton } from '../button/internal';
import InternalCheckbox from '../checkbox/internal';
import InternalColumnLayout from '../column-layout/internal';
import InternalFormField from '../form-field/internal';
import InternalModal from '../modal/internal';
import InternalSelect from '../select/internal';
import InternalSpaceBetween from '../space-between/internal';
import { FormFieldContext } from '../internal/context/form-field-context';
import { LightThemes, DarkThemes } from './ace-themes';
function filterThemes(allThemes, available) {
    if (!available) {
        return allThemes;
    }
    return allThemes.filter(function (theme) { return available.indexOf(theme.value) > -1; });
}
export default (function (props) {
    var _a, _b, _c, _d, _e, _f;
    var _g = useState((_b = (_a = props.preferences) === null || _a === void 0 ? void 0 : _a.wrapLines) !== null && _b !== void 0 ? _b : true), wrapLines = _g[0], setWrapLines = _g[1];
    var _h = useState((_d = (_c = props.preferences) === null || _c === void 0 ? void 0 : _c.theme) !== null && _d !== void 0 ? _d : props.defaultTheme), theme = _h[0], setTheme = _h[1];
    var themeOptions = [
        {
            label: props.i18nStrings.lightThemes,
            options: filterThemes(LightThemes, (_e = props.themes) === null || _e === void 0 ? void 0 : _e.light)
        },
        {
            label: props.i18nStrings.darkThemes,
            options: filterThemes(DarkThemes, (_f = props.themes) === null || _f === void 0 ? void 0 : _f.dark)
        },
    ];
    var _j = useState(function () { return __spreadArray(__spreadArray([], LightThemes, true), DarkThemes, true).filter(function (t) { return t.value === theme; })[0]; }), selectedThemeOption = _j[0], setSelectedThemeOption = _j[1];
    var onThemeSelected = function (e) {
        setTheme(e.detail.selectedOption.value);
        setSelectedThemeOption(e.detail.selectedOption);
    };
    return (React.createElement(FormFieldContext.Provider, { value: {} },
        React.createElement(InternalModal, { size: "medium", visible: true, onDismiss: props.onDismiss, header: props.i18nStrings.header, closeAriaLabel: props.i18nStrings.cancel, footer: React.createElement(InternalBox, { float: "right" },
                React.createElement(InternalSpaceBetween, { direction: "horizontal", size: "xs" },
                    React.createElement(InternalButton, { onClick: props.onDismiss }, props.i18nStrings.cancel),
                    React.createElement(InternalButton, { onClick: function () { return props.onConfirm({ wrapLines: wrapLines, theme: theme }); }, variant: "primary" }, props.i18nStrings.confirm))) },
            React.createElement(InternalColumnLayout, { columns: 2, variant: "text-grid" },
                React.createElement("div", null,
                    React.createElement(InternalCheckbox, { checked: wrapLines, onChange: function (e) { return setWrapLines(e.detail.checked); } }, props.i18nStrings.wrapLines)),
                React.createElement("div", null,
                    React.createElement(InternalFormField, { label: props.i18nStrings.theme },
                        React.createElement(InternalSelect, { selectedOption: selectedThemeOption, onChange: onThemeSelected, options: themeOptions, filteringType: "auto" })))))));
});
//# sourceMappingURL=preferences-modal.js.map