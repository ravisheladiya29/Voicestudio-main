// Shared cookie names for local/OSS-mode auth. Centralized so the
// middleware, server helpers, and the session/logout API routes can't drift.
import { AUTH_COOKIE_PREFIX } from "@/config/brand";

export const OSS_TOKEN_COOKIE = `${AUTH_COOKIE_PREFIX}_auth_token`;
export const OSS_USER_COOKIE = `${AUTH_COOKIE_PREFIX}_auth_user`;
