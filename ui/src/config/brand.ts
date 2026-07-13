// Centralized whitelabel brand configuration. Every user-visible brand
// string (product name, marketing copy, external links) should be read
// from here instead of being hardcoded in components — that keeps a future
// rebrand to a single-file change.
//
// Values can be overridden at build time via NEXT_PUBLIC_* env vars without
// touching code. Defaults below use the `.example` TLD (reserved for
// documentation per RFC 2606) as placeholders until real domains exist.

export const BRAND_NAME = process.env.NEXT_PUBLIC_BRAND_NAME || "Zenvoice";

export const BRAND_TAGLINE =
  process.env.NEXT_PUBLIC_BRAND_TAGLINE || "Open Source Voice Assistant Workflow Builder";

export const BRAND_HERO_HEADLINE =
  process.env.NEXT_PUBLIC_BRAND_HERO_HEADLINE || "The open-source voice AI platform.";

export const BRAND_WEBSITE_URL = process.env.NEXT_PUBLIC_BRAND_WEBSITE_URL || "https://zenvoice.example";

export const BRAND_DOCS_URL = process.env.NEXT_PUBLIC_DOCS_URL || "https://docs.zenvoice.example";

export const BRAND_SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@zenvoice.example";

export const BRAND_PRIVACY_URL = process.env.NEXT_PUBLIC_PRIVACY_URL || `${BRAND_WEBSITE_URL}/privacy-policy`;

export const BRAND_TERMS_URL = process.env.NEXT_PUBLIC_TERMS_URL || `${BRAND_WEBSITE_URL}/terms-of-service`;

// Community links are deliberately blank by default: the upstream project's
// GitHub repo and Slack community belong to the original maintainers, not
// this whitelabeled deployment. Set the env vars if/when you have your own.
export const BRAND_GITHUB_URL = process.env.NEXT_PUBLIC_GITHUB_URL || "";
export const BRAND_SLACK_URL = process.env.NEXT_PUBLIC_SLACK_URL || "";

// Cookie name prefix used for local/OSS-mode auth session cookies.
export const AUTH_COOKIE_PREFIX = "zenvoice";

export function normalizeBrandText(text: string | null | undefined): string {
  if (!text) return "";
  return text.replace(/\bDograh\b/g, BRAND_NAME);
}

/** Map internal provider ids / legacy schema titles to the whitelabel name. */
export function getProviderDisplayName(
  provider: string | undefined,
  schemaTitle?: string | null,
): string | undefined {
  if (!provider) return provider;
  if (provider === "dograh" || schemaTitle === "Dograh") return BRAND_NAME;
  return schemaTitle || provider;
}
