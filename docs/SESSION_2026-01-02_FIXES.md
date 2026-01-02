# Session Log: 2026-01-02 - Docker Deployment Fixes

## Overview
This session resolved multiple issues preventing the Sovereign Council from running in Docker, culminating in the discovery of a critical Docker networking misconfiguration.

---

## Issues Encountered & Resolved

### 1. ✅ Docker Build Failure - README.md Not Found
**Issue**: Backend Docker build failed with permission error trying to access `/data/deliberations`

**Root Cause**:
- `backend/src/main.py:56` calculated storage path incorrectly: `Path(__file__).parent.parent.parent` = root `/`
- Non-root `council` user couldn't create `/data/deliberations`

**Fix**:
```python
# backend/src/main.py:58-64
data_dir = os.getenv("SOVEREIGN_COUNCIL_DATA_DIR")
if data_dir:
    storage_dir = Path(data_dir) / "deliberations"
else:
    storage_dir = Path(__file__).parent.parent / "data" / "deliberations"
```

**Files Modified**:
- `backend/src/main.py` - Added `import os` and environment variable check
- `docker-compose.yml` - Removed obsolete `version: '3.8'`

---

### 2. ✅ Configuration Not Loading from Environment
**Issue**: `SOVEREIGN_COUNCIL_CONFIG` environment variable was set but ignored

**Root Cause**:
- `backend/src/main.py:54` called `load_config()` without checking env var

**Fix**:
```python
# backend/src/main.py:54-56
config_path_str = os.getenv("SOVEREIGN_COUNCIL_CONFIG")
config_path = Path(config_path_str) if config_path_str else None
_config = load_config(config_path)
```

**Files Modified**:
- `backend/src/main.py`

---

### 3. ✅ Privacy Mode Incompatible with Docker
**Issue**: Default "sanctuary" mode blocked Docker deployment

**Root Cause**:
- Sanctuary mode requires strict network isolation
- Docker containers inherently have network access
- Privacy check failed on startup

**Fix**:
```yaml
# config/sovereign_council.yaml:26
mode: "citadel"  # Changed from "sanctuary"
```

**Files Modified**:
- `config/sovereign_council.yaml`

---

### 4. ✅ Missing Gateway Warmup Configuration
**Issue**: `GatewayConfig.warmup` attribute not found

**Root Cause**:
- Config YAML had `gateway.warmup.enabled` structure
- Pydantic model `GatewayConfig` didn't have `warmup` field
- Config parser didn't extract the warmup setting

**Fix**:
```python
# backend/src/config.py:57
class GatewayConfig(BaseModel):
    # ... existing fields
    warmup: bool = False

# backend/src/config.py:163-173
warmup_enabled = False
if "warmup" in gw and isinstance(gw["warmup"], dict):
    warmup_enabled = gw["warmup"].get("enabled", False)
gateway = GatewayConfig(
    # ... existing fields
    warmup=warmup_enabled,
)
```

**Files Modified**:
- `backend/src/config.py`

---

### 5. ✅ API Endpoint Path Mismatch
**Issue**: Frontend requested `/api/privacy/status`, backend had `/privacy-status`

**Root Cause**:
- Frontend: `api.service.ts:40` - `${API_BASE}/privacy/status`
- Backend: `main.py:336` - `@app.get("/privacy-status")`
- Nginx proxy: `/api/privacy/status` → `http://backend:8000/privacy/status` → 404

**Fix**:
```python
# backend/src/main.py:336
@app.get("/privacy/status")  # Changed from "/privacy-status"
async def privacy_status():
```

**Files Modified**:
- `backend/src/main.py`

---

### 6. ✅ Unhelpful Error Messages
**Issue**: Generic "400 Bad Request" errors didn't explain Ollama was missing

**Root Cause**:
- All ValueError exceptions converted to 400
- No pre-flight gateway health check
- Users had no idea what was wrong

