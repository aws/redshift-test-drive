import React from 'react';
import { DesktopDrawerProps } from './drawer';
import { AppLayoutProps } from './interfaces';
import useContentHeight from './utils/use-content-height';
interface ToolsAndSplitPanelProps {
    toolsHide: boolean;
    toolsOpen: boolean;
    isHidden: DesktopDrawerProps['isHidden'];
    splitPanelOpen: boolean;
    drawerWidth: number;
    toolsWidth: number;
    splitPanelReportedSize: number;
    closedDrawerWidth: number;
    headerHeight: DesktopDrawerProps['topOffset'];
    footerHeight: DesktopDrawerProps['bottomOffset'];
    panelHeightStyle: ReturnType<typeof useContentHeight>['panelHeightStyle'];
    contentHeightStyle: ReturnType<typeof useContentHeight>['contentHeightStyle'];
    tools: React.ReactNode;
    splitPanel: React.ReactNode;
    ariaLabels: AppLayoutProps['ariaLabels'];
    disableContentPaddings: AppLayoutProps['disableContentPaddings'];
    isMobile: boolean;
    isMotionEnabled: boolean;
    onToolsToggle: DesktopDrawerProps['onToggle'];
    toggleRefs: DesktopDrawerProps['toggleRefs'];
    onLoseToolsFocus: (event: React.FocusEvent) => void;
}
export declare function ToolsAndSplitPanel({ ariaLabels, drawerWidth, footerHeight, headerHeight, isHidden, isMobile, onToolsToggle, panelHeightStyle, splitPanel, toggleRefs, onLoseToolsFocus, tools, toolsHide, toolsOpen, toolsWidth, splitPanelOpen, }: ToolsAndSplitPanelProps): JSX.Element;
export {};
//# sourceMappingURL=tools-and-split-panel.d.ts.map