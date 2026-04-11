# Post-Mortem: Small Model Structured Output

**Features affected:** Points of Agreement / Unique Insights, Disagreement Analysis, Council Synthesis  
**Branch:** `task-19-candor-design-system`  
**Last updated:** 2026-04-11

---

## TL;DR — Rules for prompting sub-2B models

1. **One task per call.** Two structured sections in one prompt → unreliable. Two calls → works.
2. **Format at the top.** Instructions after context paragraphs get ignored. Lead with the output spec.
3. **Ground the model explicitly.** Add "only include ideas directly stated above — do not add, infer, or invent" or the model will hallucinate from training data.
4. **Inject concrete values.** Member names, counts, example outputs — never leave template placeholders the model could echo literally.
5. **Ban bad output patterns by name.** "Do not write `From [name]'s perspective`" works. "Write coherent prose" does not.
6. **Write defensive parsers.** Normalize headers, accept `•` and `-`, strip member-name affixes in all positions, handle NONE variants.
7. **Unit-test the parser before touching a model.** It's a pure function. <1s, no Ollama needed.
8. **Build a probe script for every new extraction call.** 30s to validate output format, not 12 minutes.
9. **Never swallow LLM exceptions silently.** `([], [])` and "crashed" look identical without explicit logging.
10. **Verify attribute names locally before rebuilding.** One `python -c` import check saves a container rebuild.

---

## What we were building

Three extraction features on top of raw council deliberations:

- **Points of Agreement / Unique Insights** (`analysis.py` → `extract_consensus_and_insights()`)
- **Disagreement Analysis** (`analysis.py` → `analyze_disagreements()`)
- **Council Synthesis** (`council.py` → `_synthesize()`)

All run on the same ≤1B models used for perspective generation.

---

## Timeline of failure — Consensus/Insights

| # | What we tried | Why it failed |
|---|--------------|---------------|
| 1 | Embedded `CONSENSUS_POINTS:` / `UNIQUE_INSIGHTS:` blocks inside the chairman synthesis prompt | Model ignored structured format in a long multi-task prompt |
| 2 | Separate call with combined two-section prompt | `Temperature.ANALYTICAL` typo → `AttributeError` swallowed by `except Exception`; silent `([], [])` |
| 3 | Fixed typo → still 0 items | Parser only matched `- ` bullets; model outputs `•` (U+2022) |
| 4 | Fixed `•` bullet handling → still 0 items | Parser matched `CONSENSUS_POINTS` exactly; model outputs `### Consensus Points:` |
| 5 | Fixed section header matching → still 0 items | Model ignored headers entirely; output was flat bullets with no section break |
| 6 | Split into two calls → items appeared but with member labels | Model grouped bullets by member, echoing `• Phi:` or `phi - idea` as prefixes |
| 7 | Added label filter + grounding instruction | ✅ Working in production |

**Total elapsed:** ~2 sessions (~3–4 hrs) due to 12-min iteration cycle.

---

## Timeline of failure — Disagreement Analysis

| # | What we tried | Why it failed |
|---|--------------|---------------|
| 1 | Original prompt: "identify points where perspectives fundamentally conflict" | Model flagged same-topic-different-subtopic pairs as FUNDAMENTAL (e.g. employee burnout vs. employer termination) |
| 2 | Added explicit contradiction test (Step 1/Step 2 in prompt) | Model echoed the example text from the prompt verbatim as if it were a real quote |
| 3 | Reframed as "find opposite recommendations"; injected member names | Model produced single-position disagreements (one member per entry, not two) |
| 4 | Added parser guard (discard if <2 positions) + stricter prompt | Reduced to 1 false positive; genuine disagreements found correctly |

**Remaining gap:** Topically adjacent statements from different subtopics (employer vs. employee perspective) still occasionally slip through. No prompt reliably solves this at ≤1B — see issue #33.

---

## Timeline of failure — Council Synthesis

| # | What we tried | Why it failed |
|---|--------------|---------------|
| 1 | Vague system prompt: "synthesize multiple perspectives into a coherent response" | Model defaulted to `From phi's perspective... From psi's perspective...` — sequential summary, not synthesis. Repeated "A synthesis of perspectives suggests..." multiple times. |
| 2 | Rewrote prompt with explicit prohibitions + direct-opening requirement | ✅ 3 concise sentences, grounded, no repetition |

---

## Root causes

### A — Typing error masked by silent failure

`Temperature.ANALYTICAL` does not exist; correct is `Temperature.ANALYSIS`. Caught by `except Exception`, logged only as WARNING without `exc_info=True`. Feature silently returned `([], [])` — indistinguishable from "model found nothing."

**Fix:** `exc_info=True`, feature name in log message, verify imports with `python -c` before rebuilding.

### B — Parser fragility against real model output

Parsers written to match a single bullet style and exact header strings, with no tests against real model output. Each format mismatch took a full 12-minute cycle to discover.

**Fix:** Normalize headers. Accept `•` and `-`. Unit tests against known-bad strings before model contact.

### C — Multi-task prompts exceed small model capacity

Sub-1B models cannot reliably follow two structural constraints in one prompt. When asked for two labeled sections they output one of: flat bullets, echo of section labels without content, or per-member groupings.

**Fix:** One task per call. `asyncio.gather()` for parallel execution.

### D — No fast feedback loop

Full cycle was `edit → docker build (2m) → deliberate (10m) → grep logs`. Seven iterations = 3–4 hours.

