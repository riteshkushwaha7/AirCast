import { ToggleRow } from "@/components/forms/toggle-row";
import { SectionCard } from "@/components/cards/section-card";

export function NotificationPreferenceCard({
  title,
  description,
  enabled,
}: {
  title: string;
  description: string;
  enabled: boolean;
}) {
  return (
    <SectionCard className="p-4">
      <ToggleRow title={title} description={description} enabled={enabled} />
    </SectionCard>
  );
}

