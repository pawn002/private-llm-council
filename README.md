# The Sovereign Council

> Your deliberations belong to you.

A privacy-first local LLM council for deliberative AI assistance. Inspired by [Karpathy's llm-council](https://github.com/karpathy/llm-council), rebuilt from the ground up with privacy as the architectural foundation.

## What Is This?

A council of locally-hosted language models that deliberate on your questions:

1. **Multiple perspectives** - Each council member provides their independent view
2. **Peer review** - Models critique each other's responses (anonymized to prevent bias)
3. **Synthesis with dissent** - A chairman model synthesizes the discussion while preserving disagreement

All of this happens **entirely on your machine**. No queries leave your hardware. No responses are logged externally. No telemetry phones home.

## Why?

When you ask difficult questions—about relationships, career decisions, health concerns, ethical dilemmas—you engage in intellectual intimacy. That intimacy deserves a private space, not a public square.

Cloud AI services collapse this distinction. You type as if in private, but speak into infrastructure you don't control.

This project restores the distinction. See [MANIFESTO.md](MANIFESTO.md) for the full philosophy.

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

This implementation reflects specific value choices:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Default privacy mode | Sanctuary | Balance between security and usability |
| Minimum council size | 2 (warn below 3) | Allow operation on limited hardware |
| Chairman fallback | Allowed | Don't block users with modest hardware |
| Encryption for saves | Required | If worth saving, worth encrypting |
| Consent banner | Always shown, user-dismissable | Transparency is non-negotiable |

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
    │   ├── components/       # React components
    │   ├── hooks/            # Custom React hooks
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

## What This Is Not

- **Not a cost-saving measure** - Local inference often costs more than cloud
- **Not a performance optimization** - Local is usually slower
- **Not paranoid** - Believing your thoughts deserve privacy is dignity, not paranoia
- **Not a product** - No business model, no telemetry, no premium tier

## Contributing

Contributions welcome. Please read [MANIFESTO.md](MANIFESTO.md) first to understand the values this project embodies.

## License

MIT

## Acknowledgments

- [Andrej Karpathy](https://github.com/karpathy) for the original llm-council concept
- The open-source LLM community for making local inference possible
- Everyone who believes that some spaces should remain private
