import { Text, View } from "react-native";

import { SectionContainer } from "./SectionContainer";
import { PrimaryButton } from "./PrimaryButton";

export function ErrorState({
  title,
  message,
  onRetry
}: {
  title: string;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <SectionContainer className="border-unhealthy/30 bg-unhealthy/5">
      <Text className="text-base font-semibold text-unhealthy">{title}</Text>
      <Text className="mt-2 text-sm text-ink-soft">{message}</Text>
      {onRetry ? (
        <View className="mt-3">
          <PrimaryButton label="Retry" onPress={onRetry} />
        </View>
      ) : null}
    </SectionContainer>
  );
}
