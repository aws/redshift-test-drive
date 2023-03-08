import { ExpandableSectionProps } from './interfaces';
import { KeyboardEventHandler, MouseEventHandler, ReactNode } from 'react';
interface ExpandableDefaultHeaderProps {
    id: string;
    className?: string;
    children?: ReactNode;
    expanded: boolean;
    ariaControls: string;
    ariaLabel?: string;
    onKeyUp: KeyboardEventHandler;
    onKeyDown: KeyboardEventHandler;
    onClick: MouseEventHandler;
    icon: JSX.Element;
}
interface ExpandableSectionHeaderProps extends Omit<ExpandableDefaultHeaderProps, 'children' | 'icon'> {
    variant: ExpandableSectionProps.Variant;
    header?: ReactNode;
    headerText?: ReactNode;
    headerDescription?: ReactNode;
    headerCounter?: string;
    headingTagOverride?: ExpandableSectionProps.HeadingTag;
    ariaLabelledBy?: string;
}
export declare const ExpandableSectionHeader: ({ id, className, variant, header, headerText, headerDescription, headerCounter, headingTagOverride, expanded, ariaControls, ariaLabel, ariaLabelledBy, onKeyUp, onKeyDown, onClick, }: ExpandableSectionHeaderProps) => JSX.Element;
export {};
//# sourceMappingURL=expandable-section-header.d.ts.map