# ContriBook - Troubleshooting Guide

## Issue: Frontend Not Starting (Node.js Version)

**Problem**: Frontend container fails with error:
```
You are using Node.js 18.x. Vite requires Node.js version 20.19+ or 22.12+
```

**Solution**: Already fixed in the repository. The Dockerfile now uses Node.js 20.

If you cloned before this fix:
1. Make sure `frontend/Dockerfile` has `FROM node:20-alpine` (not `node:18-alpine`)
2. Rebuild: `docker-compose down && docker-compose up -d --build`

---

## Issue: Backend Import Error (email-validator)

**Problem**: Backend fails with:
```
ImportError: email-validator is not installed, run `pip install pydantic[email]`
```

**Solution**: Already fixed. The `requirements.txt` now includes `email-validator==2.1.0`.

If you cloned before this fix:
1. Add `email-validator==2.1.0` to `backend/requirements.txt`
2. Rebuild: `docker-compose up -d --build backend`

---

## Issue: Tailwind CSS PostCSS Plugin Error

**Problem**: Frontend fails with:
```
[postcss] It looks like you're trying to use `tailwindcss` directly as a PostCSS plugin.
The PostCSS plugin has moved to a separate package...
```

**Solution**: Already fixed. The `package.json` now uses Tailwind CSS v3.4.1 instead of v4.x, and the Dockerfile deletes package-lock.json before installing.

If you cloned before this fix:
1. Update `frontend/package.json` to use `"tailwindcss": "^3.4.1"`
2. Delete `frontend/package-lock.json`
3. Rebuild: `docker-compose down && docker rmi contribook-frontend && docker-compose build frontend && docker-compose up -d`

---

## Issue: Rollup ARM64 Module Not Found (Apple Silicon)

**Problem**: Frontend fails on Apple Silicon Macs with:
```
Error: Cannot find module @rollup/rollup-linux-arm64-musl
```

**Solution**: Already fixed. The Dockerfile now:
1. Installs build tools (python3, make, g++)
2. Deletes package-lock.json before npm install (avoids npm optional deps bug)

If you see this error:
1. Make sure `frontend/Dockerfile` has build dependencies installed
2. Rebuild: `docker-compose down && docker rmi contribook-frontend && docker-compose build frontend && docker-compose up -d`

---

## Common Issues

### 1. Port Already in Use

**Symptoms**:
- `Error: port is already allocated`
- Cannot access http://localhost:5173

**Solution**:
```bash
# Check what's using the port
lsof -i :5173  # For frontend
lsof -i :8000  # For backend
lsof -i :5432  # For PostgreSQL

# Kill the process or change ports in docker-compose.yml
```

### 2. Database Connection Failed

**Symptoms**:
- Backend logs show `could not connect to server`
- API returns 500 errors

**Solution**:
```bash
# Check PostgreSQL is healthy
docker-compose ps

# View database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Wait for health check
sleep 10 && docker-compose logs backend
```

### 3. Frontend Can't Reach Backend

**Symptoms**:
- Login fails with network error
- API calls timeout

**Solution**:
1. Check `frontend/.env`:
   ```
   VITE_API_URL=http://localhost:8000/api
   ```
2. Verify backend is running:
   ```bash
   curl http://localhost:8000
   ```
3. Check browser console for CORS errors

### 4. Permission Denied on setup.sh

**Symptoms**:
- `bash: ./setup.sh: Permission denied`

**Solution**:
```bash
chmod +x setup.sh
./setup.sh
```

### 5. Environment Variables Not Set

**Symptoms**:
- Backend fails to start
- Errors about missing SECRET_KEY or ENCRYPTION_KEY

**Solution**:
```bash
# Run setup script
./setup.sh

# Or manually create .env files:
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Generate keys:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 6. Docker Compose Version Warning

**Symptoms**:
- Warning about `version` attribute being obsolete

**Solution**: This is just a warning and can be ignored. The `version` field has been removed from docker-compose.yml.

---

## Verification Steps

After fixing issues, verify everything works:

### 1. Check All Containers Running
```bash
docker-compose ps

# Expected output:
# All containers should show "Up" status
# PostgreSQL should show "(healthy)"
```

### 2. Test Backend API
```bash
# Root endpoint
curl http://localhost:8000

# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux
```

### 3. Test Frontend
```bash
# Check if serving
curl -I http://localhost:5173

# Open in browser
open http://localhost:5173  # macOS
xdg-open http://localhost:5173  # Linux
```

### 4. Test Full Stack
1. Open http://localhost:5173
2. Click "Register"
3. Create an account
4. If successful, everything is working!

---

## View Logs

### All Services
```bash
docker-compose logs -f
```

### Specific Service
```bash
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Last N Lines
```bash
docker-compose logs --tail=50 backend
```

---

## Clean Start

If all else fails, clean slate:

```bash
# Stop and remove everything
docker-compose down -v

# Remove images (optional)
docker-compose down -v --rmi all

# Rebuild from scratch
docker-compose up -d --build

# Wait for services to start
sleep 10

# Check status
docker-compose ps
docker-compose logs
```

---

## Manual Setup (Without Docker)

If Docker isn't working, run manually:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### PostgreSQL
Install PostgreSQL locally and create database:
```sql
CREATE DATABASE contribook;
CREATE USER contribook WITH PASSWORD 'contribook';
GRANT ALL PRIVILEGES ON DATABASE contribook TO contribook;
```

Update `backend/.env`:
```
DATABASE_URL=postgresql://contribook:contribook@localhost:5432/contribook
```

---

## Getting Help

1. Check logs: `docker-compose logs`
2. Verify containers: `docker-compose ps`
3. Check ports: `lsof -i :5173`, `lsof -i :8000`
4. Test connectivity: `curl http://localhost:8000`
5. Review this guide for common issues

Still stuck? Open an issue on GitHub with:
- Output of `docker-compose ps`
- Relevant logs from `docker-compose logs`
- Steps to reproduce
