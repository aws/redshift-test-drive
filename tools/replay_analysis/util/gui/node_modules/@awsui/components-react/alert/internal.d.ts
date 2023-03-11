import { AlertProps } from './interfaces';
import { InternalBaseComponentProps } from '../internal/hooks/use-base-component';
import { SomeRequired } from '../internal/types';
type InternalAlertProps = SomeRequired<AlertProps, 'type'> & InternalBaseComponentProps;
export default function InternalAlert({ type, statusIconAriaLabel, visible, dismissible, dismissAriaLabel, children, header, buttonText, action, onDismiss, onButtonClick, __internalRootRef, ...rest }: InternalAlertProps): JSX.Element;
export {};
//# sourceMappingURL=internal.d.ts.map