import Link from "next/link";
import { ArrowIcon } from "@/components/icons";
import { CATEGORIES } from "@/lib/categories";
import { CategoryCard } from "./CategoryCard";

export function CategorySection() {
  return (
    <section>
      <div className="mb-5 flex items-center justify-between sm:mb-6">
        <h2 className="text-lg font-semibold text-ink sm:text-xl lg:text-2xl">تسوقي حسب الفئة</h2>
        <Link
          href="#"
          className="flex items-center gap-2 text-xs text-ink-soft transition-colors hover:text-ink sm:text-sm"
        >
          <span>عرض جميع الفئات</span>
          <ArrowIcon className="h-3.5 w-3.5" />
        </Link>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {CATEGORIES.map((category) => (
          <CategoryCard key={category.id} category={category} />
        ))}
      </div>
    </section>
  );
}
