import { TruckIcon } from "@/components/icons";

export function AnnouncementBar() {
  return (
    <div className="bg-cream-dark">
      <div className="mx-auto flex max-w-[1400px] items-center justify-center gap-2 px-4 py-2 text-xs text-ink-soft sm:text-sm">
        <span>توصيل سريع في جميع أنحاء الإمارات</span>
        <TruckIcon className="h-4 w-4" />
      </div>
    </div>
  );
}
