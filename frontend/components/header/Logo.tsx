import Image from "next/image";
import Link from "next/link";

export function Logo() {
  return (
    <Link href="/" className="flex shrink-0 items-center justify-center">
      <Image
        src="/logo.svg"
        alt="Sajda"
        width={300}
        height={90}
        priority
        unoptimized
        className="h-14 w-auto sm:h-16 lg:h-20"
      />
    </Link>
  );
}
