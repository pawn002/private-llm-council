# Plan C: The Sovereign Council - Unified Implementation

## Preface: Merging the Pragmatic and the Principled

This plan synthesizes the DevOps pragmatism of Plan A with the philosophical rigor of Plan B. Where they align, we proceed. Where they conflict, we make explicit choices and document the trade-offs.

The result: a system that is both *deployable by a grizzled engineer on a Friday afternoon* and *defensible to a philosopher asking "but why?"*

---

## Incompatibilities Identified and Resolved

Before presenting the unified plan, we must be honest about where Plans A and B conflict:

### ⚠️ CONFLICT 1: Network Stance (MAJOR)

| Plan A | Plan B | Tension |
|--------|--------|---------|
| Docker Compose with container networking | Air-gapped, refuse if network detected | Container networking *is* networking |

**Resolution: Tiered Privacy Modes**

We introduce three operational modes, letting users choose their position on the pragmatism-principle spectrum:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRIVACY MODE SPECTRUM                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SOVEREIGN          SANCTUARY           CITADEL                 │
│  (Air-Gapped)       (Local Network)     (Containerized)         │
│                                                                 │
│  ████████████       ░░░░████████        ░░░░░░░░████            │
│  Most Private       Balanced            Most Convenient         │
│                                                                 │
│  • No network       • Localhost only    • Docker networking     │
│  • Direct model     • Ollama/vLLM       • Full orchestration    │
│  • Manual setup       gateway           • Health checks         │
│  • Maximum trust    • No external       • Graceful degradation  │
│    in hardware        egress            • Easier deployment     │
│                     • Verified at                               │
│                       startup                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Recommendation**: Default to SANCTUARY mode. Users requiring SOVEREIGN mode can disable networking at the OS level. CITADEL mode for teams prioritizing operational convenience.

---

### ⚠️ CONFLICT 2: Default Persistence (MODERATE)

| Plan A | Plan B |
|--------|--------|
| `persist_conversations: true` | `default: "ephemeral"` |

**Resolution: Privacy-Respecting Default with Operator Override**

```yaml
persistence:
  # User-facing default: ephemeral (Plan B wins philosophically)
  user_default: "ephemeral"

  # Operator can override for specific deployments (Plan A pragmatism)
  operator_override: null  # Set to "persistent" for enterprise deployments

  # But never silent persistence - always inform the user
  require_consent_banner: true
```

The philosophical principle (impermanence by default) takes precedence for end users. Operators deploying for teams can override, but must display a consent banner.

---

### ⚠️ CONFLICT 3: Graceful Degradation vs. Principled Operation (MODERATE)

| Plan A | Plan B |
|--------|--------|
| Fall back to smaller models, continue with fewer council members | Implicit: no compromise on principles |

**Resolution: Degradation with Transparency**

We allow graceful degradation (pragmatic) but with full transparency (principled):

```python
class DegradationPolicy:
    """
    When resources are constrained, we may operate in reduced mode.
    But we never pretend to be operating at full capacity.
    """

    def handle_missing_model(self, model_id: str) -> Decision:
        # Don't silently substitute
        # Don't fail completely
        # Do: inform and ask
        return Decision(
            action="prompt_user",
            message=f"Council member '{model_id}' unavailable. "
                    f"Continue with reduced council? "
                    f"(Epistemic diversity will be diminished)",
            options=["continue_reduced", "wait_for_model", "abort"]
        )
```

The user always knows when they're getting less than the full council.

---

### ⚠️ CONFLICT 4: Docker Networking vs. Air-Gap Philosophy

| Plan A | Plan B |
|--------|--------|
| Docker Compose stack | "NO NETWORK ACCESS" |

**Resolution: Mode-Specific Deployment**

```
SOVEREIGN MODE:
  └── Native installation (no containers)
  └── Direct llama.cpp / Ollama binary
  └── Network interfaces disabled at OS level
  └── Models pre-downloaded to local storage

SANCTUARY MODE:
  └── Single-machine Docker with host networking
  └── Firewall rules blocking external egress
  └── Startup verification of network isolation
  └── Models in local volume

CITADEL MODE:
  └── Full Docker Compose stack
  └── Internal bridge network only
  └── No port exposure except localhost
  └── Egress blocked via network policy
```

---

### ✓ COMPATIBLE: Model Selection (Merged)

