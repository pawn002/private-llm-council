# Plan A: DevOps Pivot - Local LLM Council

## Executive Summary

A straightforward infrastructure pivot from cloud-based OpenRouter to locally-hosted LLM inference servers. This approach treats the privacy requirement as an infrastructure concern and focuses on operational reliability, reproducibility, and minimal code changes.

---

## The Problem

Karpathy's llm-council routes all queries through OpenRouter, a cloud API aggregator. Every user question, every model response, and every peer review passes through third-party infrastructure. For privacy-conscious deployments, this is a non-starter:

- Queries may contain sensitive personal or business data
- Model responses are logged by external providers
- No guarantees on data retention or usage policies
- Network dependency introduces latency and availability risks

---

## The Solution: Infrastructure Swap

Replace OpenRouter with a local inference gateway that speaks the same OpenAI-compatible API format. The application code remains largely unchanged; we're just pointing the firehose at different plumbing.

### Target Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User's Machine                          │
│  ┌──────────┐     ┌──────────────┐     ┌────────────────┐  │
│  │ React    │────▶│ FastAPI      │────▶│ Local Gateway  │  │
│  │ Frontend │◀────│ Backend      │◀────│ (Ollama/vLLM)  │  │
│  └──────────┘     └──────────────┘     └───────┬────────┘  │
│                                                 │           │
│                         ┌───────────────────────┼───────┐   │
│                         │      Model Pool       │       │   │
│                         │  ┌─────────┐  ┌───────▼─────┐ │   │
│                         │  │ Llama 3 │  │ Mistral     │ │   │
│                         │  └─────────┘  └─────────────┘ │   │
│                         │  ┌─────────┐  ┌─────────────┐ │   │
│                         │  │ Qwen    │  │ Phi-3       │ │   │
│                         │  └─────────┘  └─────────────┘ │   │
│                         └───────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Local Inference Gateway Setup

**Option A: Ollama (Recommended for simplicity)**
- Single binary, cross-platform
- Built-in model management (`ollama pull llama3.2`)
- OpenAI-compatible API at `http://localhost:11434/v1`
- Supports concurrent model loading

**Option B: vLLM (Recommended for performance)**
- Higher throughput via PagedAttention
- Better GPU utilization for multi-model scenarios
- Requires more setup but scales better

**Option C: LM Studio (Recommended for non-technical users)**
- GUI-based model management
- One-click server deployment
- Good for prototyping

### Phase 2: Backend Modifications

```python
# Original (OpenRouter)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Pivoted (Local)
LOCAL_INFERENCE_URL = os.getenv("LLM_GATEWAY_URL", "http://localhost:11434/v1")
```

Key changes to `main.py` / council logic:
1. Replace OpenRouter base URL with configurable local endpoint
2. Remove OpenRouter API key requirement (or make optional)
3. Update model identifiers to local format (e.g., `llama3.2` vs `meta-llama/llama-3.2`)
4. Add health checks for local inference availability
5. Implement model warm-up on startup (first inference is slow)

### Phase 3: Model Selection Strategy

**Recommended Local Council Composition:**

| Role | Model | Size | Rationale |
|------|-------|------|-----------|
| Council Member 1 | Llama 3.2 | 8B | Strong general reasoning |
| Council Member 2 | Mistral 7B | 7B | Good instruction following |
| Council Member 3 | Qwen 2.5 | 7B | Diverse training corpus |
| Chairman | Llama 3.2 | 70B | Synthesis needs larger context |

**Hardware Requirements:**
- Minimum: 16GB RAM, 8GB VRAM (run 7B models sequentially)
- Recommended: 32GB RAM, 24GB VRAM (run multiple 7B models, one 70B)
- Optimal: 64GB RAM, 48GB+ VRAM (parallel inference)

### Phase 4: Configuration & Environment

```yaml
# config/local_council.yaml
gateway:
  url: "http://localhost:11434/v1"
  timeout: 120  # Local inference is slower
  retry_attempts: 3

council:
  members:
    - model: "llama3.2:8b"
      temperature: 0.7
    - model: "mistral:7b"
      temperature: 0.7
    - model: "qwen2.5:7b"
      temperature: 0.7
  chairman:
    model: "llama3.2:70b"
    temperature: 0.3

privacy:
  log_queries: false
  persist_conversations: true  # Local disk only
  telemetry: disabled
```

### Phase 5: Docker Compose Stack

```yaml
version: '3.8'
services:
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  backend:
    build: ./backend
    environment:
      - LLM_GATEWAY_URL=http://ollama:11434/v1
    depends_on:
      - ollama
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  ollama_data:
```

---

## Operational Considerations

### Startup Sequence
1. Launch Ollama/vLLM gateway
2. Pre-pull required models (`ollama pull llama3.2:8b`)
3. Warm up models with dummy inference
4. Start FastAPI backend
5. Start React frontend

### Monitoring
- GPU utilization (nvidia-smi)
- Inference latency per model
- Memory pressure alerts
- Model loading status

### Graceful Degradation
- If chairman model unavailable, fall back to largest available
- If < 3 council members available, warn user but continue
- Implement request queuing for resource contention

---

## Migration Checklist

- [ ] Choose inference gateway (Ollama recommended)
- [ ] Inventory available hardware (GPU/RAM)
- [ ] Select appropriate model sizes
- [ ] Fork llm-council repository
- [ ] Replace OpenRouter client with local client
- [ ] Update model identifiers
- [ ] Add configuration file support
- [ ] Create Docker Compose stack
- [ ] Write health check endpoints
- [ ] Test full council workflow locally
- [ ] Document hardware requirements
- [ ] Create model download script

---

## Trade-offs Acknowledged

| Aspect | Cloud (OpenRouter) | Local (This Plan) |
|--------|-------------------|-------------------|
| Setup Complexity | Low | Medium-High |
| Hardware Cost | None (pay per token) | Significant upfront |
| Model Quality | Access to GPT-5, Claude | Limited to open weights |
| Latency | ~1-3s per response | ~5-30s per response |
| Privacy | Poor | Excellent |
| Offline Capability | None | Full |
| Maintenance | Provider handles | Self-managed |

---

## Estimated Effort

- **Phase 1** (Gateway Setup): 2-4 hours
- **Phase 2** (Backend Mods): 4-8 hours
- **Phase 3-4** (Config): 2-3 hours
- **Phase 5** (Docker): 2-4 hours
- **Testing & Polish**: 4-8 hours

**Total: 14-27 hours for a competent engineer**

---

## Next Steps

1. Confirm hardware availability
2. Select inference gateway
3. Begin Phase 1 implementation
4. Iterate based on performance testing

---

*This plan treats privacy as an infrastructure problem. For a deeper examination of the philosophical implications of private AI deliberation, see PLAN_PHILOSOPHICAL.md*
