export interface AppLayoutContextProps {
    stickyOffsetBottom: number;
    stickyOffsetTop: number;
    hasBreadcrumbs: boolean;
    setHasStickyBackground?: (hasBackground: boolean) => void;
    setDynamicOverlapHeight?: (height: number) => void;
}
export declare const AppLayoutContext: import("react").Context<AppLayoutContextProps>;
export declare function useAppLayoutContext(): AppLayoutContextProps;
//# sourceMappingURL=app-layout-context.d.ts.map