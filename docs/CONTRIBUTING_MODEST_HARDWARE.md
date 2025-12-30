# Contributing with Modest Hardware

> You don't need a gaming PC to contribute meaningfully to this project.

This guide is for contributors with modest hardware: laptops with integrated graphics, older machines, or systems with 16GB RAM and no dedicated GPU. While running the full deliberation system with large models is resource-intensive, there are many valuable ways to contribute that don't require high-end hardware.

## Philosophy

**Contribution is not a hardware benchmark.** The Private Council project values:
- Documentation improvements
- Configuration design
- Frontend development
- Testing infrastructure
- Community building

All of these can be done on a laptop from 2015.

---

## Quick Reference: What You Can Do

| Activity | Hardware Required | Time to Start |
|----------|-------------------|---------------|
| Documentation | Any | < 5 minutes |
| Frontend development | 8GB RAM | 10 minutes |
| Configuration design | Any | 5 minutes |
| Unit tests (no models) | 8GB RAM | 10 minutes |
| Light model testing | 16GB RAM, integrated GPU | 30 minutes |
| Full system testing | 16GB RAM + 8GB VRAM | 1 hour |

---

## Getting Started Without Running Models

### 1. Documentation Contributions

**Hardware needed**: Any computer that can run a text editor

**How to start**:

```bash
# Clone the repository
git clone https://github.com/yourusername/private-llm-council.git
cd private-llm-council

# Create a branch
git checkout -b docs/improve-hardware-guide

# Edit markdown files
# No build process required!
```

**What to contribute**:
- Fix typos and improve clarity
- Add examples for different use cases
- Document edge cases you discover
- Improve installation instructions
- Add troubleshooting tips
- Write tutorial content

**Example PRs welcome**:
- "Add Windows-specific installation notes"
- "Document common Ollama connection issues"
- "Add privacy mode comparison table"
- "Improve hardware requirements clarity"

---

### 2. Configuration Design

**Hardware needed**: Any computer that can edit YAML

**How to start**:

```bash
# No installation required - just edit config files
cd config/

# Copy the base configuration
cp sovereign_council.yaml sovereign_council_modest.yaml

# Design your configuration
# Test syntax with yamllint (optional)
```

**What to contribute**:
- Design council compositions for specific domains (legal, medical, creative)
- Create configuration presets for different hardware tiers
- Propose new privacy mode settings
- Design degradation policies
- Document configuration patterns

**Example configurations to create**:
```yaml
# config/presets/creative_writing_council.yaml
council:
  members:
    - id: "storyteller"
      model: "llama3.2:8b"
      character: "Narrative focus, plot structure"
    - id: "poet"
      model: "qwen2.5:7b"
      character: "Language beauty, metaphor"
    - id: "editor"
      model: "mistral:7b"
      character: "Grammar, clarity, conciseness"
```

---

### 3. Frontend Development (Angular UI)

**Hardware needed**: 8GB+ RAM, no GPU required

**How to start**:

```bash
cd frontend

# Install dependencies
npm install

# Run in development mode WITHOUT backend
npm run dev

# The UI will use mock data - no models required!
```

**How to use mock data**:

Create a mock API service:

```typescript
// src/app/services/mock-deliberation.service.ts
export class MockDeliberationService {
  getMockDeliberation() {
    return {
      question: "What are the privacy implications of local AI?",
      perspectives: [
        {
          model: "phi",
          response: "Local AI ensures data never leaves your machine...",
          confidence: 0.85
        },
        // ... more perspectives
      ],
      synthesis: "The council finds consensus that...",
      disagreements: [/* ... */]
    };
  }
}
```

**What to contribute**:
- UI/UX improvements
- Disagreement visualization enhancements
- Accessibility improvements
- Mobile responsiveness
- Dark mode refinements
- Loading state animations
- Error handling UI

**Testing without backend**:

```bash
# Use Angular testing utilities
npm run test

# Run e2e tests with mock data
npm run e2e
```

---

### 4. Backend Development (Python FastAPI)

