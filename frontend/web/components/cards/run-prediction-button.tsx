"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { runPrediction } from "@/lib/api";

export function RunPredictionButton({ locationId }: { locationId: string }) {
  const [status, setStatus] = useState<"idle" | "loading" | "error">("idle");
  const router = useRouter();

  const handleRun = async () => {
    setStatus("loading");
    try {
      await runPrediction(locationId);
      router.refresh();
      setStatus("idle");
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Button
        variant="secondary"
        onClick={handleRun}
        disabled={status === "loading"}
      >
        {status === "loading" ? "Running…" : "Run Prediction"}
      </Button>
      {status === "error" && (
        <p className="text-xs text-red-500">Prediction failed, try again.</p>
      )}
    </div>
  );
}
