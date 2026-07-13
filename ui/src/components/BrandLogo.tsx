import { BRAND_NAME } from "@/config/brand";
import { cn } from "@/lib/utils";

// Reusable Zenvoice brand lockup. `mark` renders the square app icon (e.g.
// the app sidebar header); the default/`inverse` variants render a
// text-based wordmark that is theme-aware without needing separate light/dark
// logo image files. Height is controlled by the caller via className (e.g.
// "h-7"); the wordmark scales its font-size off that height automatically.
export function BrandLogo({
  className,
  inverse = false,
  mark = false,
}: {
  className?: string;
  inverse?: boolean;
  mark?: boolean;
}) {
  if (mark) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src="/zenvoice-mark.png"
        alt={BRAND_NAME}
        className={cn("aspect-square w-auto select-none rounded-md", className)}
      />
    );
  }

  return (
    <span
      className={cn(
        "inline-flex h-7 items-center text-xl font-semibold leading-none tracking-tight select-none",
        inverse ? "text-zinc-50" : "text-foreground",
        className,
      )}
    >
      {BRAND_NAME}
    </span>
  );
}
