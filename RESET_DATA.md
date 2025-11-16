# Reset Data Commands

This document contains commands to completely reset all data from ContriBook, including users, teams, contributions, and blockchain data.

## ⚠️ WARNING

**These commands will permanently delete ALL data. Use with caution!**

## Prerequisites

- PostgreSQL database access
- Access to the backend directory
- Python 3.11+ installed

## Complete Reset (All Data)

### Option 1: Using PostgreSQL Commands

```bash
# Connect to PostgreSQL
psql -U your_username -d contribook

# Drop all tables (this will delete everything)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO your_username;
GRANT ALL ON SCHEMA public TO public;

# Exit psql
\q
```

### Option 2: Using Python Script

Create a reset script `backend/reset_database.py`:

```python
from app.database import engine, Base
from app.models import User, Team, Contribution, Verification, Flag
import os
import shutil
from app.config import settings

def reset_all():
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Recreate tables
    Base.metadata.create_all(bind=engine)
    
    # Delete blockchain storage
    if os.path.exists(settings.BLOCKCHAIN_STORAGE_PATH):
        shutil.rmtree(settings.BLOCKCHAIN_STORAGE_PATH)
        os.makedirs(settings.BLOCKCHAIN_STORAGE_PATH)
    
    # Delete encrypted storage
    if os.path.exists(settings.ENCRYPTED_STORAGE_PATH):
        shutil.rmtree(settings.ENCRYPTED_STORAGE_PATH)
        os.makedirs(settings.ENCRYPTED_STORAGE_PATH)
    
    # Delete archives
    if os.path.exists(settings.ARCHIVE_PATH):
        shutil.rmtree(settings.ARCHIVE_PATH)
        os.makedirs(settings.ARCHIVE_PATH)
    
    # Delete old blockchain.db if it exists
    if os.path.exists(settings.BLOCKCHAIN_DB_PATH):
        os.remove(settings.BLOCKCHAIN_DB_PATH)
    
    print("✅ All data reset successfully!")

if __name__ == "__main__":
    reset_all()
```

Run it:
```bash
cd backend
python3 reset_database.py
```

## Reset Specific Components

### Reset Only Users

```sql
-- Connect to PostgreSQL
psql -U your_username -d contribook

-- Delete all users (this will cascade to teams, contributions, etc.)
DELETE FROM users CASCADE;

-- Exit
\q
```

### Reset Only Teams and Contributions

```sql
-- Connect to PostgreSQL
psql -U your_username -d contribook

-- Delete all teams (this will cascade to contributions)
DELETE FROM teams CASCADE;

-- Exit
\q
```

### Reset Only Blockchain Data

```bash
cd backend

# Delete all blockchain database files
rm -rf blockchain_storage/*

# Delete old blockchain.db if it exists
rm -f blockchain.db
```

### Reset Only Encrypted Files

```bash
cd backend

# Delete all encrypted files
rm -rf encrypted_storage/*
```

## Docker Reset

If using Docker Compose:

```bash
# Stop containers
docker-compose down

# Remove volumes (this deletes all data)
docker-compose down -v

# Remove blockchain storage
rm -rf backend/blockchain_storage/*
rm -rf backend/encrypted_storage/*
rm -rf backend/archives/*

# Restart
docker-compose up -d
```

## Quick Reset Script

Create `reset.sh` in the project root:

```bash
#!/bin/bash

echo "⚠️  WARNING: This will delete ALL data!"
read -p "Are you sure? Type 'yes' to continue: " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 1
fi

# Reset database
cd backend
python3 -c "
from app.database import engine, Base
from app.models import User, Team, Contribution, Verification, Flag
import os
import shutil
from app.config import settings

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

if os.path.exists(settings.BLOCKCHAIN_STORAGE_PATH):
    shutil.rmtree(settings.BLOCKCHAIN_STORAGE_PATH)
    os.makedirs(settings.BLOCKCHAIN_STORAGE_PATH)

if os.path.exists(settings.ENCRYPTED_STORAGE_PATH):
    shutil.rmtree(settings.ENCRYPTED_STORAGE_PATH)
    os.makedirs(settings.ENCRYPTED_STORAGE_PATH)

if os.path.exists(settings.ARCHIVE_PATH):
    shutil.rmtree(settings.ARCHIVE_PATH)
    os.makedirs(settings.ARCHIVE_PATH)

if os.path.exists(settings.BLOCKCHAIN_DB_PATH):
    os.remove(settings.BLOCKCHAIN_DB_PATH)

print('✅ Reset complete!')
"

echo "✅ All data has been reset!"
```

Make it executable and run:
```bash
chmod +x reset.sh
./reset.sh
```

## Verification

After resetting, verify the database is empty:

```sql
-- Connect to PostgreSQL
psql -U your_username -d contribook

-- Check table counts
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM teams) as teams,
    (SELECT COUNT(*) FROM contributions) as contributions,
    (SELECT COUNT(*) FROM verifications) as verifications,
    (SELECT COUNT(*) FROM flags) as flags;

-- Should all return 0
\q
```

## Notes

- **Backup First**: Always backup your data before resetting
- **Environment Variables**: Make sure your `.env` file has correct database credentials
- **Permissions**: Ensure you have proper database permissions
- **Blockchain Files**: Each team has its own blockchain file in `blockchain_storage/`, all will be deleted
- **Encrypted Files**: All uploaded files will be permanently deleted

