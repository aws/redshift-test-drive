import { FilteringProperty, I18nStrings, Token, ExtendedOperatorForm, ComparisonOperator } from './interfaces';
interface PorpertyEditorProps<TokenValue> {
    property: FilteringProperty;
    operator: ComparisonOperator;
    filter: string;
    operatorForm: ExtendedOperatorForm<TokenValue>;
    onCancel: () => void;
    onSubmit: (value: Token) => void;
    i18nStrings: I18nStrings;
}
export declare function PropertyEditor<TokenValue = any>({ property, operator, filter, operatorForm, onCancel, onSubmit, i18nStrings, }: PorpertyEditorProps<TokenValue>): JSX.Element;
export {};
//# sourceMappingURL=property-editor.d.ts.map