if (-not $env:SOURCE_MOCK_MODE) { $env:SOURCE_MOCK_MODE = "true" }
if (-not $env:ALLOW_MOCK_AUTH) { $env:ALLOW_MOCK_AUTH = "true" }
if (-not $env:NEXT_PUBLIC_ENABLE_MOCK_FALLBACK) { $env:NEXT_PUBLIC_ENABLE_MOCK_FALLBACK = "true" }
if (-not $env:EXPO_PUBLIC_ENABLE_MOCK_FALLBACK) { $env:EXPO_PUBLIC_ENABLE_MOCK_FALLBACK = "true" }

docker compose up --build
