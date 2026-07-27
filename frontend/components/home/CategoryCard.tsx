import Link from "next/link";
import { ArrowIcon } from "@/components/icons";
import { PlaceholderImage } from "@/components/ui/PlaceholderImage";
import type { Category } from "@/types/category";

interface CategoryCardProps {
  category: Category;
}

export function CategoryCard({ category }: CategoryCardProps) {
  return (
    <Link href={category.href} className="group flex flex-col gap-3">
      <div className="relative aspect-[3/4] w-full overflow-hidden rounded-2xl bg-cream-dark">
        <PlaceholderImage tone={category.tone} className="absolute inset-0" />
      </div>
      <div className="flex items-center justify-between gap-2">
        <span className="text-sm font-medium text-ink sm:text-base">{category.name}</span>
        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-border text-ink transition-colors group-hover:bg-ink group-hover:text-cream sm:h-9 sm:w-9">
          <ArrowIcon className="h-4 w-4" />
        </span>
      </div>
    </Link>
  );
}