Plans A and B both select similar models but for different reasons:

| Model | Plan A Rationale | Plan B Rationale | Unified |
|-------|------------------|------------------|---------|
| Llama 3.2 | Strong reasoning | Western tech tradition | ✓ Both |
| Mistral 7B | Good instruction following | European regulatory mindset | ✓ Both |
| Qwen 2.5 | Diverse training corpus | Different cultural priors | ✓ Both |

**Unified approach**: Select for *both* capability and epistemic diversity. Document both rationales.

---

### ✓ COMPATIBLE: Enhanced Interface (Additive)

Plan B's interface features (disagreement highlighting, minority reports) can be added to Plan A's infrastructure. No conflict—just additional work.

---

## The Unified Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     THE SOVEREIGN COUNCIL                           │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    PRIVACY BOUNDARY                          │   │
│  │   ┌─────────────────────────────────────────────────────┐   │   │
│  │   │                                                     │   │   │
│  │   │   ┌──────────┐     ┌──────────────┐                 │   │   │
│  │   │   │  React   │────▶│   FastAPI    │                 │   │   │
│  │   │   │ Frontend │◀────│   Backend    │                 │   │   │
│  │   │   └──────────┘     └──────┬───────┘                 │   │   │
│  │   │                           │                         │   │   │
│  │   │              ┌────────────┴────────────┐            │   │   │
│  │   │              │    Council Orchestrator │            │   │   │
│  │   │              │    ┌─────────────────┐  │            │   │   │
│  │   │              │    │ Dissent Tracker │  │            │   │   │
│  │   │              │    └─────────────────┘  │            │   │   │
│  │   │              └────────────┬────────────┘            │   │   │
│  │   │                           │                         │   │   │
│  │   │   ┌───────────────────────┼───────────────────────┐ │   │   │
│  │   │   │         Inference Gateway (Ollama/vLLM)       │ │   │   │
│  │   │   │  ┌─────────┐  ┌─────────┐  ┌─────────┐       │ │   │   │
│  │   │   │  │ Llama   │  │ Mistral │  │  Qwen   │       │ │   │   │
│  │   │   │  │  (φ)    │  │  (ψ)    │  │  (ω)    │       │ │   │   │
│  │   │   │  │ Western │  │ European│  │ Eastern │       │ │   │   │
│  │   │   │  └─────────┘  └─────────┘  └─────────┘       │ │   │   │
│  │   │   │                    │                          │ │   │   │
│  │   │   │              ┌─────▼─────┐                    │ │   │   │
│  │   │   │              │ Chairman  │                    │ │   │   │
│  │   │   │              │ (Σ) 70B   │                    │ │   │   │
│  │   │   │              └───────────┘                    │ │   │   │
│  │   │   └───────────────────────────────────────────────┘ │   │   │
│  │   │                                                     │   │   │
│  │   └─────────────────────────────────────────────────────┘   │   │
│  │                                                             │   │
│  │   ████████████ EGRESS BLOCKED / VERIFIED █████████████     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  STORAGE (Encrypted, Ephemeral by Default)                  │   │
│  │  [Deliberations] [User Key Required] [Secure Delete]        │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Unified Configuration Schema

