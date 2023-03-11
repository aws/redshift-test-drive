import React from 'react';
import { ScreenreaderOnlyProps } from '../screenreader-only';
export interface LiveRegionProps extends ScreenreaderOnlyProps {
    assertive?: boolean;
    delay?: number;
    visible?: boolean;
    tagName?: 'span' | 'div';
    children: React.ReactNode;
}
/**
 * The live region is hidden in the layout, but visible for screen readers.
 * It's purpose it to announce changes e.g. when custom navigation logic is used.
 *
 * The way live region works differently in different browsers and screen readers and
 * it is recommended to manually test every new implementation.
 *
 * If you notice there are different words being merged together,
 * check if there are text nodes not being wrapped in elements, like:
 * <LiveRegion>
 *   {title}
 *   <span><Details /></span>
 * </LiveRegion>
 *
 * To fix, wrap "title" in an element:
 * <LiveRegion>
 *   <span>{title}</span>
 *   <span><Details /></span>
 * </LiveRegion>
 *
 * Or create a single text node if possible:
 * <LiveRegion>
 *   {`${title} ${details}`}
 * </LiveRegion>
 *
 * The live region is always atomic, because non-atomic regions can be treated by screen readers
 * differently and produce unexpected results. To imitate non-atomic announcements simply use
 * multiple live regions:
 * <>
 *   <LiveRegion>{title}</LiveRegion>
 *   <LiveRegion><Details /></LiveRegion>
 * </>
 */
declare const _default: React.MemoExoticComponent<typeof LiveRegion>;
export default _default;
declare function LiveRegion({ assertive, delay, visible, tagName: TagName, children, ...restProps }: LiveRegionProps): JSX.Element;
//# sourceMappingURL=index.d.ts.map