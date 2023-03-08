import React from 'react';
import { ButtonProps } from '../button/interfaces';
import { SplitPanelProps, SplitPanelContentProps } from './interfaces';
interface SplitPanelContentSideProps extends SplitPanelContentProps {
    i18nStrings: SplitPanelProps.I18nStrings;
    toggleRef: React.RefObject<ButtonProps.Ref>;
}
export declare function SplitPanelContentSide({ baseProps, splitPanelRef, toggleRef, header, children, resizeHandle, isOpen, cappedSize, i18nStrings, panelHeaderId, onToggle, }: SplitPanelContentSideProps): JSX.Element;
export {};
//# sourceMappingURL=side.d.ts.map