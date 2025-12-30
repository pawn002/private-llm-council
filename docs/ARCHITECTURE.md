# Architecture Overview

This document describes the technical architecture and design decisions behind The Private Council.

## System Overview

The Private Council is a local-first AI deliberation system that runs multiple language models to provide diverse perspectives on user questions.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     THE PRIVATE COUNCIL                              │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    PRIVACY BOUNDARY                          │    │
│  │                                                              │    │
│  │   ┌──────────┐     ┌──────────────┐                         │    │
│  │   │  React   │────▶│   FastAPI    │                         │    │
│  │   │ Frontend │◀────│   Backend    │                         │    │
│  │   └──────────┘     └──────┬───────┘                         │    │
│  │                           │                                  │    │
│  │              ┌────────────┴────────────┐                    │    │
│  │              │    Council Orchestrator │                    │    │
│  │              │    ┌─────────────────┐  │                    │    │
│  │              │    │ Dissent Tracker │  │                    │    │
│  │              │    └─────────────────┘  │                    │    │
│  │              └────────────┬────────────┘                    │    │
│  │                           │                                  │    │
│  │   ┌───────────────────────┼───────────────────────┐         │    │
│  │   │         Inference Gateway (Ollama/vLLM)       │         │    │
│  │   │  ┌─────────┐  ┌─────────┐  ┌─────────┐       │         │    │
│  │   │  │ Llama   │  │ Mistral │  │  Qwen   │       │         │    │
│  │   │  │  (φ)    │  │  (ψ)    │  │  (ω)    │       │         │    │
│  │   │  └─────────┘  └─────────┘  └─────────┘       │         │    │
│  │   │                    │                          │         │    │
│  │   │              ┌─────▼─────┐                    │         │    │
│  │   │              │ Chairman  │                    │         │    │
│  │   │              │   (Σ)     │                    │         │    │
│  │   │              └───────────┘                    │         │    │
│  │   └───────────────────────────────────────────────┘         │    │
│  │                                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  STORAGE (Encrypted, Ephemeral by Default)                   │    │
│  │  [Deliberations] [User Key Required] [Secure Delete]         │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### Frontend (React + TypeScript)

A single-page application providing:
- Question input interface
- Real-time deliberation streaming
- Individual perspective viewing
- Disagreement highlighting
- Save/export/forget controls

### Backend (FastAPI + Python)

RESTful API handling:
- Deliberation orchestration
- Privacy mode verification
- Encrypted persistence
- Model health monitoring

### Inference Gateway (Ollama/vLLM)

Local LLM serving layer:
- OpenAI-compatible API format
- Model lifecycle management
- GPU resource allocation

---

## Privacy Modes

The system offers three operational modes to accommodate different requirements:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRIVACY MODE SPECTRUM                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  SOVEREIGN          SANCTUARY           CITADEL                  │
│  (Air-Gapped)       (Local Network)     (Containerized)          │
│                                                                  │
│  Most Private       Balanced            Most Convenient          │
│                                                                  │
│  • No network       • Localhost only    • Docker networking      │
│  • Direct model     • Ollama/vLLM       • Full orchestration     │
│  • Manual setup       gateway           • Health checks          │
│  • Maximum trust    • No external       • Graceful degradation   │
│    in hardware        egress            • Easier deployment      │
│                     • Verified at                                │
│                       startup                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Sovereign Mode
- Native binary installation (no containers)
- Network interfaces disabled at OS level
- Models pre-downloaded to local storage
- For users requiring maximum isolation

### Sanctuary Mode (Default)
- Single-machine Docker with host networking
- Firewall rules blocking external egress
- Startup verification of network isolation
- Recommended for most users

### Citadel Mode
- Full Docker Compose stack
- Internal bridge network only
- Egress blocked via network policy
- For operational convenience

---

## Council Composition

Models are selected for both capability and diversity of perspective:

| Model | Capability | Perspective |
|-------|------------|-------------|
| Llama 3.2 (8B) | Strong general reasoning | Western analytical tradition |
| Mistral 7B | Excellent instruction following | European regulatory mindset |
| Qwen 2.5 (7B) | Diverse training corpus | Different cultural context |
| Llama 3.2 (70B) | Large context for synthesis | Chairman - synthesizer |

