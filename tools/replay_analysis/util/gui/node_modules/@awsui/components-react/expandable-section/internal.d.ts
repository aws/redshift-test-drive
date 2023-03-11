import { ExpandableSectionProps } from './interfaces';
import { InternalBaseComponentProps } from '../internal/hooks/use-base-component';
type InternalExpandableSectionProps = ExpandableSectionProps & InternalBaseComponentProps;
export default function InternalExpandableSection({ expanded: controlledExpanded, defaultExpanded, onChange, variant, children, header, headerText, headerCounter, headerDescription, headingTagOverride, disableContentPaddings, headerAriaLabel, __internalRootRef, ...props }: InternalExpandableSectionProps): JSX.Element;
export {};
//# sourceMappingURL=internal.d.ts.map