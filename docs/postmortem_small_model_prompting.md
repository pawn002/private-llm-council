# Post-Mortem: Small Model Structured Output

**Feature:** Points of Agreement / Unique Insights extraction  
**Branch:** `task-19-candor-design-system`  
**Resolution commit:** `90aee41`

---

## TL;DR — Rules for prompting sub-2B models

1. **One task per call.** Two structured sections in one prompt → unreliable. Two calls → works.
2. **Format at the top.** Instructions after context paragraphs get ignored. Lead with the output spec.
3. **Write defensive parsers.** Normalize headers, accept `•` and `-`, filter label echoes. Never match exact strings.
4. **Unit-test the parser before touching a model.** It's a pure function. 0.1s, no Ollama needed.
5. **Build a probe script for every new extraction call.** 30s to validate output format, not 12 minutes.
6. **Never swallow LLM exceptions silently.** `([], [])` and "crashed" look identical without explicit logging.
7. **Verify attribute names locally before rebuilding.** One `python -c` import check saves a container rebuild.

---

## What we were building

The synthesis panel needed two structured lists extracted from each deliberation:
- **Points of Agreement** — ideas all or most council members shared
- **Unique Insights** — distinctive ideas raised by only one member

These required a dedicated LLM extraction step in `backend/src/analysis.py`, separate from
the chairman synthesis prompt. The models in use are ≤1B parameters running locally via Ollama.

---

## Timeline of failure

| # | What we tried | Why it failed |
|---|--------------|---------------|
| 1 | Embedded `CONSENSUS_POINTS:` / `UNIQUE_INSIGHTS:` blocks inside the chairman synthesis prompt | Model (≤1B) ignored structured format in a long multi-task prompt; section markers never appeared in output |
| 2 | Separate `extract_consensus_and_insights()` call with a combined two-section prompt | `Temperature.ANALYTICAL` typo → `AttributeError` swallowed by bare `except Exception`; feature silently returned `([], [])` |
| 3 | Fixed typo → still 0 items, no error | Parser only matched `- ` bullets; model outputs `•` (U+2022) |
| 4 | Fixed `•` bullet handling → still 0 items | Parser matched `CONSENSUS_POINTS` exactly; model outputs `### Consensus Points:` |
| 5 | Fixed section header matching (case-insensitive, strip `#`/`*`) → still 0 items | Model ignored section headers entirely; output was flat bullets with no section break |
| 6 | Split into two focused calls, simpler prompts → items appeared but included member labels | Model grouped bullets by member, echoing `• Phi:` as a bullet before the actual content |
| 7 | Added label filter + "do not include member names" → 5 consensus, 3 unique insights | ✅ Confirmed working in production |

**Total elapsed:** ~2 sessions, ~3–4 hours of clock time — disproportionate to the feature's complexity, almost entirely due to the 12-minute iteration cycle.

---

## Root causes

### A — Typing error masked by silent failure

`Temperature.ANALYTICAL` does not exist. The correct attribute is `Temperature.ANALYSIS`.
The `AttributeError` was caught by a bare `except Exception` at the call site and logged only
as a WARNING that was not visible unless explicitly grepped. The function returned `([], [])`,
indistinguishable from "model found nothing."

**Fix:** Log with `exc_info=True`. Name the feature in the warning message so it appears in
targeted log greps. Consider re-raising in development to make crashes loud.

### B — Parser fragility against real model output

The parser was written to match a single bullet style (`- `) and exact uppercase header strings
(`CONSENSUS_POINTS`). No tests existed against real model output. The actual model output used
`•` bullets (U+2022) and markdown-headed section labels (`### Consensus Points:`).

Because there were no unit tests, each format mismatch required a full 12-minute cycle to discover.

**Fix:** Normalize headers (lowercase, strip `#*_`, replace `_` with space). Accept both `•` and `-`.
Write unit tests against the actual bad strings before ever running the model.

### C — Multi-task prompts exceed small model instruction-following capacity

Sub-1B models cannot reliably follow two structural constraints simultaneously in one prompt.
When asked to produce two labeled sections, they typically do one of:

- Output one list and ignore the second
- Output both without the section labels (flat bullets)
- Echo the section label text without any content beneath it
- Reinterpret the task as a per-member breakdown, using member names as section headers

The longer the prompt, the worse this gets. Instructions appearing after several paragraphs of
context are effectively invisible to these models.

**Fix:** One task per call. Parallel calls add negligible latency and eliminate the structural constraint.

### D — No fast feedback loop

The full iteration cycle was:

```
edit → docker compose build (1–2 min) → open browser → submit deliberation (5–10 min LLM time) → grep logs
```

