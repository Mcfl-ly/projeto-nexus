// Handoff from a successful login; never persisted in browser storage.
let pendingUser = null;
export function rememberLogin(user) { pendingUser = user ?? null; }
export function peekLogin() { return pendingUser; }
export function clearLogin() { pendingUser = null; }
