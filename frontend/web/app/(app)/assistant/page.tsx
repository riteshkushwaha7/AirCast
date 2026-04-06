"use client";

import { useState } from "react";

import { AssistantPromptCard } from "@/components/cards/assistant-prompt-card";
import { PageHeader } from "@/components/layout/page-header";
import { SectionCard } from "@/components/cards/section-card";
import { Button } from "@/components/ui/button";
import { TextArea } from "@/components/ui/textarea";
import { askAssistant } from "@/lib/api";
import { assistantExamplePrompts, mockAssistantResponse } from "@/lib/mock";

export default function AssistantPage() {
  const [question, setQuestion] = useState(assistantExamplePrompts[0]);
  const [response, setResponse] = useState(mockAssistantResponse.explanation);
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    setLoading(true);
    const result = await askAssistant({
      location_label: "Delhi",
      current_aqi: 168,
      current_category: "unhealthy",
      recommendation_text: "Wear a mask and reduce prolonged outdoor exposure.",
      trend_summary: "AQI likely rises toward evening",
    });
    setResponse(result.explanation);
    setLoading(false);
  };

  return (
    <div className="space-y-4">
      <PageHeader title="Assistant" subtitle="Ask questions about forecasts and recommendations in plain language." />

      <SectionCard className="space-y-3">
        <TextArea value={question} onChange={(event) => setQuestion(event.target.value)} rows={3} />
        <Button onClick={handleAsk} disabled={loading}>{loading ? "Explaining..." : "Ask"}</Button>
      </SectionCard>

      <SectionCard className="space-y-2">
        <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Assistant response</p>
        <p className="text-sm text-ink">{response}</p>
        <p className="text-xs text-ink-soft">Predictions come from My AirCast forecasting models. The assistant only explains them.</p>
      </SectionCard>

      <div className="space-y-2">
        {assistantExamplePrompts.map((prompt) => (
          <AssistantPromptCard key={prompt} prompt={prompt} />
        ))}
      </div>
    </div>
  );
}