**Hardware needed**: 8GB+ RAM, no GPU required

**How to start**:

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run unit tests (no models required)
pytest tests/ -v
```

**What to contribute**:
- Unit tests for existing functions
- Code refactoring
- Error handling improvements
- API endpoint documentation
- Type hints and validation
- Performance optimizations

**Testing without models**:

Mock the inference gateway:

```python
# tests/test_council.py
from unittest.mock import Mock

def test_council_deliberation():
    mock_gateway = Mock()
    mock_gateway.generate.return_value = "Mock response"

    council = CouncilOrchestrator(gateway=mock_gateway)
    result = council.deliberate("Test question")

    assert result is not None
```

---

## Running Light Models (16GB RAM + Integrated GPU)

If you want to test the actual deliberation system with modest hardware:

### Choose Your Speed/Quality Balance

**Option A: Fast Mode (2-5 minutes)** - New! ⚡
- Ultra-lightweight models (0.5-1B)
- Perfect for time-constrained exploration
- Good for learning, testing, brainstorming

**Option B: Standard Mode (5-15 minutes)**
- Light models (1-3B)
- Better quality, slower inference
- Suitable for more thoughtful deliberation

### Step 1: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

**For Fast Mode (2-5 min deliberations)**:
```bash
# Pull ultra-lightweight models
ollama pull qwen2.5:0.5b   # ~600MB - smallest viable
ollama pull llama3.2:1b    # ~1GB
ollama pull tinyllama:1.1b # ~600MB - alternative
```

**For Standard Mode (5-15 min deliberations)**:
```bash
# Pull light models
ollama pull llama3.2:1b    # ~1GB
ollama pull qwen2.5:3b     # ~2GB
```

### Step 2: Choose Your Configuration

**Option A: Use Pre-built Fast Mode Config** (Recommended for beginners):
```bash
# No config editing needed!
CONFIG_PATH=config/sovereign_council_fast.yaml python -m src.main
```

**Option B: Use Pre-built Standard Modest Config**:
```bash
CONFIG_PATH=config/sovereign_council_modest.yaml python -m src.main
```

**Option C: Create Custom Config**:

Create `config/sovereign_council_custom.yaml`:

```yaml
council:
  members:
    # Minimal 2-member council
    - id: "phi"
      model: "llama3.2:1b"
      temperature: 0.7
    - id: "psi"
      model: "qwen2.5:3b"
      temperature: 0.7

  chairman:
    model: "llama3.2:3b"
    temperature: 0.3
    preserve_dissent: true

deliberation:
  stages:
    collect:
      parallel: false  # Sequential to reduce memory pressure
      timeout_per_model_seconds: 120  # Longer timeout for slower inference

gateway:
  warmup:
    enabled: false  # Skip warmup to save memory
```

### Step 3: Force CPU Inference (Often Faster on Integrated GPUs)

```bash
# Set environment variable
export OLLAMA_NUM_GPU=0

# Start Ollama
ollama serve &

# Run backend with modest config
cd backend
CONFIG_PATH=../config/sovereign_council_modest.yaml python -m src.main
```

### Step 4: Verify It Works

```bash
# Test with a simple question
curl -X POST http://localhost:8000/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the benefit of local AI?"}'
```

**Performance expectations**:

| Mode | Deliberation Time | Memory | When to Use |
|------|-------------------|---------|-------------|
| **Fast** | 2-5 minutes | 4-6GB | Quick tests, learning, time-limited |
| **Standard** | 5-15 minutes | 8-12GB | Better quality, more nuanced |

**System behavior (both modes)**:
- **CPU usage**: 80-100% during inference (normal)
- **Temperature**: Laptop will get warm (use cooling pad)
- **Progress**: Watch logs to see which model is currently responding

---

## Contribution Workflows

### Workflow 1: Documentation Only

```bash
# Fork and clone
git clone https://github.com/yourusername/private-llm-council.git
cd private-llm-council

# Create branch
git checkout -b docs/add-troubleshooting-guide

