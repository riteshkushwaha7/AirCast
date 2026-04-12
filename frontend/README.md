# AirWise Frontend Workspace

This folder contains both client applications:

- `web/` - Next.js web app
- `mobile/` - Expo React Native app

## Environment

Use `frontend/.env.example` as a reference.

- For web, copy `frontend/web/.env.local.example` to `frontend/web/.env.local`
- For mobile, copy `frontend/mobile/.env.example` to `frontend/mobile/.env`

## Run

Web:
```bash
cd frontend/web
npm install
npm run dev
```

Mobile:
```bash
cd frontend/mobile
npm install
npm run start
```

## Demo Mode

Keep these enabled for stable demos without live backend/model data:

- `NEXT_PUBLIC_ENABLE_MOCK_FALLBACK=true`
- `EXPO_PUBLIC_ENABLE_MOCK_FALLBACK=true`
