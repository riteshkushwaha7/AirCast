import { useState } from "react";
import { ScrollView, Text, View, Pressable } from "react-native";

import { AppHeader } from "../components/layout";
import { AppTextInput, PrimaryButton, SectionContainer } from "../components/ui";
import { askAssistant } from "../services/api";
import { mockAssistantExamples } from "../services/mock-data";

export default function AssistantScreen() {
  const [question, setQuestion] = useState(mockAssistantExamples[0]);
  const [response, setResponse] = useState("Ask a question to get a simple explanation.");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    const result = await askAssistant({
      location_label: "Delhi",
      current_aqi: 168,
      current_category: "unhealthy",
      recommendation_text: "Wear a mask and reduce prolonged outdoor exposure.",
      trend_summary: "AQI likely worsens toward evening"
    });
    setResponse(result.explanation);
    setLoading(false);
  };

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader title="Assistant" subtitle="Simple explanations for your forecast and recommendations." />

      <SectionContainer>
        <AppTextInput value={question} onChangeText={setQuestion} placeholder="Ask about your AQI forecast" className="h-12" />
        <View className="mt-3">
          <PrimaryButton label={loading ? "Explaining..." : "Ask"} onPress={handleAsk} disabled={loading} />
        </View>
      </SectionContainer>

      <SectionContainer className="mt-3">
        <Text className="text-xs uppercase tracking-wide text-ink-soft">Response</Text>
        <Text className="mt-2 text-sm text-ink">{response}</Text>
        <Text className="mt-2 text-xs text-ink-soft">
          My AirCast Assistant explains structured forecast outputs and does not generate AQI predictions.
        </Text>
      </SectionContainer>

      <SectionContainer className="mt-3">
        <Text className="text-sm font-semibold text-ink">Try asking</Text>
        <View className="mt-2 gap-2">
          {mockAssistantExamples.map((item) => (
            <Pressable key={item} onPress={() => setQuestion(item)} className="rounded-xl border border-line px-3 py-2">
              <Text className="text-sm text-ink-soft">{item}</Text>
            </Pressable>
          ))}
        </View>
      </SectionContainer>
    </ScrollView>
  );
}