**Fix:** Probe scripts (30s) + parser unit tests (<1s) + volume-mounted scripts (no rebuild for script edits).

### E — Models hallucinate from training data

When asked to extract ideas from perspectives, models supplement or replace perspective content with training data. On a "2+2" question, Points of Agreement included a bullet about "publicly owned, vertically integrated healthcare systems."

**Fix:** Explicit grounding instruction in every extraction prompt: *"Only include ideas directly stated in the perspectives above. Do not add, infer, or invent anything not in the text."*

### F — Models cannot detect logical contradiction

Disagreement detection requires determining whether accepting claim A forces rejection of claim B. Sub-1B models cannot do this reliably. They pattern-match on topic overlap instead — any two statements about "leaving a job" get paired as a FUNDAMENTAL disagreement, even if one is about the employee quitting and the other is about the employer terminating.

**Fix (partial):** Reframe as "find opposite recommendations" (concrete) rather than "find contradictions" (abstract). Inject real member names. Parser guard: discard any disagreement with fewer than 2 distinct member positions.

### G — Synthesis defaults to per-member paragraph structure

Without explicit prohibition, models write `From phi's perspective... From psi's perspective...` — a sequential summary, not a synthesis. Filler phrases (`A synthesis of perspectives suggests`, `In conclusion`, `It's essential to consider multiple factors`) appear without instruction to avoid them.

**Fix:** Explicitly ban per-member paragraph structure and filler phrases by name. Require direct opening. Cap at 3–5 sentences.

---

## Observed model behavior patterns

| Prompt asked for | Model actually produced |
|-----------------|------------------------|
| `CONSENSUS_POINTS:` header | `### Consensus Points:` or `**Consensus Points:**` |
| `- ` dash bullets | `•` (U+2022) bullets |
| Two labeled sections | Flat unlabeled bullet list |
| Content bullets only | Member names as prefix (`• Phi:`, `phi - idea`) or suffix (`idea - phi`, `idea (phi)`) |
| NONE sentinel | `-NONE`, `- -NONE`, `NONE.` |
| Format spec at bottom of prompt | Ignored; model continues in tone of preceding context |
| Template placeholder (`member_name`) | Echoed literally as output |
| Synthesis prose | `From [name]'s perspective...` per-member paragraphs |
| Disagreement between opposing claims | Any two statements on the same broad topic, regardless of whether they conflict |
| MODERATE severity by default | FUNDAMENTAL regardless of actual severity |

---

## What works with small models

### 1. One task per call

Never ask a ≤2B model to produce two structurally distinct sections. Split into two calls and `asyncio.gather()` them.

### 2. Format at the top

Place output format spec at the very beginning of the prompt, before any context.

```python
# Works
"Output a bullet list. Only bullets, no prose.\n\nPerspectives:\n{perspectives}"

# Fails
"Here are some perspectives...\n{perspectives}\n\nPlease output a bullet list."
```

### 3. Ground the model

Add to every extraction prompt: *"Only include ideas directly stated in the perspectives above. Do not add, infer, or invent anything not present in the text."* Without this, models hallucinate from training data.

### 4. Inject concrete values

Pass member names, counts, and example format using actual values — never template placeholders the model could echo. `{member_names}` in the prompt, filled with `"phi and psi"` at call time.

### 5. Ban bad patterns by name

Vague instructions ("be concise", "write coherently") are ignored. Explicit prohibitions work:
- "Do not write `From [name]'s perspective`"
- "Forbidden phrases: `In conclusion`, `A synthesis of`, `multiple factors`"
- "Open with a direct answer — no preamble"

### 6. Defensive parsers

- Normalize headers: lowercase, strip `#*_`, replace `_` with space
- Accept `•` and `-` equally
- Strip member-name affixes in all positions: `phi: idea`, `phi - idea`, `idea - phi`, `idea (phi)`
- NONE sentinel variants: `text.strip("- ").upper() == "NONE"`
- Discard entries with fewer than 2 member positions (disagreement parser)

### 7. Parser unit tests before model contact

The parser is a pure function. Write tests against known-bad model output strings before running the model once.

### 8. Probe script for every new extraction feature

```bash
python scripts/probe_consensus.py      # consensus/insights
python scripts/probe_disagreements.py  # disagreement analysis
python scripts/probe_synthesis.py      # chairman synthesis
```

30 seconds vs. 12 minutes.

### 9. Never swallow exceptions silently

```python
# Bad
except Exception as e:
    return [], []

# Good
except Exception as e:
    logger.warning("Feature extraction failed: %s", e, exc_info=True)
    return [], []
```

### 10. Verify attribute names before rebuilding

```bash
python -c "from src.config import Temperature; print(Temperature.ANALYSIS)"
```

---

## Files

| File | Purpose |
|------|---------|
| `backend/src/analysis.py` | All extraction logic and parsers |
| `backend/src/council.py` | Chairman synthesis prompt (`_CHAIRMAN_SYSTEM_PROMPT`) |
| `backend/tests/test_parsing.py` | 12 parser unit tests; runs in <0.1s |
| `backend/scripts/probe_consensus.py` | 30s probe for consensus/insights |
| `backend/scripts/probe_disagreements.py` | 30s probe with false-positive fixtures |
| `backend/scripts/probe_synthesis.py` | 30s probe for chairman synthesis |

## Related

- GitHub issue #33 — Known limits of ≤1B models for structured analysis extraction
