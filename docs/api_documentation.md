# Operational API Endpoint Documentation

## Authentication Sub-System
All secure data actions expect an `Authorization` header containing a valid signed corporate token.
- **Header Structure:** `Authorization: Bearer <JWT_TOKEN_STRING>`

## Primary Versioned Route Subsets
- `POST /api/v1/auth/login`: Accepts credentials, yields access token payloads.
- `POST /api/v1/reports/submit`: Accepts image file multi-parts and latitude/longitude parameters.
- `GET /api/v1/dashboard/reports`: Returns summarized historical arrays.
- `GET /api/v1/analytics/summary`: Compiles high-level severity counts.