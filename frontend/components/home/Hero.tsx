import Link from "next/link";

const SLIDE_COUNT = 4;

export function Hero() {
  return (
    <section className="relative min-h-[480px] overflow-hidden rounded-2xl sm:min-h-[440px] sm:rounded-3xl lg:min-h-[520px]">
      {/*
        Stand-in for a photograph of a woman praying, framed with the subject
        toward the physical right and open space toward the physical left --
        the gradient direction mirrors that fixed composition rather than
        following logical start/end.
      */}
      <div
        aria-hidden="true"
        className="absolute inset-0 bg-gradient-to-l from-[#c7ab9c] via-[#e6d9c9] to-[#f5efe4]"
      />

      <div className="absolute inset-y-0 end-0 flex w-full flex-col justify-center gap-5 bg-gradient-to-l from-cream via-cream/85 to-transparent p-6 sm:gap-6 sm:p-10 md:w-[65%] md:p-12 lg:w-[45%] lg:p-16">
        <h1 className="font-display text-3xl leading-tight text-ink sm:text-4xl lg:text-5xl">
          راحة في صلاتك
          <br />
          وجمال في تفاصيلك
        </h1>
        <p className="max-w-sm text-sm leading-relaxed text-ink-soft sm:text-base">
          مجموعة مختارة بعناية من ملابس الصلاة الراقية لترافقك في كل لحظة خشوع.
        </p>
        <Link
          href="#"
          className="inline-flex w-fit items-center justify-center rounded-full bg-ink px-7 py-3 text-sm font-medium text-cream transition-colors hover:bg-ink-soft"
        >
          تسوقي الأن
        </Link>
      </div>

      <div className="absolute bottom-5 end-6 flex items-center gap-2 sm:bottom-8 sm:end-10">
        {Array.from({ length: SLIDE_COUNT }).map((_, index) => (
          <span
            key={index}
            aria-hidden="true"
            className={`h-2 rounded-full ${index === 0 ? "w-6 bg-ink" : "w-2 bg-ink/25"}`}
          />
        ))}
      </div>
    </section>
  );
}
