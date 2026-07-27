import Link from "next/link";
import { EmblemIcon } from "@/components/icons";
import { FOOTER_LINK_GROUPS } from "@/lib/footer";

const SOCIAL_LINKS = ["IG", "TW", "FB"];

export function Footer() {
  return (
    <footer className="border-t border-border bg-cream-dark">
      <div className="mx-auto max-w-[1400px] px-4 py-10 sm:px-6 lg:px-10">
        <div className="flex flex-col gap-8 md:grid md:grid-cols-3">
          <div className="flex flex-col gap-3">
            <Link href="/" className="flex items-center gap-2">
              <EmblemIcon className="h-6 w-6 text-gold" />
              <span className="font-display text-xl text-ink">سجدة</span>
            </Link>
            <p className="max-w-xs text-sm leading-relaxed text-ink-muted">
              ملابس صلاة تعبر عن طهارتك، مصممة براحة وأناقة لتلازمك في كل لحظة خشوع.
            </p>
            <div className="mt-1 flex items-center gap-2">
              {SOCIAL_LINKS.map((label) => (
                <Link
                  key={label}
                  href="#"
                  className="flex h-9 w-9 items-center justify-center rounded-full border border-border text-xs text-ink-soft transition-colors hover:bg-ink hover:text-cream"
                >
                  {label}
                </Link>
              ))}
            </div>
          </div>

          {FOOTER_LINK_GROUPS.map((group) => (
            <div key={group.title} className="flex flex-col gap-3">
              <h3 className="text-sm font-semibold text-ink">{group.title}</h3>
              <ul className="flex flex-col gap-2">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-ink-muted transition-colors hover:text-ink"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 flex flex-col items-center justify-between gap-3 border-t border-border pt-6 text-xs text-ink-muted sm:flex-row">
          <p>© 2026 سجدة. جميع الحقوق محفوظة.</p>
          <div className="flex items-center gap-4">
            <Link href="#" className="transition-colors hover:text-ink">
              سياسة الخصوصية
            </Link>
            <Link href="#" className="transition-colors hover:text-ink">
              الشروط والأحكام
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
