# Research: llama.cpp Cancellation Capabilities & API Assessment

**Issue Reference:** #18 - Reliance on Ollama is causing downstream UX fault
**Date:** 2026-01-03

## Executive Summary

**Verdict:** llama.cpp has **partial** cancellation support—better than Ollama for streaming, but with the same core limitation during prompt processing.

---

## Cancellation Capabilities

| Phase | Can Cancel? | How |
|-------|-------------|-----|
| **Token generation** (streaming) | ✅ Yes | Close connection / AbortController |
| **Prompt processing** (`llama_decode`) | ❌ No | Must wait for completion |
| **Queued requests** | ⚠️ Partial | Connection close removes from queue |

**Key finding:** The fundamental limitation is the same—during `llama_decode` (prompt processing), neither Ollama nor llama.cpp can interrupt mid-execution. This is an [open feature request in llama.cpp](https://github.com/ggml-org/llama.cpp/issues/10509).

**What works:** For streaming responses, closing the HTTP connection stops token generation. This is more reliable in llama.cpp than Ollama because llama.cpp's server is designed around a **slot-based architecture** that handles disconnections better.

---

## API Comparison

| Feature | Ollama | llama.cpp |
|---------|--------|-----------|
| OpenAI-compatible API | ✅ | ✅ |
| Streaming (SSE) | ✅ | ✅ |
| Cancel via disconnect | ⚠️ Poor | ✅ Better |
| Concurrent requests | Limited | Slot-based parallelism |
| Context window | ~11K tokens | ~32K tokens |
| Setup complexity | Simple | Requires compilation |

---

## llama.cpp Server Key Endpoints

```
POST /v1/chat/completions  - OpenAI-compatible chat
POST /completion           - Native completion API
GET  /health               - Health check
GET  /slots                - Monitor parallel request slots
GET  /metrics              - Prometheus metrics
```

Full docs: [llama.cpp server README](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)

---

## Advantages of llama.cpp for This Project

1. **Better disconnect handling** - Slot-based architecture properly releases resources when clients disconnect
2. **True parallel processing** - Multiple council members could query simultaneously via slots
3. **Larger context windows** - 32K vs 11K tokens on same hardware
4. **Lower-level control** - Can tune `n_batch` for more cancellation checkpoints

## Disadvantages

1. **Same prompt-phase limitation** - Large prompts still block until processed
2. **Harder deployment** - Requires compilation vs Ollama's one-click install
3. **No model management** - Must manually handle model files (no `ollama pull`)
4. **More configuration** - Requires explicit GPU layers, context size, etc.

---

## Recommendation

**For the UX issue:** Switching to llama.cpp would provide **marginal improvement** for cancellation during streaming, but won't solve the root problem (prompt processing can't be interrupted in either system).

**Alternative UX solutions to consider:**

1. **Frontend cancel button** that closes the SSE connection (works with both backends)
2. **Smaller context/prompts** to reduce blocking time
3. **Timeout with retry** mechanism
4. **Queue management** in the backend to prevent request pileup

---

## Sources

- [Feature Request: Cancel during prompt processing](https://github.com/ggml-org/llama.cpp/issues/10509)
- [Simple way to stop server generating](https://github.com/ggml-org/llama.cpp/issues/4911)
- [llama.cpp Server Documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
- [Ollama vs llama.cpp Comparison 2025](https://blog.belsterns.com/post/ollama-vs-llama-cpp-which-one-should-you-choose-in-2025)
- [llama.cpp GitHub Repository](https://github.com/ggml-org/llama.cpp)

---

## Next Steps

Awaiting direction on whether to:
- Proceed with migration assessment (analyze current Ollama integration points)
- Focus on frontend UX improvements that work with both backends
