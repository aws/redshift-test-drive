import { ComparisonOperator, FilteringOption, FilteringProperty, Token } from './interfaces';
export declare function matchFilteringProperty(filteringProperties: readonly FilteringProperty[], filteringText: string): null | FilteringProperty;
export declare function matchOperator(allowedOperators: readonly ComparisonOperator[], filteringText: string): null | ComparisonOperator;
export declare function matchOperatorPrefix(allowedOperators: readonly ComparisonOperator[], filteringText: string): null | string;
export declare function matchTokenValue(token: Token, filteringOptions: readonly FilteringOption[]): Token;
export declare function trimStart(source: string): string;
export declare function trimFirstSpace(source: string): string;
//# sourceMappingURL=utils.d.ts.map