# Development Guide

> Complete guide to developing, testing, and debugging The Private Council

This guide covers everything you need to know to contribute code to this project, from making your first change to verifying it works correctly.

**Prerequisites:** You should have already completed the [Getting Started Guide](GETTING_STARTED.md) and have the project running.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Understanding the Architecture](#understanding-the-architecture)
3. [The Critical Rule: Rebuild, Don't Restart](#the-critical-rule-rebuild-dont-restart)
4. [Making Backend Changes](#making-backend-changes)
5. [Making Frontend Changes](#making-frontend-changes)
6. [Testing Your Changes](#testing-your-changes)
7. [Debugging Workflow](#debugging-workflow)
8. [Common Pitfalls](#common-pitfalls)
9. [Quick Reference](#quick-reference)

---

## Development Setup

### Choose Your Development Method

You have two options for development:

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| **Docker** | Matches production, isolated environment | Requires rebuilds for code changes | Most contributors |
| **Manual** | Instant code updates, easier debugging | More setup, environment differences | Backend-heavy work |

### Docker Development Setup

```bash
# Clone the repo (if you haven't already)
git clone https://github.com/pawn002/private-llm-council.git
cd private-llm-council

# Copy environment configuration
cp .env.example .env

# Start services
docker compose up -d

# View logs (useful for development)
docker compose logs -f
```

### Manual Development Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .

# Run the server
python -m src.main
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

---

## Understanding the Architecture

### System Overview

```
Browser → nginx (localhost:3000) → backend (backend:8000) → Ollama (host.docker.internal:11434)
```

**Key components:**
- **Frontend**: Angular SPA served by nginx
- **Backend**: FastAPI Python server
- **Ollama**: Local LLM inference engine

### Data Flow

1. User submits question via web UI
2. nginx proxies request to backend (`/api/*` → `backend:8000`)
3. Backend orchestrates deliberation with multiple models via Ollama
4. Backend streams responses back via Server-Sent Events (SSE)
5. Frontend displays perspectives and synthesis in real-time

### Important Interfaces

**SSE Stream Events (backend → frontend):**
```json
{"type": "status", "message": "Starting deliberation..."}
{"type": "complete", "deliberation": {...}}
{"type": "error", "message": "..."}
```

**Deliberation Response Structure:**
```typescript
{
  synthesis: {
    content: string,
    consensus_points: string[],
    divisions: string[],
    unique_insights: string[],
    confidence: {...}
  },
  perspectives: [
    {
      member_id: string,
      model: string,
      character: string,
      content: string,
      timestamp: string
    }
  ]
}
```

**Common mistake:** Backend sends field names that don't match frontend TypeScript interfaces. Always verify both sides match!

---

## The Critical Rule: Rebuild, Don't Restart

### Why This Matters

**Docker containers have code baked into the image at build time.**

When you edit a Python or TypeScript file, that change exists on your host machine, but **not inside the running container**. The container is still running the old code from when the image was built.

### Wrong ❌

```bash
# Edit backend/src/main.py
docker compose restart backend  # Does NOT pick up code changes!
```

The container restarts, but it's using the **old image** that still has the old code.

### Correct ✅

```bash
# Edit backend/src/main.py
docker compose build backend    # Rebuild image with new code
docker compose up -d backend    # Recreate container with new image
```

Now the container runs the **new image** with your updated code.

### Quick Reference: What Requires a Rebuild?

| File Changed | Rebuild Required? | Command |
|-------------|-------------------|---------|
| `backend/src/*.py` | **YES** | `docker compose build backend && docker compose up -d backend` |
| `frontend/src/**/*` | **YES** | `docker compose build frontend && docker compose up -d frontend` |
| `frontend/nginx.conf` | **YES** | `docker compose build frontend && docker compose up -d frontend` |
| `config/sovereign_council.yaml` | **NO** (mounted) | `docker compose restart backend` |
| `.env` | **NO** (mounted) | `docker compose restart backend` |
| `docker-compose.yml` | **FULL RESTART** | `docker compose down && docker compose up -d` |

---

## Making Backend Changes

### 1. Edit the Code

```bash
# Example: editing the deliberation endpoint
vim backend/src/main.py
```

### 2. Rebuild and Deploy

**If using Docker:**
```bash
docker compose build backend
docker compose up -d backend
```

**If using manual setup:**
- Just save the file - FastAPI auto-reloads in development mode
- Watch the console for reload confirmation

### 3. Check Logs

```bash
# Docker
docker compose logs backend --tail 50

# Manual
# Watch the terminal where you ran `python -m src.main`
```

**Look for:**
- Import errors
- Syntax errors
- Startup failures
- Port binding issues

### 4. Verify the Change

**First, test the API directly** (before opening the browser):

```bash
# Test health endpoint
curl http://localhost:3000/api/health

# Test deliberation endpoint
curl -X POST http://localhost:3000/api/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question":"What is 2+2?"}'

# Test SSE stream endpoint
timeout 180 curl -N "http://localhost:3000/api/deliberate/stream?question=test"
```

**Why curl first?**
- Confirms backend is actually working
- Shows exact response structure
- Eliminates browser/frontend as source of issues
- Faster than browser testing

### 5. Test in Browser

Only after curl tests pass:
1. Open DevTools **before** submitting the request
2. Go to Network tab
3. Submit your test request
4. Check Console tab for JavaScript errors
5. Verify Response Preview shows expected structure

---

## Making Frontend Changes

### 1. Edit the Code

```bash
# Example: editing the deliberation component
vim frontend/src/app/components/deliberation/deliberation.component.ts
```

### 2. Rebuild and Deploy

**If using Docker:**
```bash
docker compose build frontend
docker compose up -d frontend
```

**If using manual setup:**
- Just save the file - Angular auto-reloads in development mode
- Watch the console for compilation status

### 3. Clear Browser Cache

Frontend changes often get cached by the browser:

```bash
# Hard refresh (clears cached JavaScript)
Ctrl + F5        # Windows/Linux
Cmd + Shift + R  # macOS
```

Or open DevTools → Network tab → check "Disable cache"

### 4. Check Browser Console

Look for:
- TypeScript compilation errors
- Runtime errors
- Failed network requests
- Type mismatches

### 5. Verify the Change

1. Test the affected UI component
2. Check Network tab for API requests
3. Verify request/response payloads
4. Confirm data displays correctly

---

## Testing Your Changes

### Testing Hierarchy

Always test in this order:

1. **Backend API** (curl) → Confirms backend works
2. **Browser Network** → Confirms frontend → backend communication
3. **UI rendering** → Confirms frontend displays data correctly

### Backend API Testing

```bash
# Save response to inspect structure
curl -X POST http://localhost:3000/api/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}' > /tmp/response.json

# Pretty-print for inspection
cat /tmp/response.json | python -m json.tool

# Test SSE streaming (timeout prevents hanging)
timeout 180 curl -N "http://localhost:3000/api/deliberate/stream?question=test"
```

### Frontend Testing Checklist

- [ ] Open DevTools before testing
- [ ] Network tab shows request sent
- [ ] Request payload is correct
- [ ] Response status is 200 (or expected error code)
- [ ] Response structure matches TypeScript interface
- [ ] Console has no errors
- [ ] UI displays data correctly
- [ ] Edge cases handled (empty data, errors, etc.)

### Verify Data Structure Matches

**Common issue:** Backend sends different structure than frontend expects.

**Check both sides:**

1. **Backend** - Look at the Python dataclass or dict:
   ```python
   # backend/src/council.py
   @dataclass
   class Perspective:
       member_id: str  # Note: "member_id"
       model: str
       content: str
   ```

2. **Frontend** - Look at the TypeScript interface:
   ```typescript
   // frontend/src/app/models/index.ts
   export interface Perspective {
     member_id: string;  // Must match backend!
     model: string;
     content: string;
   }
   ```

If these don't match exactly, you'll see runtime errors or missing data in the UI.

---

## Debugging Workflow

### When Something Doesn't Work

Follow this systematic approach:

#### Step 1: Verify Container is Using New Code

```bash
# Check container creation time
docker compose ps
```

Look at the "Created" column. If it's **before** your code change, you forgot to rebuild!

```bash
docker compose build <service>
docker compose up -d <service>
```

#### Step 2: Check Logs for Errors

```bash
# Backend logs
docker compose logs backend --tail 50

# Frontend logs
docker compose logs frontend --tail 50

# Follow logs in real-time
docker compose logs -f backend
```

**Common errors:**
- Import errors (missing dependencies)
- Syntax errors
- Port conflicts
- Connection to Ollama failed

#### Step 3: Verify API Response

```bash
# Test endpoint and inspect response
curl -s http://localhost:3000/api/deliberate \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}' | python -m json.tool
```

**Look for:**
- Response structure
- Missing fields
- Type mismatches (string vs object)
- Extra/unexpected fields

#### Step 4: Check Browser Console and Network

1. Open DevTools (F12)
2. Go to Console tab - look for errors
3. Go to Network tab - find the API request
4. Click the request → Preview tab
5. Compare to what you expect

#### Step 5: Compare Backend Output to Frontend Expectations

Read both sides of the interface:
- Backend: Python dataclass or dict structure
- Frontend: TypeScript interface

Ensure they match **exactly** - field names, types, nesting.

### Debugging Tools

```bash
# View file inside container (verify changes are there)
docker compose exec backend cat /app/src/main.py | grep -A 5 "function_name"

# Get a shell inside container
docker compose exec backend /bin/bash

# Check if Ollama is reachable from host
curl http://localhost:11434/api/tags

# Check if backend can reach Ollama
docker compose exec backend curl http://host.docker.internal:11434/api/tags

# Restart everything (nuclear option)
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## Common Pitfalls

### 1. Restarting Instead of Rebuilding

**Symptom:** "I changed the code but it's still broken"

**Cause:** Container is using old image

**Fix:**
```bash
docker compose build <service>
docker compose up -d <service>
```

**How to prevent:** Always rebuild after code changes. Get in the habit:
```bash
# Make this muscle memory
docker compose build backend && docker compose up -d backend
```

### 2. Testing in Browser Before Verifying API

**Symptom:** "Browser shows errors but I can't tell why"

**Cause:** Assuming backend works without testing it first

**Fix:** Always test with curl before opening browser

### 3. Frontend JavaScript Caching

**Symptom:** "Frontend shows old behavior after rebuild"

**Cause:** Browser cached old JavaScript

**Fix:**
- Hard refresh: `Ctrl+F5` (Windows/Linux) or `Cmd+Shift+R` (macOS)
- Or: Open DevTools → Network → check "Disable cache"

### 4. Not Checking Container Logs

**Symptom:** "Container is running but not working"

**Cause:** Container may have startup errors that aren't visible

**Fix:**
```bash
docker compose logs <service> --tail 50
```

The service might appear "Up" but actually be crashing and restarting.

### 5. Docker Network Confusion

**Symptom:** "Can't connect to Ollama from backend"

**Cause:** Using `localhost` instead of `host.docker.internal`

**Fix:** In Docker containers:
- `localhost` = the container itself
- `host.docker.internal` = your host machine

For backend to reach Ollama on host:
```yaml
# config/sovereign_council.yaml
gateway:
  url: "http://host.docker.internal:11434"  # NOT localhost:11434
```

### 6. Forgetting CORS Headers

**Symptom:** "EventSource fails immediately in browser"

**Cause:** nginx proxy missing CORS headers for SSE

**Fix:** Check `frontend/nginx.conf` has CORS headers in `/api/` location:
```nginx
location /api/ {
    add_header Access-Control-Allow-Origin *;
    # ... other config
}
```

### 7. Port Conflicts

**Symptom:** "Port already in use" or service won't start

**Cause:** Another service using port 3000 or 8000

**Fix:**
```bash
# Check what's using port 3000
netstat -ano | findstr :3000  # Windows
lsof -i :3000                 # macOS/Linux

# Either stop that service, or change port in .env
```

---

## Quick Reference

### Essential Commands

```bash
# === Docker Operations ===

# Rebuild and restart single service
docker compose build backend && docker compose up -d backend
docker compose build frontend && docker compose up -d frontend

# Rebuild and restart everything
docker compose down
docker compose build
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs --tail 50 backend

# Check status
docker compose ps

# Full reset (nuclear option - rebuilds everything from scratch)
docker compose down
docker compose build --no-cache
docker compose up -d

# === Testing Commands ===

# Test backend health
curl http://localhost:3000/api/health

# Test deliberation (POST)
curl -X POST http://localhost:3000/api/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question":"What is 2+2?"}'

# Test deliberation (SSE stream with timeout)
timeout 180 curl -N "http://localhost:3000/api/deliberate/stream?question=test"

# Save and inspect response
curl -X POST http://localhost:3000/api/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}' | python -m json.tool > /tmp/response.json

# Check if Ollama is reachable
curl http://localhost:11434/api/tags

# === Debugging Commands ===

# View file inside container (verify changes are present)
docker compose exec backend cat /app/src/main.py | head -20

# Get shell inside container
docker compose exec backend /bin/bash
docker compose exec frontend /bin/sh

# Check container resource usage
docker stats

# === Git Commands ===

# Check status before committing
git status
git diff

# Stage and commit changes
git add .
git commit -m "Description of changes"

# Push to remote
git push origin branch-name
```

### Development Workflow Cheatsheet

**Backend change:**
```bash
# 1. Edit file
vim backend/src/main.py

# 2. Rebuild
docker compose build backend && docker compose up -d backend

# 3. Check logs
docker compose logs backend --tail 50

# 4. Test with curl
curl http://localhost:3000/api/health

# 5. Test in browser (DevTools open!)
```

**Frontend change:**
```bash
# 1. Edit file
vim frontend/src/app/components/deliberation/deliberation.component.ts

# 2. Rebuild
docker compose build frontend && docker compose up -d frontend

# 3. Hard refresh browser
# Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (macOS)

# 4. Check browser console for errors
```

**Config change (no rebuild needed):**
```bash
# 1. Edit config
vim config/sovereign_council.yaml

# 2. Restart (NOT rebuild)
docker compose restart backend
```

---

## Pre-Commit Checklist

Before committing your changes:

- [ ] Code changes made and saved
- [ ] Docker image rebuilt (if applicable)
- [ ] Container recreated with new image
- [ ] Logs checked for errors
- [ ] API tested with curl (for backend changes)
- [ ] Response structure verified against TypeScript interfaces
- [ ] Browser tested with DevTools open
- [ ] No console errors
- [ ] UI displays data correctly
- [ ] Both POST and SSE endpoints work (if applicable)
- [ ] Changes tested on clean browser session (no cached data)
- [ ] Git status checked (`git status`)
- [ ] Only relevant files staged (`git add`)

---

## Getting Help

**Still stuck?**

1. **Check existing documentation:**
   - [GETTING_STARTED.md](GETTING_STARTED.md) - Initial setup
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md) - Performance tuning

2. **Search GitHub issues:**
   - Someone may have hit the same problem
   - https://github.com/pawn002/private-llm-council/issues

3. **Open a new issue:**
   - Include: OS, RAM, GPU (if applicable)
   - Include: Error messages, logs
   - Include: What you tried and what happened
   - Include: Docker or manual setup

---

## Contributing

Once you've made and tested your changes:

1. Create a feature branch: `git checkout -b feature/description`
2. Make your changes following this guide
3. Test thoroughly
4. Commit with clear messages
5. Push to your fork
6. Open a Pull Request

See [CONTRIBUTING_MODEST_HARDWARE.md](CONTRIBUTING_MODEST_HARDWARE.md) for ways to contribute without expensive hardware.

---

**Remember:** Docker containers are immutable. Code changes require image rebuilds, not just restarts. When in doubt, rebuild!
