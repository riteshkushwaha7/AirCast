import { useEffect } from "react";

import { addNotificationListeners } from "../services/notifications";

export function useNotificationBridge() {
  useEffect(() => {
    const detach = addNotificationListeners(
      () => {
        // Placeholder: route to alert details in future versions.
      },
      () => {
        // Placeholder: open relevant screen from notification response.
      }
    );

    return () => {
      detach();
    };
  }, []);
}
