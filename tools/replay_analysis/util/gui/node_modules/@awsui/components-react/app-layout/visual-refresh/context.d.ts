import React from 'react';
import { AppLayoutProps } from '../interfaces';
import { FocusControlState } from '../utils/use-focus-control';
import { SplitPanelSideToggleProps } from '../../internal/context/split-panel-context';
interface AppLayoutInternals extends AppLayoutProps {
    dynamicOverlapHeight: number;
    handleSplitPanelClick: () => void;
    handleNavigationClick: (isOpen: boolean) => void;
    handleSplitPanelPreferencesChange: (detail: AppLayoutProps.SplitPanelPreferences) => void;
    handleSplitPanelResize: (detail: {
        size: number;
    }) => void;
    handleToolsClick: (value: boolean) => void;
    hasDefaultToolsWidth: boolean;
    hasNotificationsContent: boolean;
    hasStickyBackground: boolean;
    isAnyPanelOpen: boolean;
    isMobile: boolean;
    isNavigationOpen: boolean;
    isSplitPanelForcedPosition: boolean;
    isSplitPanelOpen?: boolean;
    isToolsOpen: boolean;
    layoutElement: React.Ref<HTMLElement>;
    layoutWidth: number;
    mainElement: React.Ref<HTMLDivElement>;
    mainOffsetLeft: number;
    notificationsElement: React.Ref<HTMLDivElement>;
    notificationsHeight: number;
    offsetBottom: number;
    setDynamicOverlapHeight: (value: number) => void;
    setHasStickyBackground: (value: boolean) => void;
    setSplitPanelReportedSize: (value: number) => void;
    setSplitPanelReportedHeaderHeight: (value: number) => void;
    headerHeight: number;
    footerHeight: number;
    splitPanelMaxWidth: number;
    splitPanelMinWidth: number;
    splitPanelPosition: AppLayoutProps.SplitPanelPosition;
    splitPanelReportedSize: number;
    splitPanelReportedHeaderHeight: number;
    splitPanelToggle: SplitPanelSideToggleProps;
    setSplitPanelToggle: (toggle: SplitPanelSideToggleProps) => void;
    splitPanelDisplayed: boolean;
    toolsFocusControl: FocusControlState;
}
interface AppLayoutProviderInternalsProps extends AppLayoutProps {
    children: React.ReactNode;
}
export declare function useAppLayoutInternals(): AppLayoutInternals;
export declare const AppLayoutInternalsProvider: React.ForwardRefExoticComponent<AppLayoutProviderInternalsProps & React.RefAttributes<AppLayoutProps.Ref>>;
export {};
//# sourceMappingURL=context.d.ts.map