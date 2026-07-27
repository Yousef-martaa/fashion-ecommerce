import { CategorySection } from "@/components/home/CategorySection";
import { FeaturesSection } from "@/components/home/FeaturesSection";
import { Hero } from "@/components/home/Hero";

export default function Home() {
  return (
    <main className="flex-1">
      <div className="mx-auto flex max-w-[1400px] flex-col gap-10 px-4 py-6 sm:px-6 lg:px-10 lg:py-8">
        <Hero />
        <CategorySection />
        <FeaturesSection />
      </div>
    </main>
  );
}
