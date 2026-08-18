// Vitest's jsdom environment skips overriding `localStorage` on the global
// object because Node.js (22+) ships its own experimental `localStorage`
// global, which returns `undefined` unless started with
// `--localstorage-file`. Explicitly wire up jsdom's real localStorage
// implementation so tests can use the standard global `localStorage` API.
const dom = (globalThis as unknown as { jsdom?: { window: Window } }).jsdom;
if (dom?.window?.localStorage) {
  Object.defineProperty(globalThis, "localStorage", {
    value: dom.window.localStorage,
    configurable: true,
    writable: true,
  });
}
if (dom?.window && "sessionStorage" in dom.window) {
  Object.defineProperty(globalThis, "sessionStorage", {
    value: (dom.window as unknown as { sessionStorage: Storage }).sessionStorage,
    configurable: true,
    writable: true,
  });
}
