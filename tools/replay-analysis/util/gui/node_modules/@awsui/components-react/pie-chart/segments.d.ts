import React from 'react';
import { PieArcDatum } from 'd3-shape';
import { PieChartProps } from './interfaces';
import { InternalChartDatum } from './pie-chart';
interface SegmentsProps<T> {
    pieData: Array<PieArcDatum<InternalChartDatum<T>>>;
    highlightedSegment: T | null;
    size: NonNullable<PieChartProps['size']>;
    variant: PieChartProps['variant'];
    focusedSegmentRef: React.RefObject<SVGGElement>;
    popoverTrackRef: React.RefObject<SVGCircleElement>;
    segmentAriaRoleDescription?: string;
    onMouseDown: (datum: InternalChartDatum<T>) => void;
    onMouseOver: (datum: InternalChartDatum<T>) => void;
    onMouseOut: (event: React.MouseEvent<SVGElement>) => void;
}
export default function Segments<T extends PieChartProps.Datum>({ pieData, highlightedSegment, size, variant, focusedSegmentRef, popoverTrackRef, segmentAriaRoleDescription, onMouseDown, onMouseOver, onMouseOut, }: SegmentsProps<T>): JSX.Element;
export {};
//# sourceMappingURL=segments.d.ts.map