import { SectionCard } from "@/components/cards/section-card";

export function AssistantPromptCard({ prompt }: { prompt: string }) {
  return (
    <SectionCard className="p-4">
      <p className="text-sm text-ink">{prompt}</p>
    </SectionCard>
  );
}

