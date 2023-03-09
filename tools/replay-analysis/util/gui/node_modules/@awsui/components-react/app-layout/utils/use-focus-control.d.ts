import { RefObject } from 'react';
import { ButtonProps } from '../../button/interfaces';
export interface FocusControlState {
    refs: {
        toggle: RefObject<ButtonProps.Ref>;
        close: RefObject<ButtonProps.Ref>;
    };
    setFocus: () => void;
    loseFocus: () => void;
}
export declare function useFocusControl(isOpen: boolean, restoreFocus?: boolean): FocusControlState;
//# sourceMappingURL=use-focus-control.d.ts.map