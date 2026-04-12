import { Text } from "react-native";

import { SectionContainer } from "../ui/SectionContainer";

export function BestTimeCard({
  title,
  lines
}: {
  title: string;
  lines: string[];
}) {
  return (
    <SectionContainer className="mb-3 p-4">
      <Text className="text-xs uppercase tracking-[1px] text-ink-soft">{title}</Text>
      {lines.map((line) => (
        <Text key={line} className="mt-2 text-sm text-ink-soft">
          {line}
        </Text>
      ))}
    </SectionContainer>
  );
}
