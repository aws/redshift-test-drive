import { __assign } from "tslib";
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0
import React, { useRef } from 'react';
import clsx from 'clsx';
import InternalForm from '../form/internal';
import InternalHeader from '../header/internal';
import { useMobile } from '../internal/hooks/use-mobile';
import WizardActions from './wizard-actions';
import WizardFormHeader from './wizard-form-header';
import styles from './styles.css.js';
import useFocusVisible from '../internal/hooks/focus-visible';
import { useEffectOnUpdate } from '../internal/hooks/use-effect-on-update';
export default function WizardForm(_a) {
    var steps = _a.steps, activeStepIndex = _a.activeStepIndex, isVisualRefresh = _a.isVisualRefresh, showCollapsedSteps = _a.showCollapsedSteps, i18nStrings = _a.i18nStrings, isPrimaryLoading = _a.isPrimaryLoading, allowSkipTo = _a.allowSkipTo, secondaryActions = _a.secondaryActions, onCancelClick = _a.onCancelClick, onPreviousClick = _a.onPreviousClick, onPrimaryClick = _a.onPrimaryClick, onSkipToClick = _a.onSkipToClick;
    var _b = steps[activeStepIndex] || {}, title = _b.title, info = _b.info, description = _b.description, content = _b.content, errorText = _b.errorText, isOptional = _b.isOptional;
    var isLastStep = activeStepIndex >= steps.length - 1;
    var skipToTargetIndex = findSkipToTargetIndex(steps, activeStepIndex);
    var isMobile = useMobile();
    var stepHeaderRef = useRef(null);
    useEffectOnUpdate(function () {
        var _a;
        if (stepHeaderRef && stepHeaderRef.current) {
            (_a = stepHeaderRef.current) === null || _a === void 0 ? void 0 : _a.focus();
        }
    }, [activeStepIndex]);
    var focusVisible = useFocusVisible();
    var showSkipTo = allowSkipTo && skipToTargetIndex !== -1;
    var skipToButtonText = skipToTargetIndex !== -1 && i18nStrings.skipToButtonLabel
        ? i18nStrings.skipToButtonLabel(steps[skipToTargetIndex], skipToTargetIndex + 1)
        : undefined;
    return (React.createElement(React.Fragment, null,
        React.createElement(WizardFormHeader, { isMobile: isMobile || showCollapsedSteps, isVisualRefresh: isVisualRefresh },
            React.createElement("div", { className: clsx(styles['collapsed-steps'], !showCollapsedSteps && styles['collapsed-steps-hidden'], isVisualRefresh && isMobile && styles['collapsed-steps-extra-padding']) }, i18nStrings.collapsedStepsLabel(activeStepIndex + 1, steps.length)),
            React.createElement(InternalHeader, { className: styles['form-header-component'], variant: "h1", description: description, info: info },
                React.createElement("span", __assign({ className: styles['form-header-component-wrapper'], tabIndex: -1, ref: stepHeaderRef }, focusVisible),
                    title,
                    isOptional && React.createElement("i", null, " - ".concat(i18nStrings.optional))))),
        React.createElement(InternalForm, { className: clsx(styles['form-component']), actions: React.createElement(WizardActions, { cancelButtonText: i18nStrings.cancelButton, primaryButtonText: isLastStep ? i18nStrings.submitButton : i18nStrings.nextButton, previousButtonText: i18nStrings.previousButton, onCancelClick: onCancelClick, onPreviousClick: onPreviousClick, onPrimaryClick: onPrimaryClick, onSkipToClick: function () { return onSkipToClick(skipToTargetIndex); }, showPrevious: activeStepIndex !== 0, isPrimaryLoading: isPrimaryLoading, showSkipTo: showSkipTo, skipToButtonText: skipToButtonText }), secondaryActions: secondaryActions, errorText: errorText, errorIconAriaLabel: i18nStrings.errorIconAriaLabel }, content)));
}
function findSkipToTargetIndex(steps, activeStepIndex) {
    var nextRequiredStepIndex = activeStepIndex;
    do {
        nextRequiredStepIndex++;
    } while (nextRequiredStepIndex < steps.length - 1 && steps[nextRequiredStepIndex].isOptional);
    return nextRequiredStepIndex > activeStepIndex + 1 ? nextRequiredStepIndex : -1;
}
//# sourceMappingURL=wizard-form.js.map