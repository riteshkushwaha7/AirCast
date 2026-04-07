import { Text } from "react-native";

import { AQI_CATEGORY_META, AQI_TONE_CLASSES } from "../../constants/app";
import type { AQICategory } from "../../types/airwise";

export function AQIBadge({ category }: { category: AQICategory }) {
  const meta = AQI_CATEGORY_META[category];
  return (
    <Text className={`rounded-full border px-3 py-1 text-xs font-semibold ${AQI_TONE_CLASSES[meta.tone]}`}>
      {meta.label}
    </Text>
  );
}
