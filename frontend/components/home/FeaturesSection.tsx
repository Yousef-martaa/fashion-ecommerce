import { BoxIcon, LockIcon, RefreshIcon, ShieldCheckIcon } from "@/components/icons";
import { FEATURES } from "@/lib/features";
import type { FeatureIcon } from "@/types/feature";

const ICONS: Record<FeatureIcon, typeof LockIcon> = {
  lock: LockIcon,
  return: RefreshIcon,
  shield: ShieldCheckIcon,
  delivery: BoxIcon,
};

export function FeaturesSection() {
  return (
    <section className="flex flex-col rounded-2xl bg-cream-dark md:flex-row">
      {FEATURES.map((feature, index) => {
        const Icon = ICONS[feature.icon];
        return (
          <div
            key={feature.id}
            className={`flex flex-1 items-center justify-center gap-3 px-4 py-6 sm:px-6 sm:py-8 ${
              index === 0 ? "" : "border-t border-border md:border-t-0 md:border-s"
            }`}
          >
            <Icon className="h-7 w-7 shrink-0 text-ink sm:h-8 sm:w-8" />
            <div className="text-start">
              <p className="text-sm font-semibold text-ink sm:text-base">{feature.title}</p>
              <p className="text-xs text-ink-muted sm:text-sm">{feature.description}</p>
            </div>
          </div>
        );
      })}
    </section>
  );
}
