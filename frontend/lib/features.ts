import type { Feature } from "@/types/feature";

export const FEATURES: Feature[] = [
  { id: "secure-payment", title: "دفع آمن", description: "خيارات دفع متعددة", icon: "lock" },
  { id: "easy-return", title: "إرجاع سهل", description: "خلال 14 يوم", icon: "return" },
  {
    id: "guaranteed-quality",
    title: "جودة مضمونة",
    description: "أقمشة مختارة بعناية",
    icon: "shield",
  },
  {
    id: "fast-delivery",
    title: "توصيل سريع",
    description: "في جميع أنحاء الإمارات",
    icon: "delivery",
  },
];
