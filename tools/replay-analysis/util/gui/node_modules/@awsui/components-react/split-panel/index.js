import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useState, useEffect, useLayoutEffect, useRef } from 'react';
import clsx from 'clsx';
import { InternalButton } from '../button/internal';
import { getBaseProps } from '../internal/base-component';
import { useSplitPanelContext } from '../internal/context/split-panel-context';
import useFocusVisible from '../internal/hooks/focus-visible';
import { applyDisplayName } from '../internal/utils/apply-display-name';
import ResizeHandler from './icons/resize-handler';
import PreferencesModal from './preferences-modal';
import { usePointerEvents } from './utils/use-pointer-events';
import { useKeyboardEvents } from './utils/use-keyboard-events';
import styles from './styles.css.js';
import useBaseComponent from '../internal/hooks/use-base-component';
import { useMergeRefs } from '../internal/hooks/use-merge-refs';
import { AppLayoutContext } from '../internal/context/app-layout-context';
import { getLimitedValue } from './utils/size-utils';
import { Transition } from '../internal/components/transition';
import { useEffectOnUpdate } from '../internal/hooks/use-effect-on-update';
import { useVisualRefresh } from '../internal/hooks/use-visual-mode';
import { useUniqueId } from '../internal/hooks/use-unique-id';
import { SplitPanelContentSide } from './side';
import { SplitPanelContentBottom } from './bottom';
var MIN_HEIGHT = 160;
var MIN_WIDTH = 280;
export default function SplitPanel(_a) {
    var header = _a.header, children = _a.children, _b = _a.hidePreferencesButton, hidePreferencesButton = _b === void 0 ? false : _b, _c = _a.closeBehavior, closeBehavior = _c === void 0 ? 'collapse' : _c, i18nStrings = _a.i18nStrings, restProps = __rest(_a, ["header", "children", "hidePreferencesButton", "closeBehavior", "i18nStrings"]);
    var isRefresh = useVisualRefresh();
    var __internalRootRef = useBaseComponent('SplitPanel').__internalRootRef;
    var _d = useSplitPanelContext(), size = _d.size, getMaxWidth = _d.getMaxWidth, getMaxHeight = _d.getMaxHeight, position = _d.position, topOffset = _d.topOffset, bottomOffset = _d.bottomOffset, rightOffset = _d.rightOffset, contentWidthStyles = _d.contentWidthStyles, isOpen = _d.isOpen, isForcedPosition = _d.isForcedPosition, lastInteraction = _d.lastInteraction, onPreferencesChange = _d.onPreferencesChange, onResize = _d.onResize, onToggle = _d.onToggle, reportSize = _d.reportSize, setSplitPanelToggle = _d.setSplitPanelToggle;
    var baseProps = getBaseProps(restProps);
    var focusVisible = useFocusVisible();
    var _e = useState(false), isPreferencesOpen = _e[0], setPreferencesOpen = _e[1];
    var _f = useState(0), relativeSize = _f[0], setRelativeSize = _f[1];
    var _g = useState(size), maxSize = _g[0], setMaxSize = _g[1];
    var minSize = position === 'bottom' ? MIN_HEIGHT : MIN_WIDTH;
    var cappedSize = getLimitedValue(minSize, size, maxSize);
    var appLayoutMaxWidth = isRefresh && position === 'bottom' ? contentWidthStyles : undefined;
    useEffect(function () {
        setSplitPanelToggle({ displayed: closeBehavior === 'collapse', ariaLabel: i18nStrings.openButtonAriaLabel });
    }, [setSplitPanelToggle, i18nStrings.openButtonAriaLabel, closeBehavior]);
    useEffect(function () {
        // effects are called inside out in the components tree
        // wait one frame to allow app-layout to complete its calculations
        var handle = requestAnimationFrame(function () {
            var maxSize = position === 'bottom' ? getMaxHeight() : getMaxWidth();
            setRelativeSize((size / maxSize) * 100);
            setMaxSize(maxSize);
        });
        return function () { return cancelAnimationFrame(handle); };
    }, [size, position, getMaxHeight, getMaxWidth]);
    useEffect(function () {
        reportSize(cappedSize);
    }, [reportSize, cappedSize]);
    useEffect(function () {
        var handler = function () { return setMaxSize(position === 'bottom' ? getMaxHeight() : getMaxWidth()); };
        window.addEventListener('resize', handler);
        return function () { return window.removeEventListener('resize', handler); };
    }, [position, getMaxWidth, getMaxHeight]);
    var setSidePanelWidth = function (width) {
        var maxWidth = getMaxWidth();
        var size = getLimitedValue(MIN_WIDTH, width, maxWidth);
        if (isOpen && maxWidth >= MIN_WIDTH) {
            onResize({ size: size });
        }
    };
    var setBottomPanelHeight = function (height) {
        var maxHeight = getMaxHeight();
        var size = getLimitedValue(MIN_HEIGHT, height, maxHeight);
        if (isOpen && maxHeight >= MIN_HEIGHT) {
            onResize({ size: size });
        }
    };
    var splitPanelRefObject = useRef(null);
    var handleRef = useRef(null);
    var sizeControlProps = {
        position: position,
        splitPanelRef: splitPanelRefObject,
        handleRef: handleRef,
        setSidePanelWidth: setSidePanelWidth,
        setBottomPanelHeight: setBottomPanelHeight
    };
    var onSliderPointerDown = usePointerEvents(sizeControlProps);
    var onKeyDown = useKeyboardEvents(sizeControlProps);
    var toggleRef = useRef(null);
    var closeRef = useRef(null);
    var preferencesRef = useRef(null);
    useEffectOnUpdate(function () {
        var _a, _b, _c;
        switch (lastInteraction === null || lastInteraction === void 0 ? void 0 : lastInteraction.type) {
            case 'open':
                return (_a = handleRef.current) === null || _a === void 0 ? void 0 : _a.focus();
            case 'close':
                return (_b = toggleRef.current) === null || _b === void 0 ? void 0 : _b.focus();
            case 'position':
                return (_c = preferencesRef.current) === null || _c === void 0 ? void 0 : _c.focus();
            default:
                return;
        }
    }, [lastInteraction]);
    var wrappedChildren = (React.createElement(AppLayoutContext.Provider, { value: {
            stickyOffsetTop: topOffset,
            stickyOffsetBottom: bottomOffset,
            hasBreadcrumbs: false
        } }, children));
    var panelHeaderId = useUniqueId('split-panel-header');
    var wrappedHeader = (React.createElement("div", { className: styles.header, style: appLayoutMaxWidth },
        React.createElement("h2", { className: styles['header-text'], id: panelHeaderId }, header),
        React.createElement("div", { className: styles['header-actions'] },
            !hidePreferencesButton && isOpen && (React.createElement(React.Fragment, null,
                React.createElement(InternalButton, { className: styles['preferences-button'], iconName: "settings", variant: "icon", onClick: function () { return setPreferencesOpen(true); }, formAction: "none", ariaLabel: i18nStrings.preferencesTitle, ref: preferencesRef }),
                React.createElement("span", { className: styles.divider }))),
            isOpen ? (React.createElement(InternalButton, { className: styles['close-button'], iconName: isRefresh && closeBehavior === 'collapse' ? (position === 'side' ? 'angle-right' : 'angle-down') : 'close', variant: "icon", onClick: onToggle, formAction: "none", ariaLabel: i18nStrings.closeButtonAriaLabel, ref: closeRef, ariaExpanded: isOpen })) : position === 'side' ? null : (React.createElement(InternalButton, { className: styles['open-button'], iconName: "angle-up", variant: "icon", formAction: "none", ariaLabel: i18nStrings.openButtonAriaLabel, ref: toggleRef, ariaExpanded: isOpen })))));
    var resizeHandle = (React.createElement("div", __assign({ ref: handleRef, role: "slider", tabIndex: 0, "aria-label": i18nStrings.resizeHandleAriaLabel, "aria-valuemax": 100, "aria-valuemin": 0, "aria-valuenow": relativeSize, className: clsx(styles.slider, styles["slider-".concat(position)]), onKeyDown: onKeyDown, onPointerDown: onSliderPointerDown }, focusVisible),
        React.createElement(ResizeHandler, { className: clsx(styles['slider-icon'], styles["slider-icon-".concat(position)]) })));
    /*
      This effect forces the browser to recalculate the layout
      whenever the split panel might have moved.
  
      This is needed as a workaround for a bug in Safari, which does
      not automatically calculate the new position of the split panel
      _content_ when the split panel moves.
    */
    useLayoutEffect(function () {
        var root = __internalRootRef.current;
        if (root) {
            var property = 'transform';
            var temporaryValue = 'translateZ(0)';
            var valueBefore = root.style[property];
            root.style[property] = temporaryValue;
            // This line forces the browser to recalculate the layout
            void root.offsetHeight;
            root.style[property] = valueBefore;
        }
    }, [rightOffset, __internalRootRef]);
    var mergedRef = useMergeRefs(splitPanelRefObject, __internalRootRef);
    if (closeBehavior === 'hide' && !isOpen) {
        return React.createElement(React.Fragment, null);
    }
    /**
     * The AppLayout factor moved the circular buttons out of the
     * SplitPanel and into the Tools component. This conditional
     * is still needed for the early return to prevent execution
     * of the following code.
     */
    if (isRefresh && !isOpen && position === 'side') {
        return React.createElement(React.Fragment, null);
    }
    return (React.createElement(Transition, { "in": isOpen !== null && isOpen !== void 0 ? isOpen : false }, function (state, transitioningElementRef) { return (React.createElement(React.Fragment, null,
        position === 'side' && (React.createElement(SplitPanelContentSide, { resizeHandle: resizeHandle, baseProps: baseProps, isOpen: isOpen, splitPanelRef: mergedRef, cappedSize: cappedSize, onToggle: onToggle, i18nStrings: i18nStrings, toggleRef: toggleRef, header: wrappedHeader, panelHeaderId: panelHeaderId }, wrappedChildren)),
        position === 'bottom' && (React.createElement(SplitPanelContentBottom, { resizeHandle: resizeHandle, baseProps: baseProps, isOpen: isOpen, splitPanelRef: mergedRef, cappedSize: cappedSize, onToggle: onToggle, header: wrappedHeader, panelHeaderId: panelHeaderId, state: state, transitioningElementRef: transitioningElementRef, appLayoutMaxWidth: appLayoutMaxWidth }, wrappedChildren)),
        isPreferencesOpen && (React.createElement(PreferencesModal, { visible: true, preferences: { position: position }, disabledSidePosition: position === 'bottom' && isForcedPosition, isRefresh: isRefresh, i18nStrings: {
                header: i18nStrings.preferencesTitle,
                confirm: i18nStrings.preferencesConfirm,
                cancel: i18nStrings.preferencesCancel,
                positionLabel: i18nStrings.preferencesPositionLabel,
                positionDescription: i18nStrings.preferencesPositionDescription,
                positionBottom: i18nStrings.preferencesPositionBottom,
                positionSide: i18nStrings.preferencesPositionSide
            }, onConfirm: function (preferences) {
                onPreferencesChange(__assign({}, preferences));
                setPreferencesOpen(false);
            }, onDismiss: function () {
                setPreferencesOpen(false);
            } })))); }));
}
applyDisplayName(SplitPanel, 'SplitPanel');
//# sourceMappingURL=index.js.map