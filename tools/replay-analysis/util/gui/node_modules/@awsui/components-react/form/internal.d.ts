import { FormProps } from './interfaces';
import { InternalBaseComponentProps } from '../internal/hooks/use-base-component';
type InternalFormProps = FormProps & InternalBaseComponentProps;
export default function InternalForm({ children, header, errorText, errorIconAriaLabel, actions, secondaryActions, __internalRootRef, ...props }: InternalFormProps): JSX.Element;
export {};
//# sourceMappingURL=internal.d.ts.map