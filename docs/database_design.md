# Database Entity-Relationship Architecture

## Data Tables Map

### 1. `users` Table
- `id` (Integer, Primary Key)
- `username` (String, Unique, Index)
- `email` (String, Unique)
- `hashed_password` (String)
- `is_active` (Boolean)
- `is_admin` (Boolean)

### 2. `reports` Table
- `id` (Integer, Primary Key)
- `image_path` (String)
- `damage_category` (String)
- `severity_level` (String)
- `latitude` (Float, Nullable)
- `longitude` (Float, Nullable)
- `timestamp` (DateTime)

### 3. `damages` Table
- `id` (Integer, Primary Key)
- `report_id` (Integer, ForeignKey -> reports.id)
- `category` (String)
- `confidence` (Float)