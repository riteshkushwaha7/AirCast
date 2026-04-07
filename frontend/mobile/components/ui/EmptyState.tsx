import { Text } from "react-native";

import { SectionContainer } from "./SectionContainer";

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <SectionContainer className="items-center border-dashed bg-surface-muted">
      <Text className="text-base font-semibold text-ink">{title}</Text>
      <Text className="mt-2 text-center text-sm text-ink-soft">{message}</Text>
    </SectionContainer>
  );
}
