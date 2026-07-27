import Link from "next/link";
import { AnnouncementBar } from "./AnnouncementBar";
import { Logo } from "./Logo";
import { Navigation } from "./Navigation";
import { SearchBar } from "./SearchBar";
import { BagIcon, ChevronDownIcon, HeartIcon, UaeFlagIcon, UserIcon } from "@/components/icons";

export function SiteHeader() {
  return (
    <header className="border-b border-border bg-cream">
      <AnnouncementBar />

      <div className="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-10">
        <div className="flex items-center justify-between gap-4 py-4 sm:py-6">
          {/* Physical right / RTL start: account, favorites, cart */}
          <div className="flex items-center gap-4 text-xs text-ink-soft sm:gap-6 sm:text-sm">
            <Link href="#" className="flex items-center gap-1.5 transition-colors hover:text-ink">
              <UserIcon className="h-5 w-5" />
              <span className="hidden sm:inline">حسابي</span>
            </Link>
            <Link
              href="#"
              className="hidden items-center gap-1.5 transition-colors hover:text-ink md:flex"
            >
              <HeartIcon className="h-5 w-5" />
              <span>المفضلة</span>
            </Link>
            <Link href="#" className="flex items-center gap-1.5 transition-colors hover:text-ink">
              <span className="relative">
                <BagIcon className="h-5 w-5" />
                <span className="absolute -end-1.5 -top-1.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-ink text-[9px] font-medium text-cream">
                  0
                </span>
              </span>
              <span className="hidden sm:inline">سلة المشتريات</span>
            </Link>
          </div>

          <Logo />

          {/* Physical left / RTL end: currency, language */}
          <div className="flex items-center gap-3 text-xs text-ink-soft sm:gap-5 sm:text-sm">
            <button type="button" className="flex items-center gap-1.5">
              <UaeFlagIcon className="h-3.5 w-5 rounded-[2px]" />
              <span className="hidden sm:inline">د.إ.</span>
              <ChevronDownIcon className="h-3.5 w-3.5" />
            </button>
            <button type="button" className="hidden items-center gap-1.5 sm:flex">
              <span>العربية</span>
              <ChevronDownIcon className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-3 border-t border-border py-3 md:flex-row md:items-center md:justify-between md:py-4">
          <Navigation className="order-2 md:order-none" />
          <SearchBar className="order-1 md:order-none" />
        </div>
      </div>
    </header>
  );
}
