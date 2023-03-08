import { RefObject } from 'react';
interface StickyHeaderContextProps {
    isStuck: boolean;
}
export declare const StickyHeaderContext: import("react").Context<StickyHeaderContextProps>;
export declare const useStickyHeader: (rootRef: RefObject<HTMLDivElement>, headerRef: RefObject<HTMLDivElement>, __stickyHeader?: boolean, __stickyOffset?: number) => {
    isSticky: boolean;
    isStuck: boolean;
    stickyStyles: {
        style: {
            top: string;
        };
    } | {
        style?: undefined;
    };
};
export declare function useSupportsStickyHeader(): boolean;
export {};
//# sourceMappingURL=use-sticky-header.d.ts.map