With this cycle, 7 iterations consumed 3–4 hours. There was no way to observe raw model output
in isolation, no way to test the parser without a real model, and no way to validate a prompt
change in under 10 minutes.

**Fix:** The probe script (`backend/scripts/probe_consensus.py`) and unit test suite
(`backend/tests/test_parsing.py`) built as part of the resolution reduce this to:

| Concern | Time |
|---------|------|
| Parser change | `pytest tests/test_parsing.py` → <1s |
| Prompt change | `python scripts/probe_consensus.py` → ~30s |
| Deploy | `docker compose build backend && docker compose up -d backend` → ~1min |

---

## Observed model behavior patterns

What ≤1B models actually produce vs. what the prompt requested:

| Prompt asked for | Model actually produced |
|-----------------|------------------------|
| `CONSENSUS_POINTS:` header | `### Consensus Points:` or `**Consensus Points:**` |
| `- ` dash bullets | `•` (U+2022) bullets |
| Two labeled sections | Flat unlabeled bullet list |
| Content bullets only | Member names as section bullets (`• Phi:`) followed by sub-bullets |
| Format spec at bottom of prompt | Ignored entirely; model continues in the tone of the preceding context |

These are not bugs in any one model — they are general behaviors of small instruction-tuned
models when format requirements conflict with the natural continuation of long-context prompts.

---

## What works with small models

### 1. One task per call

Never ask a ≤2B model to produce two structurally distinct sections in a single response.
The model will satisfy one constraint and silently drop the other, or produce a hybrid that
satisfies neither. Split into two calls and `asyncio.gather()` them — the latency cost is
a single round-trip.

### 2. Format at the top

Models are autoregressive: early tokens shape late tokens. Place the output format specification
at the very beginning of the prompt, before any context. Then give the data.

```
# Works
"Output a bullet list. Only bullets, no prose.\n\nPerspectives:\n{perspectives}"

# Fails
"Here are some perspectives...\n{perspectives}\n\nPlease output a bullet list."
```

### 3. Defensive parsers

Parsers for LLM output should never match exact strings. Assume the model will:
- Use different capitalization
- Add markdown decorators (`#`, `**`, `_`)
- Use `•` instead of `-`
- Echo label text as bullet content

Normalize before matching. Filter out anything that looks like a label (ends with `:`,
short string with `:`, single word). Keep only substantive sentences.

### 4. Parser unit tests before model contact

The parser is a pure function with no dependencies. Write unit tests against the expected
bad strings — `•` bullets, `### Headers`, member echoes — before running the model once.
This separates "the model doesn't follow the format" from "the parser can't handle the format."

### 5. Probe script for every new extraction feature

Before integrating a new extraction call into the full deliberation flow, write a standalone
probe script:
- Hardcoded minimal fixtures (2–3 short perspectives)
- One LLM call
- Prints raw response and parsed output

Pattern: `backend/scripts/probe_consensus.py`. Add `--model` arg; default to the smallest
available model.

### 6. Never swallow exceptions silently

```python
# Bad
except Exception as e:
    logger.warning("Failed: %s", e)
    return [], []

# Better
except Exception as e:
    logger.warning("Consensus/insights extraction failed: %s", e, exc_info=True)
    return [], []
```

`exc_info=True` prints the full traceback. Naming the feature in the message makes it
greppable: `docker compose logs backend | grep "extraction failed"`.

### 7. Verify imports locally before rebuilding

Before any container rebuild, check that enum values, module paths, and attribute names
exist in the current codebase:

```bash
cd backend
python -c "from src.config import Temperature; print(Temperature.ANALYSIS)"
```

This catches `AttributeError` in 1 second instead of 12 minutes.

---

## Changes made

| File | Change |
|------|--------|
| `backend/src/analysis.py` | Split `CONSENSUS_INSIGHTS_PROMPT` into `CONSENSUS_POINTS_PROMPT` + `UNIQUE_INSIGHTS_PROMPT`; parallel `asyncio.gather()` calls; `_parse_bullet_list()` helper with label filter; `_parse_consensus_insights()` retains combined-response fallback with normalized header matching |
| `backend/tests/test_parsing.py` | 12 unit tests covering dash bullets, `•` bullets, NONE exclusion, missing headers, bold headers, markdown heading + mixed case, empty response, mixed styles |
| `backend/scripts/probe_consensus.py` | Standalone probe: hardcoded fixtures, parallel calls, prints raw + parsed |
| `backend/Dockerfile` | `pip install ".[dev]"` — pytest available inside container |
| `docker-compose.yml` | Volume-mounts `./backend/tests` and `./backend/scripts` for live edits without rebuild |
