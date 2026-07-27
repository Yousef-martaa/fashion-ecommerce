import type { FooterLinkGroup } from "@/types/footer";

export const FOOTER_LINK_GROUPS: FooterLinkGroup[] = [
  {
    title: "تسوقي",
    links: [
      { label: "ملابس الصلاة", href: "#" },
      { label: "أطقم الصلاة", href: "#" },
      { label: "الإكسسوارات", href: "#" },
      { label: "وصل حديثاً", href: "#" },
    ],
  },
  {
    title: "خدمة العملاء",
    links: [
      { label: "تواصلي معنا", href: "#" },
      { label: "الشحن والتوصيل", href: "#" },
      { label: "الإرجاع والاستبدال", href: "#" },
      { label: "الأسئلة الشائعة", href: "#" },
    ],
  },
];
