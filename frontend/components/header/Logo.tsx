import Image from "next/image";
import Link from "next/link";

export function Logo() {
  return (
    <Link href="/" className="flex shrink-0 flex-col items-center gap-1 text-center">
      <Image
        src="/logo.svg"
        alt="Sajda"
        width={300}
        height={90}
        priority
        unoptimized
        className="h-10 w-auto sm:h-12 lg:h-14"
      />
      <span className="hidden text-[11px] text-ink-muted sm:block">ملابس صلاة تعبر عن طهارتك</span>
    </Link>
  );
}
