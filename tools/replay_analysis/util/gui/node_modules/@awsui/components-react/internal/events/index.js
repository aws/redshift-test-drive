var CustomEventStub = /** @class */ (function () {
    function CustomEventStub(cancelable, detail) {
        if (cancelable === void 0) { cancelable = false; }
        if (detail === void 0) { detail = null; }
        this.cancelable = cancelable;
        this.detail = detail;
        this.defaultPrevented = false;
        this.cancelBubble = false;
    }
    CustomEventStub.prototype.preventDefault = function () {
        this.defaultPrevented = true;
    };
    CustomEventStub.prototype.stopPropagation = function () {
        this.cancelBubble = true;
    };
    return CustomEventStub;
}());
export function createCustomEvent(_a) {
    var cancelable = _a.cancelable, detail = _a.detail;
    return new CustomEventStub(cancelable, detail);
}
export function fireNonCancelableEvent(handler, detail) {
    if (!handler) {
        return;
    }
    var event = createCustomEvent({ cancelable: false, detail: detail });
    handler(event);
}
export function fireCancelableEvent(handler, detail, sourceEvent) {
    if (!handler) {
        return false;
    }
    var event = createCustomEvent({ cancelable: true, detail: detail });
    handler(event);
    if (event.defaultPrevented && sourceEvent) {
        sourceEvent.preventDefault();
    }
    if (event.cancelBubble && sourceEvent) {
        sourceEvent.stopPropagation();
    }
    return event.defaultPrevented;
}
export function fireKeyboardEvent(handler, reactEvent) {
    return fireCancelableEvent(handler, {
        keyCode: reactEvent.keyCode,
        key: reactEvent.key,
        ctrlKey: reactEvent.ctrlKey,
        shiftKey: reactEvent.shiftKey,
        altKey: reactEvent.altKey,
        metaKey: reactEvent.metaKey
    }, reactEvent);
}
var isMouseEvent = function (e) {
    return e.button !== undefined;
};
export function isPlainLeftClick(event) {
    return (event &&
        (!isMouseEvent(event) || event.button === 0) &&
        !event.ctrlKey &&
        !event.altKey &&
        !event.shiftKey &&
        !event.metaKey);
}
//# sourceMappingURL=index.js.map