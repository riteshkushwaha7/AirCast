# Notification Service Structure

## Trigger Inputs
- Threshold crossing
- Worsening AQI in near horizon (4h)
- Daily morning summary
- Best outdoor window
- Wear mask recommendation
- Avoid outdoor recommendation

## Pipeline
1. Forecast service provides latest snapshot.
2. Alert engine evaluates rules with user profile + preferences.
3. Notification service builds message payload.
4. FCM token registry resolves recipient devices.
5. Delivery attempt is queued/sent.

## Message Shape
- `title`
- `body`
- `alert_type`
- `user_id`
- optional `location_id`, `aqi`, `horizon`

## Current Prototype Implementation
- In-memory token store in `notification_service.py`
- Device token registration endpoint: `/api/v1/notifications/device-token`
- Test dispatch endpoint: `/api/v1/notifications/test`

## Production Hardening Notes
- Persist tokens in PostgreSQL
- Add retry + dead-letter queue
- Respect quiet hours and local timezone
- Use event bus (Kafka/RabbitMQ) between alert engine and dispatcher
