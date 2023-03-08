import React from 'react';
export declare function useClickAway(onClick: () => void): React.MutableRefObject<any>;
interface ClickAwayActive {
    onClick: () => void;
    children: React.ReactNode;
}
export declare function ClickAway({ onClick, children }: ClickAwayActive): JSX.Element;
export {};
//# sourceMappingURL=click-away.d.ts.map