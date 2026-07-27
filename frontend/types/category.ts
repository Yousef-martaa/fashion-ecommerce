export type CategoryTone = "charcoal" | "olive" | "sand" | "ivory" | "mauve" | "cream";

export interface Category {
  id: string;
  name: string;
  href: string;
  tone: CategoryTone;
}
