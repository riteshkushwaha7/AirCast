import { useEffect, useState } from "react";

import type { AlertSettings } from "../types/airwise";
import { getAlertSettings, updateAlertSettings } from "../services/api";
import { mockAlertSettings } from "../services/mock-data";

export function useAlertSettings() {
  const [settings, setSettings] = useState<AlertSettings>(mockAlertSettings);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const payload = await getAlertSettings();
        if (active) setSettings(payload);
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const updated = await updateAlertSettings(settings);
      setSettings(updated);
    } finally {
      setSaving(false);
    }
  };

  return { settings, setSettings, loading, saving, save };
}