```yaml
# config/sovereign_council.yaml
# A configuration that serves both the pragmatist and the philosopher.

#═══════════════════════════════════════════════════════════════════════
# IDENTITY & VALUES
# Why this project exists (Plan B contribution)
#═══════════════════════════════════════════════════════════════════════
identity:
  name: "The Sovereign Council"
  principle: |
    Your deliberations belong to you.
    This system exists to keep them that way.
  version: "1.0.0"

#═══════════════════════════════════════════════════════════════════════
# PRIVACY MODE
# Choose your position on the pragmatism-principle spectrum
#═══════════════════════════════════════════════════════════════════════
privacy:
  # Options: sovereign | sanctuary | citadel
  mode: "sanctuary"

  sovereign:
    # For the uncompromising
    description: "Air-gapped operation. No network activity whatsoever."
    network_check: "fail_if_any_interface_up"
    deployment: "native_binary"

  sanctuary:
    # The recommended balance
    description: "Local network only. Verified isolation from internet."
    network_check: "fail_if_external_egress_possible"
    deployment: "docker_host_network"
    allowed_connections:
      - "localhost"
      - "127.0.0.1"
      - "host.docker.internal"

  citadel:
    # For operational convenience
    description: "Containerized with network policies. Easier deployment."
    network_check: "warn_if_egress_possible"
    deployment: "docker_compose"

#═══════════════════════════════════════════════════════════════════════
# INFERENCE GATEWAY
# The plumbing (Plan A contribution)
#═══════════════════════════════════════════════════════════════════════
gateway:
  # Provider: ollama | vllm | llamacpp
  provider: "ollama"
  url: "http://localhost:11434/v1"
  timeout_seconds: 120
  retry_attempts: 3

  health_check:
    enabled: true
    interval_seconds: 30

  warmup:
    # First inference is slow; warm up on startup
    enabled: true
    prompt: "Hello"

#═══════════════════════════════════════════════════════════════════════
# COUNCIL COMPOSITION
# Both capability AND epistemic diversity (Merged)
#═══════════════════════════════════════════════════════════════════════
council:
  members:
    - id: "phi"
      model: "llama3.2:8b"
      # Plan A: capability rationale
      capability: "Strong general reasoning and instruction following"
      # Plan B: epistemic rationale
      character: "Western analytical tradition, Silicon Valley optimism"
      temperature: 0.7

    - id: "psi"
      model: "mistral:7b"
      capability: "Excellent instruction following, structured outputs"
      character: "European regulatory mindset, GDPR-informed caution"
      temperature: 0.7

    - id: "omega"
      model: "qwen2.5:7b"
      capability: "Diverse training corpus, multilingual strength"
      character: "Eastern philosophical traditions, different cultural priors"
      temperature: 0.7

  chairman:
    model: "llama3.2:70b"
    capability: "Large context window for synthesis"
    role: "Synthesizer and dissent-preserver, not arbiter of truth"
    temperature: 0.3
    preserve_dissent: true

#═══════════════════════════════════════════════════════════════════════
# DELIBERATION PROCESS
# How the council operates (Plan B contribution)
#═══════════════════════════════════════════════════════════════════════
deliberation:
  stages:
    collect:
      parallel: true
      timeout_per_model: 60

    review:
      anonymize_models: true  # Prevent favoritism
      require_rankings: true

    synthesize:
      preserve_dissent: true
      include_minority_reports: true

  # Transparency features (Plan B)
  transparency:
    show_individual_responses: true
    show_peer_reviews: true
    highlight_disagreements: true
    show_confidence_levels: true
    include_minority_reports: true

#═══════════════════════════════════════════════════════════════════════
# DEGRADATION POLICY
# When things go wrong (Merged - pragmatic action, principled transparency)
#═══════════════════════════════════════════════════════════════════════
degradation:
  # Never silently degrade - always inform user
  silent_fallback: false

  on_model_unavailable:
    action: "prompt_user"  # Options: prompt_user | auto_skip | fail
    message: "Council member unavailable. Continue with reduced epistemic diversity?"

  on_chairman_unavailable:
    action: "prompt_user"
    fallback_to_largest_available: true
    message: "Chairman unavailable. Use {fallback_model} for synthesis?"

  minimum_council_size: 2
  warn_below_size: 3

#═══════════════════════════════════════════════════════════════════════
# PERSISTENCE
# Ephemeral by default, explicit save required (Plan B wins)
#═══════════════════════════════════════════════════════════════════════
persistence:
  # User-facing default
  default: "ephemeral"

  # Operator override for enterprise deployments
  operator_can_override: true

  # Always show the banner - but users can dismiss for their session
  consent_banner:
    always_show_on_session_start: true  # Operators cannot disable this
    user_dismissable: true              # User can hide after acknowledging
    persist_dismissal: "session_only"   # Re-shown on next session
    text: "This deliberation will be forgotten when you close the session."

  # When saving is requested
  save:
    encryption: "required"  # Options: required | optional | none
    key_source: "user_provided"  # Options: user_provided | derived | system
    algorithm: "AES-256-GCM"

  # Secure deletion
  forget:
    secure_overwrite: true
    overwrite_passes: 3

#═══════════════════════════════════════════════════════════════════════
# TELEMETRY
# None. This is not negotiable. (Plan B)
#═══════════════════════════════════════════════════════════════════════
telemetry:
  enabled: false
  # This comment is the implementation:
  # We do not track you because your intellectual struggles
  # are not our training data, our metrics, or our business.

#═══════════════════════════════════════════════════════════════════════
# HARDWARE REQUIREMENTS
# What you need to run this (Plan A contribution)
#═══════════════════════════════════════════════════════════════════════
hardware:
  minimum:
    ram_gb: 16
    vram_gb: 8
    note: "Run 7B models sequentially, no 70B chairman"

  recommended:
    ram_gb: 32
    vram_gb: 24
    note: "Run multiple 7B models, 70B chairman quantized"

  optimal:
    ram_gb: 64
    vram_gb: 48
    note: "Full parallel inference, 70B chairman at full precision"
```