# Edit documentation
vim docs/TROUBLESHOOTING.md

# Commit and push
git add docs/TROUBLESHOOTING.md
git commit -m "Add troubleshooting guide for connection issues"
git push origin docs/add-troubleshooting-guide

# Open PR on GitHub
```

**No builds, no tests, no models required.**

---

### Workflow 2: Frontend Development with Mock Data

```bash
# Setup
cd frontend
npm install

# Create mock service
cat > src/app/services/mock-api.service.ts << 'EOF'
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class MockApiService {
  deliberate(question: string): Observable<any> {
    return of({
      perspectives: [
        { model: 'phi', response: 'Mock response 1' },
        { model: 'psi', response: 'Mock response 2' }
      ],
      synthesis: 'Mock synthesis'
    });
  }
}
EOF

# Run dev server
npm run dev

# Work on UI improvements
# No backend or models needed!
```

---

### Workflow 3: Backend Unit Tests

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Write tests
cat > tests/test_analysis.py << 'EOF'
from src.analysis import detect_disagreements

def test_disagreement_detection():
    perspectives = [
        {"response": "AI should be open source"},
        {"response": "AI should be proprietary"}
    ]
    disagreements = detect_disagreements(perspectives)
    assert len(disagreements) > 0
EOF

# Run tests
pytest tests/test_analysis.py -v

# No models required!
```

---

### Workflow 4: Light Model Testing

**Fast Mode** (2-5 minutes - recommended for rapid iteration):
```bash
# Pull ultra-lightweight models
ollama pull qwen2.5:0.5b
ollama pull llama3.2:1b
ollama pull tinyllama:1.1b

# Force CPU mode
export OLLAMA_NUM_GPU=0
ollama serve &

# Test with fast config
cd backend
CONFIG_PATH=../config/sovereign_council_fast.yaml python -m src.main

# Run a test deliberation (will take 2-5 minutes)
curl -X POST http://localhost:8000/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

**Standard Mode** (5-15 minutes - better quality):
```bash
# Pull light models
ollama pull llama3.2:1b
ollama pull qwen2.5:3b

# Force CPU mode
export OLLAMA_NUM_GPU=0
ollama serve &

# Test configuration changes
cd backend
CONFIG_PATH=../config/sovereign_council_modest.yaml python -m src.main

# Run a test deliberation (will take 5-15 minutes)
curl -X POST http://localhost:8000/deliberate \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

---

## Testing Strategies for Modest Hardware

### Strategy 1: Unit Tests Only

Focus on logic that doesn't require models:

```python
# Test configuration loading
def test_config_loading():
    config = load_config("config/sovereign_council.yaml")
    assert config["privacy"]["mode"] in ["sovereign", "sanctuary", "citadel"]

# Test analysis functions
def test_disagreement_scoring():
    score = calculate_disagreement_score(response1, response2)
    assert 0 <= score <= 1

# Test persistence
def test_encryption_roundtrip():
    data = {"test": "data"}
    encrypted = encrypt(data, key)
    decrypted = decrypt(encrypted, key)
    assert data == decrypted
```

### Strategy 2: Mocked Integration Tests

Test the full flow without real models:

```python
from unittest.mock import Mock

def test_full_deliberation_flow():
    # Mock the gateway
    mock_gateway = Mock()
    mock_gateway.generate.side_effect = [
        "Response from phi",
        "Response from psi",
        "Chairman synthesis"
    ]

    # Test the flow
    council = CouncilOrchestrator(gateway=mock_gateway)
    result = council.deliberate("Test question")

    # Verify structure
    assert "perspectives" in result
    assert "synthesis" in result
    assert len(result["perspectives"]) == 2
```

### Strategy 3: Occasional Full Tests

Use cloud GPU for occasional testing:

```bash
# Rent a cloud GPU for 2 hours (~$0.40)
# Test your changes with full models
# Then switch back to local development

# Example: Vast.ai workflow
ssh into vast.ai instance
git clone your-fork
./run_full_tests.sh
# Verify everything works
exit
# Continue local development
```

