import { useCallback, useEffect, useState } from "react";

import type { AlertSettings } from "../types/airwise";
import { getAlertSettings, updateAlertSettings } from "../services/api";

export function useAlertSettings() {
  const [settings, setSettingsRaw] = useState<AlertSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const payload = await getAlertSettings();
        if (active) setSettingsRaw(payload);
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  const setSettings = useCallback((updater: (prev: AlertSettings) => AlertSettings) => {
    setSettingsRaw((prev) => (prev ? updater(prev) : prev));
  }, []);

  const save = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      const updated = await updateAlertSettings(settings);
      setSettingsRaw(updated);
    } finally {
      setSaving(false);
    }
  };

  return { settings, setSettings, loading, saving, save };
}
