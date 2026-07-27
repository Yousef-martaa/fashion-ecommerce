export type FeatureIcon = "lock" | "return" | "shield" | "delivery";

export interface Feature {
  id: string;
  title: string;
  description: string;
  icon: FeatureIcon;
}
