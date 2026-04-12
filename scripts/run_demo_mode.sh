#!/usr/bin/env bash
set -euo pipefail

export SOURCE_MOCK_MODE="${SOURCE_MOCK_MODE:-true}"
export ALLOW_MOCK_AUTH="${ALLOW_MOCK_AUTH:-true}"
export NEXT_PUBLIC_ENABLE_MOCK_FALLBACK="${NEXT_PUBLIC_ENABLE_MOCK_FALLBACK:-true}"
export EXPO_PUBLIC_ENABLE_MOCK_FALLBACK="${EXPO_PUBLIC_ENABLE_MOCK_FALLBACK:-true}"

docker compose up --build