The goal is to provide genuinely different viewpoints, not variations of the same perspective.

---

## Deliberation Process

### Stage 1: Collect Perspectives
Each council member independently considers the question. Models run in parallel when hardware allows, or sequentially on constrained systems.

### Stage 2: Peer Review
Each model reviews and critiques other responses. Model identities are anonymized during review to prevent favoritism.

### Stage 3: Synthesis
The chairman model synthesizes all perspectives and critiques into a final response, while:
- Preserving areas of disagreement
- Highlighting minority reports
- Indicating confidence levels

---

## Transparency Features

The system surfaces the full deliberation process:

- **Individual Responses**: See what each council member said
- **Disagreement Detection**: Fundamental conflicts are highlighted
- **Minority Reports**: Dissenting views are preserved
- **Confidence Levels**: Distinguish consensus from judgment calls

Users observe a multi-perspective deliberation, not just a single answer.

---

## Persistence Model

### Default: Ephemeral
- Deliberations exist only in memory
- Deleted when session closes
- No automatic persistence

### Explicit Save
- User must consciously choose to save
- Encryption required (AES-256-GCM)
- Keys controlled by user

### Secure Deletion
- Multiple overwrite passes
- Cryptographic verification
- No "soft delete" - data is gone

---

## Degradation Policy

When resources are constrained, the system degrades gracefully with transparency:

```python
on_model_unavailable:
  action: "prompt_user"
  message: "Council member unavailable. Continue with reduced council?"

on_chairman_unavailable:
  fallback_to_largest_available: true
  message: "Chairman unavailable. Use {fallback_model} for synthesis?"

minimum_council_size: 2
warn_below_size: 3
```

The user always knows when they're receiving less than the full council.

---

## Configuration Schema

Configuration is stored in `config/sovereign_council.yaml`:

```yaml
# Privacy mode: sovereign | sanctuary | citadel
privacy:
  mode: "sanctuary"

# Inference gateway settings
gateway:
  provider: "ollama"
  url: "http://localhost:11434/v1"
  timeout_seconds: 120

# Council composition
council:
  members:
    - id: "phi"
      model: "llama3.2:8b"
    - id: "psi"
      model: "mistral:7b"
    - id: "omega"
      model: "qwen2.5:7b"
  chairman:
    model: "llama3.2:70b"
    preserve_dissent: true

# Deliberation settings
deliberation:
  stages:
    collect:
      parallel: true
    review:
      anonymize_models: true
    synthesize:
      preserve_dissent: true
      include_minority_reports: true

# Persistence defaults
persistence:
  default: "ephemeral"
  save:
    encryption: "required"
```

See the full configuration file for all available options.

---

## Deployment Options

### Docker Compose (Recommended)

```bash
cp .env.example .env
docker compose up -d
```

Services:
- **ollama**: Inference gateway with GPU passthrough
- **backend**: FastAPI application
- **frontend**: React UI served by nginx

### Manual Installation

```bash
# Start Ollama
ollama serve

# Pull models
ollama pull llama3.2:8b mistral:7b qwen2.5:7b

# Start backend
cd backend && pip install -e . && python -m src.main

# Start frontend
cd frontend && npm install && npm run dev
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | React, TypeScript, Vite | User interface |
| Backend | FastAPI, Python 3.10+ | API and orchestration |
| Inference | Ollama (default), vLLM | Local LLM serving |
| Encryption | AES-256-GCM | Deliberation storage |
| Container | Docker, Docker Compose | Deployment |

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Default privacy mode | Sanctuary | Balance between security and usability |
| Minimum council size | 2 | Allow operation on limited hardware |
| Chairman fallback | Allowed | Support users with modest hardware |
| Encryption for saves | Required | If worth saving, worth encrypting |
| Telemetry | None | Privacy is architectural, not optional |

---

## Future Considerations

- Support for additional inference backends (llama.cpp, Hugging Face TGI)
- Model hot-swapping without restart
- Multi-user deployment with isolated sessions
- Plugin system for custom analysis modules