---

## Hardware-Specific Tips

### For Apple Silicon (M1/M2/M3)

Unified memory makes smaller models viable:

```bash
# M1/M2 with 16GB can run 3B models comfortably
ollama pull llama3.2:3b
ollama pull qwen2.5:3b

# Metal acceleration works well
# No OLLAMA_NUM_GPU needed
ollama serve
```

**Performance**: ~2-3 minutes per perspective on M2

---

### For Intel/AMD Integrated Graphics

CPU mode is often faster than iGPU:

```bash
# Force CPU inference
export OLLAMA_NUM_GPU=0

# Use 1-3B models
ollama pull llama3.2:1b
ollama pull qwen2.5:3b

ollama serve
```

**Performance**: ~3-5 minutes per perspective on modern i5/i7

---

### For Older Hardware (8GB RAM)

Focus on contributions that don't require running the full system:

1. **Documentation** - no limits
2. **Configuration design** - edit YAML files
3. **Frontend work** - use mock data
4. **Code review** - read and suggest improvements
5. **Issue triage** - help others troubleshoot

---

## Common Questions

### "Can I contribute if I can't run the system at all?"

**Yes!** Documentation, configuration design, and frontend work are all valuable contributions that don't require running models.

### "My deliberations take 15 minutes. Is something wrong?"

**No.** With ultra-light models on CPU, 10-15 minute deliberations are expected. This is acceptable for testing configuration changes or developing features.

### "Should I buy better hardware to contribute?"

**No.** Contribute what you can with what you have. If you enjoy the project and want better hardware, that's your choice - but it's not required for meaningful contribution.

### "Can I use cloud APIs for testing?"

**This project is about local inference.** For testing, you can:
- Use ultra-light local models (slower but works)
- Mock the inference gateway in tests
- Rent cloud GPU occasionally (~$0.20/hour) for full model testing

Avoid using cloud API services (OpenAI, Anthropic, etc.) as that defeats the privacy purpose.

---

## Example Contribution Paths

### Path 1: Documentation Specialist

**No hardware requirements**

1. Week 1: Fix typos, improve clarity
2. Week 2: Add troubleshooting guide
3. Week 3: Write hardware comparison guide
4. Week 4: Create video tutorial script

**Impact**: Help dozens of users get started successfully

---

### Path 2: Frontend Developer

**Requires: 8GB RAM**

1. Week 1: Fix UI bugs, improve mobile responsiveness
2. Week 2: Add new visualization for disagreements
3. Week 3: Implement dark mode improvements
4. Week 4: Add accessibility features

**Impact**: Improve experience for all users

---

### Path 3: Configuration Designer

**No hardware requirements**

1. Week 1: Design council composition for legal questions
2. Week 2: Create privacy mode presets
3. Week 3: Write degradation policies for edge cases
4. Week 4: Document configuration patterns

**Impact**: Make the system usable for new domains

---

### Path 4: Testing Infrastructure

**Requires: 8GB RAM**

1. Week 1: Write unit tests for untested modules
2. Week 2: Add integration tests with mocks
3. Week 3: Create CI/CD pipeline improvements
4. Week 4: Document testing best practices

**Impact**: Improve code quality and maintainability

---

## Getting Help

**Stuck on setup?**
- Check [HARDWARE_REQUIREMENTS.md](HARDWARE_REQUIREMENTS.md)
- Ask in GitHub Discussions
- Open an issue with your hardware specs

**Want to contribute but not sure how?**
- Look for `good-first-issue` labels
- Ask in discussions: "I have X hardware, how can I help?"
- Review open issues and comment on ones you find interesting

**Have ideas but no hardware?**
- Open an issue describing your idea
- Others with hardware can test and implement

---

## Final Thoughts

**The best contribution is the one you actually make.** A documentation fix on a 2015 MacBook Air is more valuable than a planned feature that never ships because you're waiting to buy a new GPU.

Start with what you can do today. The project benefits from diverse contributions, not just from those with high-end hardware.

Welcome aboard. 🚀
