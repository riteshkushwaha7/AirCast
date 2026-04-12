# AirWise Project Overview

## Problem Statement

Air quality can change quickly, but most users do not get simple, personalized guidance on what those changes mean for daily activity.

## Why AirWise Matters

AirWise turns AQI data and forecasts into practical decisions:

- Is it okay to go out now?
- Should I wear a mask?
- Which day this week is better for outdoor activity?

## Project Goals

- Provide clear AQI forecasting for short and weekly horizons
- Personalize guidance using health profile and sensitivity
- Support actionable alerts and planning, not just raw numbers
- Stay demo-friendly with fallback/mock behavior

## Major Modules

- Web app: daily AQI decisions and planner view
- Mobile app: glanceable AQI + planner + alerts
- Backend API: auth/profile/location/forecast/recommendation/planner/alerts
- Data stores:
  - PostgreSQL for relational app data
  - InfluxDB for AQI time-series
- ML/data pipeline: ingestion, preprocessing, feature generation, planner projection hooks

## End-User Flow

1. User signs in
2. User sets location and health profile
3. Dashboard shows current AQI and near-term forecast
4. Recommendation engine provides concise action advice
5. Alerts notify important changes
6. Weekly planner helps schedule outdoor activities by day