**Fix**:
```python
# backend/src/main.py:257-268
# Check gateway health before attempting deliberation
if _gateway:
    gateway_health = await _gateway.health_check()
    if not gateway_health.healthy:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Inference gateway is unavailable: {gateway_health.message}. "
                f"Please ensure Ollama is running at {_config.gateway.url} "
                f"and the required models are pulled."
            )
        )

# backend/src/main.py:332-348
except ValueError as e:
    error_msg = str(e)
    if "Insufficient council members" in error_msg:
        raise HTTPException(
            status_code=503,
            detail=(
                f"{error_msg} This typically means the inference gateway "
                f"(Ollama) is not responding. Please check:\n"
                f"1. Ollama is running at {_config.gateway.url}\n"
                f"2. Required models are pulled: {', '.join([m.model for m in _config.council.members])}\n"
                f"3. Network connectivity to the gateway"
            )
        )
    else:
        raise HTTPException(status_code=400, detail=error_msg)
```

**Files Modified**:
- `backend/src/main.py`

---

### 7. ✅ CRITICAL: Docker Networking Misconfiguration
**Issue**: Backend couldn't connect to Ollama despite it running on host

**Root Cause**:
- Config: `url: "http://localhost:11434/v1"`
- Inside Docker container, `localhost` = the container itself, not the host machine
- Ollama was running on Windows host at `127.0.0.1:11434`
- Container's localhost ≠ Host's localhost

**Discovery Process**:
1. User noticed `curl http://localhost:11434/v1/models` triggered security warning
2. Ran `netstat -ano | findstr :11434` → Ollama IS listening
3. Ran `tasklist | findstr ollama` → Ollama IS running (PID 13888)
4. Realized Docker containers need `host.docker.internal` to reach host

**Fix**:
```yaml
# config/sovereign_council.yaml:58
url: "http://host.docker.internal:11434/v1"  # Changed from "http://localhost:11434/v1"
```

**Verification**:
```bash
# Before fix:
WARNING - Gateway health check failed: Cannot connect to gateway

# After fix:
INFO - Gateway healthy. Available models: ['tinyllama:1.1b', 'llama3.2:1b', 'qwen2.5:0.5b']
```

**Files Modified**:
- `config/sovereign_council.yaml`

---

### 8. ✅ Model Configuration Mismatch
**Issue**: Config expected models not pulled in Ollama

**Root Cause**:
- Config specified: `llama3.2:8b`, `mistral:7b`, `qwen2.5:7b`
- Ollama had: `llama3.2:1b`, `tinyllama:1.1b`, `qwen2.5:0.5b`
- Warmup failed with 404 errors

**Fix**:
```yaml
# config/sovereign_council.yaml:84-105
council:
  members:
    - id: "phi"
      model: "llama3.2:1b"      # Changed from llama3.2:8b

    - id: "psi"
      model: "tinyllama:1.1b"   # Changed from mistral:7b

    - id: "omega"
      model: "qwen2.5:0.5b"     # Changed from qwen2.5:7b

  chairman:
    model: "llama3.2:1b"        # Changed from llama3.2:70b
```

**Files Modified**:
- `config/sovereign_council.yaml`

---

## Remaining Issue: ⏳ Request Timeout

### Issue
Deliberations timeout after 60 seconds (nginx default) but backend is still processing.

### Symptoms
```
504 Gateway Time-out
```

Backend logs show continued processing:
```
INFO - Deliberation requested
HTTP Request: POST .../v1/chat/completions "HTTP/1.1 200 OK"
[continues for 2-3 minutes]
```

### Root Cause
- Small models (0.5-1.1B params) are slow on CPU
- Deliberation process: 3 perspectives + peer review + synthesis = multiple model calls
- Each model call takes 10-20 seconds
- Total time: 2-3 minutes
- Nginx default timeout: 60 seconds

### Potential Solutions (TODO)

#### Option 1: Increase Nginx Timeout
**File**: `frontend/nginx.conf:27-36`

Add to `/api/` location block:
```nginx
location /api/ {
    proxy_pass http://backend:8000/;
    proxy_read_timeout 300s;      # Add this (5 minutes)
    proxy_connect_timeout 300s;   # Add this
    proxy_send_timeout 300s;      # Add this
    # ... existing proxy settings
}
```

#### Option 2: Implement SSE Streaming
**Missing Endpoint**: `GET /api/deliberate/stream`

Currently:
- Frontend tries SSE: `/api/deliberate/stream` → 404
- Falls back to POST: `/api/deliberate` → works but slow

Should implement:
- Backend: Add `@app.get("/deliberate/stream")` with SSE
- Stream progress updates: "Collecting perspectives...", "Reviewing...", "Synthesizing..."
- Frontend already has fallback logic (`api.service.ts:80-90`)

