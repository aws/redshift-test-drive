import { __assign, __rest } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { createContext, useCallback, useEffect, useLayoutEffect, useImperativeHandle, useRef, useState, useContext, } from 'react';
import { fireNonCancelableEvent } from '../../internal/events';
import { getSplitPanelPosition } from './split-panel';
import { useControllable } from '../../internal/hooks/use-controllable';
import { useMobile } from '../../internal/hooks/use-mobile';
import { useContainerQuery } from '../../internal/hooks/container-queries';
import { getSplitPanelDefaultSize } from '../../split-panel/utils/size-utils';
import styles from './styles.css.js';
import { isDevelopment } from '../../internal/is-development';
import { warnOnce } from '../../internal/logging';
import { applyDefaults } from '../defaults';
import { useFocusControl } from '../utils/use-focus-control';
import { useObservedElement } from '../utils/use-observed-element';
import { AppLayoutContext } from '../../internal/context/app-layout-context';
/**
 * The default values are destructured in the context instantiation to
 * prevent downstream Typescript errors. This could likely be replaced
 * by a context interface definition that extends the AppLayout interface.
 */
var AppLayoutInternalsContext = createContext(null);
export function useAppLayoutInternals() {
    var ctx = useContext(AppLayoutInternalsContext);
    if (!ctx) {
        throw new Error('Invariant violation: this context is only available inside app layout');
    }
    return ctx;
}
export var AppLayoutInternalsProvider = React.forwardRef(function (_a, forwardRef) {
    var _b, _c, _d;
    var toolsHide = _a.toolsHide, controlledToolsOpen = _a.toolsOpen, navigationHide = _a.navigationHide, controlledNavigationOpen = _a.navigationOpen, _e = _a.contentType, contentType = _e === void 0 ? 'default' : _e, _f = _a.headerSelector, headerSelector = _f === void 0 ? '#b #h' : _f, _g = _a.footerSelector, footerSelector = _g === void 0 ? '#b #h' : _g, children = _a.children, splitPanel = _a.splitPanel, props = __rest(_a, ["toolsHide", "toolsOpen", "navigationHide", "navigationOpen", "contentType", "headerSelector", "footerSelector", "children", "splitPanel"]);
    var isMobile = useMobile();
    if (isDevelopment) {
        if (controlledToolsOpen && toolsHide) {
            warnOnce('AppLayout', "You have enabled both the `toolsOpen` prop and the `toolsHide` prop. This is not supported. Set `toolsOpen` to `false` when you set `toolsHide` to `true`.");
        }
    }
    /**
     * The overlap height has a default set in CSS but can also be dynamically overridden
     * for content types (such as Table and Wizard) that have variable size content in the overlap.
     * If a child component utilizes a sticky header the hasStickyBackground property will determine
     * if the background remains in the same vertical position.
     */
    var _h = useState(0), dynamicOverlapHeight = _h[0], setDynamicOverlapHeight = _h[1];
    var _j = useState(false), hasStickyBackground = _j[0], setHasStickyBackground = _j[1];
    /**
     * Set the default values for minimum and maximum content width.
     */
    var geckoMaxCssLength = ((1 << 30) - 1) / 60;
    var halfGeckoMaxCssLength = geckoMaxCssLength / 2;
    // CSS lengths in Gecko are limited to at most (1<<30)-1 app units (Gecko uses 60 as app unit).
    // Limit the maxContentWidth to the half of the upper boundary (≈4230^2) to be on the safe side.
    var maxContentWidth = props.maxContentWidth && props.maxContentWidth > halfGeckoMaxCssLength
        ? halfGeckoMaxCssLength
        : (_b = props.maxContentWidth) !== null && _b !== void 0 ? _b : 0;
    var minContentWidth = (_c = props.minContentWidth) !== null && _c !== void 0 ? _c : 280;
    /**
     * Determine the default state of the Navigation and Tools drawers.
     * Mobile viewports should be closed by default under all circumstances.
     * If the navigationOpen prop has been set then that should take precedence
     * over the contentType prop. Desktop viewports that do not have the
     * navigationOpen or contentType props set will use the default contentType.
     */
    var contentTypeDefaults = applyDefaults(contentType, { maxContentWidth: maxContentWidth, minContentWidth: minContentWidth }, true);
    /**
     * The useControllable hook will set the default value and manage either
     * the controlled or uncontrolled state of the Navigation drawer. The logic
     * for determining the default state is colocated with the Navigation component.
     *
     * The callback that will be passed to the Navigation and AppBar
     * components to handle the click events that will change the state
     * of the Navigation drawer. It will set the Navigation state with the
     * useControllable hook and also fire the onNavigationChange function to
     * emit the state change.
     */
    var _k = useControllable(controlledNavigationOpen, props.onNavigationChange, isMobile ? false : contentTypeDefaults.navigationOpen, { componentName: 'AppLayout', controlledProp: 'navigationOpen', changeHandler: 'onNavigationChange' }), _l = _k[0], isNavigationOpen = _l === void 0 ? false : _l, setIsNavigationOpen = _k[1];
    var handleNavigationClick = useCallback(function handleNavigationChange(isOpen) {
        setIsNavigationOpen(isOpen);
        fireNonCancelableEvent(props.onNavigationChange, { open: isOpen });
    }, [props.onNavigationChange, setIsNavigationOpen]);
    /**
     * The useControllable hook will set the default value and manage either
     * the controlled or uncontrolled state of the Tools drawer. The logic
     * for determining the default state is colocated with the Tools component.
     *
     * The callback that will be passed to the Navigation and AppBar
     * components to handle the click events that will change the state
     * of the Tools drawer. It will set the Tools state with the
     * useControllable hook and also fire the onToolsChange function to
     * emit the state change.
     */
    var toolsWidth = (_d = props.toolsWidth) !== null && _d !== void 0 ? _d : 290;
    var hasDefaultToolsWidth = props.toolsWidth === undefined;
    var _m = useControllable(controlledToolsOpen, props.onToolsChange, isMobile ? false : contentTypeDefaults.toolsOpen, { componentName: 'AppLayout', controlledProp: 'toolsOpen', changeHandler: 'onToolsChange' }), _o = _m[0], isToolsOpen = _o === void 0 ? false : _o, setIsToolsOpen = _m[1];
    var toolsFocusControl = useFocusControl(isToolsOpen, true);
    var handleToolsClick = useCallback(function handleToolsChange(isOpen) {
        setIsToolsOpen(isOpen);
        fireNonCancelableEvent(props.onToolsChange, { open: isOpen });
    }, [props.onToolsChange, setIsToolsOpen]);
    var navigationVisible = !navigationHide && isNavigationOpen;
    var toolsVisible = !toolsHide && isToolsOpen;
    var isAnyPanelOpen = navigationVisible || toolsVisible;
    /**
     * On mobile viewports the navigation and tools drawers are adjusted to a fixed position
     * that consumes 100% of the viewport height and width. The body content could potentially
     * be scrollable underneath the drawer. In order to prevent this a CSS class needs to be
     * added to the document body that sets overflow to hidden.
     */
    useEffect(function handleBodyScroll() {
        if (isMobile && (isNavigationOpen || isToolsOpen)) {
            document.body.classList.add(styles['block-body-scroll']);
        }
        else {
            document.body.classList.remove(styles['block-body-scroll']);
        }
        // Ensure the CSS class is removed from the body on side effect cleanup
        return function cleanup() {
            document.body.classList.remove(styles['block-body-scroll']);
        };
    }, [isMobile, isNavigationOpen, isToolsOpen]);
    /**
     * The useImperativeHandle hook in conjunction with the forwardRef function
     * in the AppLayout component definition expose the following callable
     * functions to component consumers when they put a ref as a property on
     * their component implementation.
     */
    useImperativeHandle(forwardRef, function createImperativeHandle() {
        return {
            closeNavigationIfNecessary: function () {
                isMobile && handleNavigationClick(false);
            },
            openTools: function () {
                handleToolsClick(true);
            },
            focusToolsClose: toolsFocusControl.setFocus
        };
    }, [isMobile, handleNavigationClick, handleToolsClick, toolsFocusControl.setFocus]);
    /**
     * Query the DOM for the header and footer elements based on the selectors provided
     * by the properties and pass the heights to the custom property definitions.
     */
    var headerHeight = useObservedElement(headerSelector);
    var footerHeight = useObservedElement(footerSelector);
    /**
     * Set the default values for the minimum and maximum Split Panel width when it is
     * in the side position. The useLayoutEffect will compute the available space in the
     * DOM for the Split Panel given the current state. The minimum and maximum
     * widths will potentially trigger a side effect that will put the Split Panel into
     * a forced position on the bottom.
     */
    var splitPanelMinWidth = 280;
    var _p = useState(splitPanelMinWidth), splitPanelMaxWidth = _p[0], setSplitPanelMaxWidth = _p[1];
    /**
     * The useControllable hook will set the default value and manage either
     * the controlled or uncontrolled state of the Split Panel. By default
     * the Split Panel should always be closed on page load.
     *
     * The callback that will be passed to the SplitPanel component
     * to handle the click events that will change the state of the SplitPanel
     * to open or closed given the current state. It will set the isSplitPanelOpen
     * controlled state and fire the onSplitPanelToggle event.
     */
    var _q = useControllable(props.splitPanelOpen, props.onSplitPanelToggle, false, { componentName: 'AppLayout', controlledProp: 'splitPanelOpen', changeHandler: 'onSplitPanelToggle' }), isSplitPanelOpen = _q[0], setIsSplitPanelOpen = _q[1];
    var handleSplitPanelClick = useCallback(function handleSplitPanelChange() {
        setIsSplitPanelOpen(!isSplitPanelOpen);
        fireNonCancelableEvent(props.onSplitPanelToggle, { open: !isSplitPanelOpen });
    }, [props.onSplitPanelToggle, isSplitPanelOpen, setIsSplitPanelOpen]);
    /**
     * The useControllable hook will manage the controlled or uncontrolled
     * state of the splitPanelPreferences. By default the splitPanelPreferences
     * is undefined. When set the object shape should have a single key to indicate
     * either bottom or side position.
     *
     * The callback that will handle changes to the splitPanelPreferences
     * object that will determine if the SplitPanel is rendered either on the
     * bottom of the viewport or within the Tools container.
     */
    var _r = useControllable(props.splitPanelPreferences, props.onSplitPanelPreferencesChange, undefined, {
        componentName: 'AppLayout',
        controlledProp: 'splitPanelPreferences',
        changeHandler: 'onSplitPanelPreferencesChange'
    }), splitPanelPreferences = _r[0], setSplitPanelPreferences = _r[1];
    /**
     * The Split Panel will be in forced (bottom) position if the defined minimum width is
     * greater than the maximum width. In other words, the maximum width is the currently
     * available horizontal space based on all other components that are rendered. If the
     * minimum width exceeds this value then there is not enough horizontal space and we must
     * force it to the bottom position.
     */
    var _s = useState(false), isSplitPanelForcedPosition = _s[0], setSplitPanelForcedPosition = _s[1];
    var splitPanelPosition = getSplitPanelPosition(isSplitPanelForcedPosition, splitPanelPreferences);
    useLayoutEffect(function handleSplitPanelForcePosition() {
        setSplitPanelForcedPosition(splitPanelMinWidth > splitPanelMaxWidth);
    }, [splitPanelMaxWidth, splitPanelMinWidth]);
    /**
     * The useControllable hook will set the default size of the SplitPanel based
     * on the default position set in the splitPanelPreferences. The logic for the
     * default size is contained in the SplitPanel component. The splitPanelControlledSize
     * will be bound to the size property in the SplitPanel context for rendering.
     *
     * The callback that will be passed to the SplitPanel component
     * to handle the resize events that will change the size of the SplitPanel.
     * It will set the splitPanelControlledSize controlled state and fire the
     * onSplitPanelResize event.
     */
    var _t = useState(0), splitPanelReportedSize = _t[0], setSplitPanelReportedSize = _t[1];
    var _u = useState(0), splitPanelReportedHeaderHeight = _u[0], setSplitPanelReportedHeaderHeight = _u[1];
    var _v = useState({
        displayed: false,
        ariaLabel: undefined
    }), splitPanelToggle = _v[0], setSplitPanelToggle = _v[1];
    var splitPanelDisplayed = !!(splitPanelToggle.displayed || isSplitPanelOpen);
    var _w = useControllable(props.splitPanelSize, props.onSplitPanelResize, getSplitPanelDefaultSize(splitPanelPosition), { componentName: 'AppLayout', controlledProp: 'splitPanelSize', changeHandler: 'onSplitPanelResize' }), splitPanelSize = _w[0], setSplitPanelSize = _w[1];
    var handleSplitPanelResize = useCallback(function handleSplitPanelChange(detail) {
        setSplitPanelSize(detail.size);
        fireNonCancelableEvent(props.onSplitPanelResize, detail);
    }, [props.onSplitPanelResize, setSplitPanelSize]);
    var handleSplitPanelPreferencesChange = useCallback(function handleSplitPanelChange(detail) {
        setSplitPanelPreferences(detail);
        fireNonCancelableEvent(props.onSplitPanelPreferencesChange, detail);
    }, [props.onSplitPanelPreferencesChange, setSplitPanelPreferences]);
    /**
     * The Layout element is not necessarily synonymous with the client
     * viewport width. There can be content in the horizontal viewport
     * that exists on either side of the AppLayout. This resize observer
     * will set the custom property of the Layout element width that
     * is used for various horizontal constraints such as the maximum
     * allowed width of the Tools container.
     *
     * The offsetLeft of the Main will return the distance that the
     * Main element has from the left edge of the Layout component.
     * The offsetLeft value can vary based on the presence and state
     * of the Navigation as well as content gaps in the grid definition.
     * This value is used to determine the max width constraint calculation
     * for the Tools container.
     */
    var _x = useContainerQuery(function (rect) { return rect.width; }), layoutContainerQuery = _x[0], layoutElement = _x[1];
    var layoutWidth = layoutContainerQuery !== null && layoutContainerQuery !== void 0 ? layoutContainerQuery : 0;
    var mainElement = useRef(null);
    var _y = useState(0), mainOffsetLeft = _y[0], setMainOffsetLeft = _y[1];
    useLayoutEffect(function handleMainOffsetLeft() {
        var _a, _b;
        setMainOffsetLeft((_b = (_a = mainElement === null || mainElement === void 0 ? void 0 : mainElement.current) === null || _a === void 0 ? void 0 : _a.offsetLeft) !== null && _b !== void 0 ? _b : 0);
    }, [layoutWidth, isNavigationOpen, isToolsOpen, splitPanelReportedSize]);
    useLayoutEffect(function handleSplitPanelMaxWidth() {
        /**
         * Warning! This is a hack! In order to accurately calculate if there is adequate
         * horizontal space for the Split Panel to be in the side position we need two values
         * that are not available in JavaScript.
         *
         * The first is the the content gap on the right which is stored in a design token
         * and applied in the Layout CSS:
         *
         *  $contentGapRight: #{awsui.$space-scaled-2x-xxxl};
         *
         * The second is the width of the element that has the circular buttons for the
         * Tools and Split Panel. This could be suppressed given the state of the Tools
         * drawer returning a zero value. It would, however, be rendered if the Split Panel
         * were to move into the side position. This is calculated in the Tools CSS and
         * the Trigger button CSS with design tokens:
         *
         * padding: awsui.$space-scaled-s awsui.$space-layout-toggle-padding;
         * width: awsui.$space-layout-toggle-diameter;
         *
         * These values will be defined below as static integers that are rough approximations
         * of their computed width when rendered in the DOM, but doubled to ensure adequate
         * spacing for the Split Panel to be in side position.
         */
        var contentGapRight = 80; // Approximately 40px when rendered but doubled for safety
        var toolsFormOffsetWidth = 160; // Approximately 80px when rendered but doubled for safety
        var toolsOffsetWidth = isToolsOpen ? toolsWidth : 0;
        setSplitPanelMaxWidth(layoutWidth - mainOffsetLeft - minContentWidth - contentGapRight - toolsOffsetWidth - toolsFormOffsetWidth);
    }, [isNavigationOpen, isToolsOpen, layoutWidth, mainOffsetLeft, minContentWidth, toolsWidth]);
    /**
     * Because the notifications slot does not give us any direction insight into
     * what the state of the child content is we need to have a mechanism for
     * tracking the height of the notifications and whether or not it has content.
     * The height of the notifications is an integer that will be used as a custom
     * property on the Layout component to determine what the sticky offset should
     * be if there are sticky notifications. This could be any number including
     * zero based on how the child content renders. The hasNotificationsContent boolean
     * is simply centralizing the logic of the notifications height being > 0 such
     * that it is not repeated in various components (such as AppBar) that need to
     * know if the notifications slot is empty.
     */
    var _z = useContainerQuery(function (rect) { return rect.height; }), notificationsContainerQuery = _z[0], notificationsElement = _z[1];
    var _0 = useState(0), notificationsHeight = _0[0], setNotificationsHeight = _0[1];
    var _1 = useState(false), hasNotificationsContent = _1[0], setHasNotificationsContent = _1[1];
    useEffect(function handleNotificationsContent() {
        setNotificationsHeight(notificationsContainerQuery !== null && notificationsContainerQuery !== void 0 ? notificationsContainerQuery : 0);
        setHasNotificationsContent(notificationsContainerQuery && notificationsContainerQuery > 0 ? true : false);
    }, [notificationsContainerQuery]);
    /**
     * Determine the offsetBottom value based on the presence of a footer element and
     * the SplitPanel component. Ignore the SplitPanel if it is not in the bottom
     * position. Use the size property if it is open and the header height if it is closed.
     */
    var offsetBottom = footerHeight;
    if (splitPanelDisplayed && splitPanelPosition === 'bottom') {
        if (isSplitPanelOpen) {
            offsetBottom += splitPanelReportedSize;
        }
        else {
            offsetBottom += splitPanelReportedHeaderHeight;
        }
    }
    return (React.createElement(AppLayoutInternalsContext.Provider, { value: __assign(__assign({}, props), { contentType: contentType, dynamicOverlapHeight: dynamicOverlapHeight, headerHeight: headerHeight, footerHeight: footerHeight, hasDefaultToolsWidth: hasDefaultToolsWidth, handleNavigationClick: handleNavigationClick, handleSplitPanelClick: handleSplitPanelClick, handleSplitPanelPreferencesChange: handleSplitPanelPreferencesChange, handleSplitPanelResize: handleSplitPanelResize, handleToolsClick: handleToolsClick, hasNotificationsContent: hasNotificationsContent, hasStickyBackground: hasStickyBackground, isAnyPanelOpen: isAnyPanelOpen, isMobile: isMobile, isNavigationOpen: isNavigationOpen !== null && isNavigationOpen !== void 0 ? isNavigationOpen : false, isSplitPanelForcedPosition: isSplitPanelForcedPosition, isSplitPanelOpen: isSplitPanelOpen, isToolsOpen: isToolsOpen, layoutElement: layoutElement, layoutWidth: layoutWidth, mainElement: mainElement, mainOffsetLeft: mainOffsetLeft, maxContentWidth: maxContentWidth, minContentWidth: minContentWidth, navigationHide: navigationHide, notificationsElement: notificationsElement, notificationsHeight: notificationsHeight, offsetBottom: offsetBottom, setDynamicOverlapHeight: setDynamicOverlapHeight, setHasStickyBackground: setHasStickyBackground, setSplitPanelReportedSize: setSplitPanelReportedSize, setSplitPanelReportedHeaderHeight: setSplitPanelReportedHeaderHeight, splitPanel: splitPanel, splitPanelDisplayed: splitPanelDisplayed, splitPanelMaxWidth: splitPanelMaxWidth, splitPanelMinWidth: splitPanelMinWidth, splitPanelPosition: splitPanelPosition, splitPanelPreferences: splitPanelPreferences, splitPanelReportedSize: splitPanelReportedSize, splitPanelReportedHeaderHeight: splitPanelReportedHeaderHeight, splitPanelSize: splitPanelSize, splitPanelToggle: splitPanelToggle, setSplitPanelToggle: setSplitPanelToggle, toolsHide: toolsHide, toolsOpen: isToolsOpen, toolsWidth: toolsWidth, toolsFocusControl: toolsFocusControl }) },
        React.createElement(AppLayoutContext.Provider, { value: {
                stickyOffsetBottom: offsetBottom,
                stickyOffsetTop: 0,
                hasBreadcrumbs: !!props.breadcrumbs,
                setHasStickyBackground: setHasStickyBackground,
                setDynamicOverlapHeight: setDynamicOverlapHeight
            } }, children)));
});
//# sourceMappingURL=context.js.map