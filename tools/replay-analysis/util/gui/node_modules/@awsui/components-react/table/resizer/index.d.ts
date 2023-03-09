interface ResizerProps {
    onDragMove: (newWidth: number) => void;
    onFinish: () => void;
    ariaLabelledby?: string;
    minWidth?: number;
}
export declare function Resizer({ onDragMove, onFinish, ariaLabelledby, minWidth }: ResizerProps): JSX.Element;
export declare function ResizeTracker(): JSX.Element;
export {};
//# sourceMappingURL=index.d.ts.map