---

## Implementation Phases (Unified)

### Phase 1: Foundation (Week 1)
*Merges Plan A Phase 1 + Plan B Phase 1*

- [ ] Write MANIFESTO.md (why this exists)
- [ ] Define privacy mode spectrum (sovereign/sanctuary/citadel)
- [ ] Select inference gateway (Ollama recommended)
- [ ] Inventory target hardware
- [ ] Create unified configuration schema

### Phase 2: Core Infrastructure (Week 2)
*Plan A backbone with Plan B verification*

- [ ] Fork llm-council repository
- [ ] Replace OpenRouter client with local gateway client
- [ ] Implement privacy mode detection and enforcement
- [ ] Add network verification for sanctuary mode
- [ ] Create model identifier translation layer
- [ ] Implement health checks

### Phase 3: Council Logic Enhancement (Week 3)
*Plan B features on Plan A foundation*

- [ ] Implement dissent tracking in peer review stage
- [ ] Build disagreement detection algorithm
- [ ] Create minority report extraction
- [ ] Add transparency metadata to deliberation objects
- [ ] Implement degradation policy with user prompts

### Phase 4: Persistence & Security (Week 4)
*Plan B philosophy, Plan A implementation*

- [ ] Implement ephemeral-by-default storage
- [ ] Build user-controlled encryption for saves
- [ ] Create secure deletion (overwrite before dealloc)
- [ ] Add consent banner system
- [ ] Implement session isolation

### Phase 5: Interface Evolution (Week 5)
*Plan B UI on Plan A stack*

- [ ] Add disagreement highlighting to response view
- [ ] Implement minority report display
- [ ] Add confidence level visualization
- [ ] Create "this will be forgotten" banner
- [ ] Build [Save Encrypted] / [Forget Now] actions

### Phase 6: Deployment Modes (Week 6)
*Plan A Docker + Plan B verification*

- [ ] Create native binary deployment for SOVEREIGN mode
- [ ] Build Docker host-network config for SANCTUARY mode
- [ ] Create Docker Compose stack for CITADEL mode
- [ ] Implement startup verification for each mode
- [ ] Write deployment documentation for each mode

### Phase 7: Documentation & Polish
*Plan B philosophy in Plan A format*

- [ ] README as philosophical statement + practical guide
- [ ] Configuration reference with rationale comments
- [ ] Hardware sizing guide
- [ ] Troubleshooting guide
- [ ] Security model documentation

---

## The Unified Interface

