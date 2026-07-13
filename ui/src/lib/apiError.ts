/**
 * Extract a human-readable message from a backend error response.
 *
 * The generated API client returns `{ error }` on failure (it does not throw),
 * and FastAPI shapes that error as `{ detail: string }`, `{ detail:
 * [{ msg, loc, ... }] }`, or backend validation arrays like `{ detail:
 * [{ model, message }] }`. This normalizes those to a single string so it can
 * be rendered or thrown directly.
 */
export function detailFromError(err: unknown, fallback = "Request failed"): string {
    if (typeof err === "string") return err;
    if (!err || typeof err !== "object") return fallback;

    const e = err as { detail?: unknown; message?: unknown };

    // Some clients nest the FastAPI body; unwrap once.
    const detail = e.detail !== undefined
        ? e.detail
        : (err as { error?: { detail?: unknown } }).error?.detail;

    if (typeof detail === "string") return detail;

    // Single Pydantic/FastAPI error object: { type, loc, msg, input, ctx }
    if (detail && typeof detail === "object" && !Array.isArray(detail)) {
        const item = detail as { message?: unknown; msg?: unknown };
        if (typeof item.message === "string") return item.message;
        if (typeof item.msg === "string") return item.msg;
    }

    if (Array.isArray(detail) && detail.length > 0) {
        const messages = detail
            .map((item) => {
                if (typeof item === "string") return item;
                if (!item || typeof item !== "object") return null;
                const d = item as { message?: unknown; msg?: unknown; model?: unknown };
                const message = typeof d.message === "string"
                    ? d.message
                    : typeof d.msg === "string"
                        ? d.msg
                        : null;
                if (!message) return null;
                return typeof d.model === "string" && d.model
                    ? `${d.model}: ${message}`
                    : message;
            })
            .filter((message): message is string => Boolean(message));
        if (messages.length > 0) return messages.join("\n");
    }

    if (typeof e.message === "string" && e.message) return e.message;
    return fallback;
}
