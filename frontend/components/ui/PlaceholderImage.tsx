import type { CategoryTone } from "@/types/category";

const TONE_GRADIENTS: Record<CategoryTone, string> = {
  charcoal: "from-neutral-700 to-neutral-900",
  olive: "from-[#7c8058] to-[#545843]",
  sand: "from-[#cba883] to-[#a9825c]",
  ivory: "from-[#f1e9da] to-[#e2d3b4]",
  mauve: "from-[#c3a094] to-[#a37c70]",
  cream: "from-[#ede4d3] to-[#ddd0b4]",
};

interface PlaceholderImageProps {
  tone: CategoryTone;
  className?: string;
}

/** Stands in for real product photography while preserving card proportions. */
export function PlaceholderImage({ tone, className = "" }: PlaceholderImageProps) {
  return <div aria-hidden="true" className={`bg-gradient-to-br ${TONE_GRADIENTS[tone]} ${className}`} />;
}
