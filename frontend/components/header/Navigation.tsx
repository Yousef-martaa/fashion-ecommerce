import Link from "next/link";
import { NAV_LINKS } from "@/lib/navigation";

interface NavigationProps {
  className?: string;
}

export function Navigation({ className = "" }: NavigationProps) {
  return (
    <nav className={`min-w-0 overflow-x-auto ${className}`} aria-label="التنقل الرئيسي">
      <ul className="flex items-center gap-6 whitespace-nowrap text-sm text-ink-soft lg:gap-8">
        {NAV_LINKS.map((link) => (
          <li key={link.label}>
            <Link
              href={link.href}
              aria-current={link.active ? "page" : undefined}
              className={
                link.active
                  ? "border-b-2 border-ink pb-1 font-medium text-ink"
                  : "border-b-2 border-transparent pb-1 transition-colors hover:text-ink"
              }
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
