import React from 'react';
export interface TableTdElementProps {
    className?: string;
    style?: React.CSSProperties;
    wrapLines: boolean | undefined;
    isFirstRow: boolean;
    isLastRow: boolean;
    isSelected: boolean;
    isNextSelected: boolean;
    isPrevSelected: boolean;
    nativeAttributes?: Omit<React.HTMLAttributes<HTMLTableCellElement>, 'style' | 'className' | 'onClick'>;
    onClick?: () => void;
    children?: React.ReactNode;
    isEvenRow?: boolean;
    stripedRows?: boolean;
    hasSelection?: boolean;
    hasFooter?: boolean;
    isVisualRefresh?: boolean;
}
export declare const TableTdElement: React.ForwardRefExoticComponent<TableTdElementProps & React.RefAttributes<HTMLTableCellElement>>;
//# sourceMappingURL=td-element.d.ts.map