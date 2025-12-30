# The Private Council

> The only LLM council that preserves and highlights minority opinions, with tiered privacy modes and ephemeral-by-default operation.

A local LLM deliberation system built on [Karpathy's llm-council](https://github.com/karpathy/llm-council) concept. While other local implementations exist (see [Prior Art](docs/PRIOR_ART.md)), this project focuses on what others don't: **preserving dissent, not just reaching consensus**.

## What Makes This Different?

Most multi-model systems optimize for agreement. We optimize for **visibility into disagreement**:

1. **Minority reports preserved** - When a model is outvoted, its dissent remains visible, not discarded
2. **Disagreement highlighting** - The UI surfaces where models fundamentally disagree, not just the synthesis
3. **Tiered privacy modes** - Choose your level: Sovereign (air-gapped), Sanctuary (local network), or Citadel (containerized)
4. **Ephemeral by default** - Deliberations vanish when you close the session; saving requires explicit action and encryption

Everything runs **entirely on your machine**. No queries leave your hardware. No telemetry.

## Why Local?

When you work through difficult questions—about relationships, career decisions, health concerns, ethical dilemmas—you're engaging in personal reflection. Some people prefer that reflection to happen in a space they fully control.

Cloud AI services are convenient and powerful. For many use cases, they work well. This project offers an alternative for those who want complete local control.

See [MANIFESTO.md](MANIFESTO.md) for the full philosophy.

## Privacy Modes

| Mode | Description |
|------|-------------|
| **Sovereign** | Air-gapped. No network activity whatsoever. |
| **Sanctuary** (default) | Local network only. Verified isolation from internet. |
| **Citadel** | Containerized with network policies. Easier deployment. |

## Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) running locally
- 16GB+ RAM (32GB+ recommended)
- GPU with 8GB+ VRAM (24GB+ recommended)

### Install Models

```bash
# Pull council member models
ollama pull llama3.2:8b
ollama pull mistral:7b
ollama pull qwen2.5:7b

# Pull chairman model (requires more VRAM)
ollama pull llama3.2:70b
# Or use a smaller chairman if hardware-constrained:
ollama pull llama3.2:8b
```

### Docker (Recommended)

```bash
# Copy environment configuration
cp .env.example .env

# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

The UI will be available at `http://localhost:3000`.

### Manual Installation

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the server
python -m src.main
```

The API will be available at `http://localhost:8000`.

For the frontend:

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:3000`.

### Test It

```bash
curl -X POST http://localhost:8000/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the trade-offs between pursuing a stable career versus taking entrepreneurial risks?"}'
```

## Configuration

Edit `config/sovereign_council.yaml` to customize:

- Privacy mode
- Council member models
- Chairman model
- Degradation policies
- Persistence settings

See the file for detailed documentation of each setting.

## Key Decisions

This implementation reflects specific choices:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Default privacy mode | Sanctuary | Balance between security and usability |
| Minimum council size | 2 (warn below 3) | Allow operation on limited hardware |
| Chairman fallback | Allowed | Support users with modest hardware |
| Encryption for saves | Required | If worth saving, worth encrypting |
| Consent banner | Always shown, user-dismissable | Transparency matters |

## Documentation

| Document | Description |
|----------|-------------|
| [MANIFESTO.md](MANIFESTO.md) | Project philosophy and values |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Technical architecture and design decisions |
| [docs/HARDWARE_REQUIREMENTS.md](docs/HARDWARE_REQUIREMENTS.md) | Hardware sizing guide |
| [docs/PRIOR_ART.md](docs/PRIOR_ART.md) | Related projects and how we differ |

## Project Structure

```
private-llm-council/
├── MANIFESTO.md              # Why this project exists
├── README.md                 # You are here
├── docker-compose.yml        # Production deployment
├── docker-compose.dev.yml    # Development override
├── .env.example              # Environment configuration template
├── config/
│   └── sovereign_council.yaml  # Configuration (values declaration)
├── docs/
│   ├── ARCHITECTURE.md       # Technical architecture
│   └── HARDWARE_REQUIREMENTS.md  # Hardware guide
├── backend/
│   ├── Dockerfile            # Backend container
│   ├── pyproject.toml        # Python dependencies
│   ├── src/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Configuration loader
│   │   ├── privacy.py        # Privacy mode verification
│   │   ├── gateway.py        # Inference gateway client
│   │   ├── council.py        # Deliberation orchestration
│   │   ├── analysis.py       # LLM-powered disagreement analysis
│   │   └── persistence.py    # Encrypted storage
│   └── tests/                # Test suite
└── frontend/
    ├── Dockerfile            # Frontend container
    ├── nginx.conf            # Production web server config
    ├── src/
    │   ├── components/       # Angular components
    │   ├── services/         # Angular services
    │   ├── api/              # API client
    │   └── types/            # TypeScript definitions
    └── ...
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health and privacy status |
| `/privacy/status` | GET | Current privacy verification |
| `/privacy/consent-banner` | GET | Get consent banner text |
| `/deliberate` | POST | Submit question for deliberation |
| `/deliberate/stream` | GET | SSE streaming deliberation |
| `/models` | GET | List available models |
| `/deliberations/save` | POST | Encrypt and save deliberation |
| `/deliberations/load` | POST | Decrypt and load deliberation |
| `/deliberations/forget` | POST | Securely delete deliberation |
| `/deliberations` | GET | List saved deliberation IDs |
| `/deliberations/{id}/exists` | GET | Check if deliberation exists |

## Hardware Requirements

| Profile | RAM | VRAM | Notes |
|---------|-----|------|-------|
| Minimum | 16GB | 8GB | 7B models only, sequential inference |
| Recommended | 32GB | 24GB | Multiple 7B + quantized 70B chairman |
| Optimal | 64GB | 48GB | Full parallel inference, 70B at full precision |

For detailed hardware guidance including GPU comparisons, Apple Silicon support, and optimization tips, see [docs/HARDWARE_REQUIREMENTS.md](docs/HARDWARE_REQUIREMENTS.md).

## What This Is Not

- **Not a cost-saving measure** - Local inference often costs more than cloud
- **Not a performance optimization** - Local is usually slower
- **Not a criticism of cloud services** - They have legitimate uses; we offer an alternative
- **Not a product** - No business model, no telemetry, no premium tier

## Contributing

Contributions welcome. Please read [MANIFESTO.md](MANIFESTO.md) first to understand the values this project embodies.

## License

MIT

## Acknowledgments

- [Andrej Karpathy](https://github.com/karpathy) for the original llm-council concept
- [mchzimm/llm-council-local-improved](https://github.com/mchzimm/llm-council-local-improved) for pioneering local privacy-focused implementation
- [Open WebUI](https://github.com/open-webui/open-webui) for advancing local LLM interfaces
- The open-source LLM community for making local inference possible
