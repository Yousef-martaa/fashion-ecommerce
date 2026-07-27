import { SearchIcon } from "@/components/icons";

interface SearchBarProps {
  className?: string;
}

/** Presentational only -- no search functionality is wired up. */
export function SearchBar({ className = "" }: SearchBarProps) {
  return (
    <div className={`w-full md:w-72 lg:w-80 ${className}`}>
      <label className="relative flex items-center">
        <span className="sr-only">ابحثي عن منتج</span>
        <SearchIcon className="pointer-events-none absolute start-4 h-4 w-4 text-ink-muted" />
        <input
          type="search"
          placeholder="ابحثي عن منتج..."
          className="w-full rounded-full border border-border bg-white py-2.5 ps-10 pe-4 text-sm text-ink placeholder:text-ink-muted focus:outline-none focus:ring-2 focus:ring-gold/40"
        />
      </label>
    </div>
  );
}
