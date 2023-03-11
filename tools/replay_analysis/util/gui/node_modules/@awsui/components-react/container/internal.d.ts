import React from 'react';
import { ContainerProps } from './interfaces';
import { InternalBaseComponentProps } from '../internal/hooks/use-base-component';
export interface InternalContainerProps extends Omit<ContainerProps, 'variant'>, InternalBaseComponentProps {
    __stickyHeader?: boolean;
    __stickyOffset?: number;
    __disableFooterDivider?: boolean;
    __disableFooterPaddings?: boolean;
    __hiddenContent?: boolean;
    __headerRef?: React.RefObject<HTMLDivElement>;
    __headerId?: string;
    __darkHeader?: boolean;
    /**
     * Additional internal variant:
     * * `embedded` - Use this variant within a parent container (such as a modal,
     *                expandable section, container or split panel).
     * * `full-page` – Only for internal use in table, cards and other components
     */
    variant?: ContainerProps['variant'] | 'embedded' | 'full-page' | 'cards';
}
export default function InternalContainer({ header, footer, children, variant, disableHeaderPaddings, disableContentPaddings, fitHeight, __stickyOffset, __stickyHeader, __internalRootRef, __disableFooterDivider, __disableFooterPaddings, __hiddenContent, __headerRef, __headerId, __darkHeader, ...restProps }: InternalContainerProps): JSX.Element;
//# sourceMappingURL=internal.d.ts.map