```
┌──────────────────────────────────────────────────────────────────────┐
│  THE SOVEREIGN COUNCIL                          [SANCTUARY MODE] 🔒  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Your Question:                                                  │ │
│  │ "Should I leave my job to pursue this startup idea?"           │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  COUNCIL PERSPECTIVES                                                │
│                                                                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐        │
│  │ φ (Llama)       │ │ ψ (Mistral)     │ │ ω (Qwen)        │        │
│  │ Western/Analyt. │ │ European/Regul. │ │ Eastern/Diverse │        │
│  ├─────────────────┤ ├─────────────────┤ ├─────────────────┤        │
│  │ "The expected   │ │ "European labor │ │ "Consider the   │        │
│  │ value calc      │ │ protections     │ │ concept of      │        │
│  │ suggests the    │ │ you'd forfeit   │ │ 'right timing'  │        │
│  │ risk is worth   │ │ deserve weight  │ │ - perhaps the   │        │
│  │ taking if..."   │ │ in this..."     │ │ question is..." │        │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘        │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  ⚡ DISAGREEMENTS DETECTED                                           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ • φ and ψ disagree on risk tolerance framing                   │ │
│  │   φ: Risk as opportunity | ψ: Risk as exposure                 │ │
│  │                                                                 │ │
│  │ • ω introduces temporal dimension neither φ nor ψ addressed    │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  CHAIRMAN'S SYNTHESIS                                    [Σ Llama70B]│
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ The council reflects genuine uncertainty, which honors the     │ │
│  │ difficulty of your question.                                   │ │
│  │                                                                 │ │
│  │ CONSENSUS: All agree this decision warrants careful analysis   │ │
│  │ DIVISION: Risk framing (opportunity vs. exposure)              │ │
│  │ UNIQUE INSIGHT: ω's temporal framing deserves consideration    │ │
│  │                                                                 │ │
│  │ The majority leans toward caution, but...                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  📋 MINORITY REPORT (φ):                                             │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ "The council optimizes for risk minimization, but perhaps      │ │
│  │ the real question is: 'Will I regret not trying?' The          │ │
│  │ asymmetry of regret may outweigh the asymmetry of outcomes."   │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  ⏳ This deliberation will be forgotten when you close               │
│                                                                      │
│  [💾 Save Encrypted]  [📤 Export]  [🗑️ Forget Now]  [❓ Why Ephemeral?]│
└──────────────────────────────────────────────────────────────────────┘
```

---

## Trade-offs of the Unified Approach

| Aspect | Pure Plan A | Pure Plan B | Unified (Plan C) |
|--------|-------------|-------------|------------------|
| Setup Complexity | Medium | High | Medium-High (mode-dependent) |
| Philosophical Coherence | Low | High | High (values documented) |
| Operational Flexibility | High | Low | High (via modes) |
| User Agency | Medium | High | High (informed choices) |
| Implementation Effort | 14-27 hrs | 30-50 hrs | 40-60 hrs |
| Deployment Options | Docker only | Native only | Both |
| Default Privacy | Good | Excellent | Excellent (ephemeral default) |
| Graceful Degradation | Silent | None | Transparent |

---

## What We Kept, What We Changed

### From Plan A (The DevOps Pragmatism)
✓ Docker Compose deployment option (as CITADEL mode)
✓ Health checks and operational monitoring
✓ Graceful degradation (but made transparent)
✓ Hardware requirements documentation
✓ Configuration file approach
✗ Changed: Silent persistence → Ephemeral default
✗ Changed: Implicit privacy → Explicit privacy modes

### From Plan B (The Philosophical Rigor)
✓ Ephemeral by default
✓ Dissent preservation and minority reports
✓ Epistemic diversity as explicit goal
✓ Configuration as values declaration
✓ "Why" documentation alongside "how"
✗ Changed: Absolute air-gap → Privacy mode spectrum
✗ Changed: Refuse-if-network → Verify-and-warn (in sanctuary mode)

### New in Plan C
+ Privacy mode spectrum (sovereign/sanctuary/citadel)
+ Degradation with transparency (not silent, not fatal)
+ Dual rationale for model selection (capability + character)
+ Consent banner system for persistence
+ Mode-specific deployment documentation

---

## Decision Points - RESOLVED

The following decisions have been finalized:

| # | Decision | Resolution |
|---|----------|------------|
| 1 | **Default privacy mode** | ✅ SANCTUARY - balanced security and usability |
| 2 | **Minimum council size** | ✅ Minimum 2, with warning if fewer than 3 |
| 3 | **Chairman fallback** | ✅ Allow fallback to largest available model with user prompt |
| 4 | **Encryption requirement** | ✅ Required for all saves - no plaintext persistence |
| 5 | **Consent banner** | ✅ Always shown, but user can dismiss for their session |

### Banner Behavior Detail

The consent banner ("This deliberation will be forgotten when you close") is:
- **Always displayed** on session start - operators cannot disable
- **Dismissable by user** - once acknowledged, can be hidden for remainder of session
- **Re-shown** on each new session

This preserves transparency (Plan B value) while reducing friction for repeat users (Plan A pragmatism).

---

## Next Steps

1. ~~Review this unified plan~~ ✅
2. ~~Resolve the decision points above~~ ✅
3. Approve plan or request modifications
4. Begin Phase 1 implementation

---

*This plan attempts to honor both the engineer who asks "does it work?" and the philosopher who asks "should it exist?" The answer to both should be yes.*