#### Option 3: Use Faster/Larger Models
Pull better models:
```bash
ollama pull llama3.2:8b   # Faster than 1b on good hardware
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

Update config back to original larger models.

#### Option 4: Optimize Model Calls
- Run perspectives in parallel (may already be doing this)
- Reduce timeout per model in config
- Skip peer review for faster results

---

## Files Changed Summary

### Configuration Files
- `config/sovereign_council.yaml`
  - Privacy mode: `sanctuary` → `citadel`
  - Gateway URL: `localhost:11434` → `host.docker.internal:11434`
  - Council models: Updated to match available models

### Backend Code
- `backend/src/main.py`
  - Added `import os`
  - Fixed storage directory path resolution (env var support)
  - Fixed config loading (env var support)
  - Fixed `/privacy-status` → `/privacy/status` endpoint
  - Added gateway health check before deliberation
  - Improved error messages (400 → 503 with details)

- `backend/src/config.py`
  - Added `warmup: bool` to `GatewayConfig`
  - Updated config parser to extract warmup setting

### Docker
- `docker-compose.yml`
  - Removed obsolete `version: '3.8'`

---

## Key Learnings

### 1. Docker Networking Is Not Localhost
**Critical Discovery**: Inside Docker containers, `localhost` refers to the container itself, not the host machine.

- ❌ `http://localhost:11434` - Container's localhost
- ✅ `http://host.docker.internal:11434` - Host machine (Windows/Mac)
- ✅ `http://172.17.0.1:11434` - Docker bridge IP (Linux alternative)

### 2. Always Check Gateway Health First
Before attempting deliberation, verify:
```python
gateway_health = await _gateway.health_check()
if not gateway_health.healthy:
    raise HTTPException(status_code=503, detail=helpful_message)
```

### 3. Error Messages Matter
Changed from:
```
400 Bad Request
"Insufficient council members responded (0 < 2)"
```

To:
```
503 Service Unavailable
"Inference gateway unavailable. Please check:
1. Ollama running at http://host.docker.internal:11434/v1
2. Required models pulled: llama3.2:1b, tinyllama:1.1b, qwen2.5:0.5b
3. Network connectivity to gateway"
```

### 4. Environment Variables for Config Paths
Use environment variables for:
- Config file paths
- Data directory paths
- Gateway URLs

Allows different values for:
- Development (localhost)
- Docker (host.docker.internal)
- Production (custom URLs)

---

## Testing Checklist

- [x] Docker build succeeds
- [x] Containers start healthy
- [x] Gateway health check passes
- [x] Privacy status endpoint returns 200
- [x] Models warm up successfully
- [x] Deliberation request starts processing
- [ ] Deliberation completes before timeout (TODO - see timeout issue above)

---

## Next Steps

1. **Address Timeout Issue** (choose one solution above)
2. **Pull larger models** for better performance (if hardware allows)
3. **Implement SSE streaming endpoint** for better UX
4. **Add monitoring** for deliberation processing time
5. **Consider caching** model responses for repeated questions

---

## Commands for Reference

### Check Ollama Status (Windows)
```bash
# Check if Ollama is listening
netstat -ano | findstr :11434

# Check if Ollama process is running
tasklist | findstr -i ollama

# Test Ollama API
curl http://localhost:11434/api/tags
```

### Docker Commands
```bash
# Rebuild and restart
docker compose down
docker compose build backend
docker compose up -d

# View logs
docker compose logs backend --tail 50
docker compose logs frontend --tail 50

# Check status
docker compose ps

# Restart specific service
docker compose restart backend
```

### Pull Ollama Models
```bash
# Lightweight (current setup)
ollama pull llama3.2:1b
ollama pull tinyllama:1.1b
ollama pull qwen2.5:0.5b

# Standard (original config)
ollama pull llama3.2:8b
ollama pull mistral:7b
ollama pull qwen2.5:7b

# Large (if you have 24GB+ VRAM)
ollama pull llama3.2:70b
```

### Test Endpoints
```bash
# Health check
curl http://localhost:3000/api/health

# Privacy status
curl http://localhost:3000/api/privacy/status

# Deliberation (will timeout, but backend processes)
curl -X POST http://localhost:3000/api/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question":"What is 2+2?"}'
```

---

## Session Duration
Approximately 2 hours of troubleshooting and fixes.

## Issues Resolved
8 major issues fixed, system now operational (pending timeout optimization).
