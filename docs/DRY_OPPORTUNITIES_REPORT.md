# DRY Refactoring Opportunities Report

**Date:** 2026-01-03
**Codebase:** Private LLM Council
**Total Violations Found:** 19

---

## Executive Summary

This report identifies opportunities to apply DRY (Don't Repeat Yourself) principles across the codebase. Each opportunity is ranked using an **Effort vs Impact** matrix to help prioritize refactoring work.

### Scoring Criteria

| Metric | Scale | Description |
|--------|-------|-------------|
| **Effort** | 1-5 | 1 = trivial (<30 min), 5 = significant (>1 day) |
| **Impact** | 1-5 | 1 = minor improvement, 5 = major maintainability gain |
| **Priority Score** | Impact / Effort | Higher = better ROI |

---

## Priority Tiers

### Tier 1: Quick Wins (Priority Score >= 2.0)

These deliver high value with minimal effort. **Recommended for immediate action.**

| # | Opportunity | Effort | Impact | Score | Files |
|---|-------------|--------|--------|-------|-------|
| 1 | System initialization guard decorator | 1 | 5 | **5.0** | `main.py` |
| 2 | Clamp float utility function | 1 | 3 | **3.0** | `analysis.py` |
| 3 | Colon-line value extractor | 1 | 3 | **3.0** | `analysis.py` |
| 4 | Perspectives text formatter | 1 | 3 | **3.0** | `council.py`, `analysis.py` |
| 5 | Member identity constants | 1 | 3 | **3.0** | `perspective-card.component.ts` |
| 6 | Temperature constants | 1 | 2 | **2.0** | `council.py`, `analysis.py` |

### Tier 2: Moderate Value (Priority Score 1.0 - 1.99)

Good improvements that require more effort but pay off in maintainability.

| # | Opportunity | Effort | Impact | Score | Files |
|---|-------------|--------|--------|-------|-------|
| 7 | Gateway health check helper | 2 | 4 | **2.0** | `main.py` |
| 8 | Confidence meter component | 2 | 3 | **1.5** | `synthesis-panel.component.html` |
| 9 | List section component | 2 | 3 | **1.5** | `synthesis-panel.component.html` |
| 10 | Observable subscription helper | 3 | 4 | **1.3** | `deliberation.service.ts`, `privacy.service.ts` |
| 11 | Status badge component | 2 | 2 | **1.0** | `consent-banner.component.html` |

### Tier 3: Strategic Improvements (Priority Score < 1.0)

Larger refactors that improve architecture but require significant investment.

| # | Opportunity | Effort | Impact | Score | Files |
|---|-------------|--------|--------|-------|-------|
| 12 | Unified serialization layer | 4 | 4 | **1.0** | `main.py`, `persistence.py` |
| 13 | State subject helper class | 3 | 2 | **0.7** | `deliberation.service.ts`, `privacy.service.ts` |
| 14 | Typed state update helpers | 3 | 2 | **0.7** | `deliberation.service.ts` |
| 15 | Phase view components | 4 | 2 | **0.5** | `council.component.html` |

---

## Detailed Analysis

### Tier 1: Quick Wins

#### 1. System Initialization Guard Decorator
**Priority Score: 5.0** | Effort: 1 | Impact: 5

**Current State:** 11 occurrences of identical guard checks across endpoints:
```python
if not _gateway or not _config:
    raise HTTPException(status_code=503, detail="System not initialized")
if not _store:
    raise HTTPException(status_code=503, detail="Store not initialized")
```

**Proposed Solution:**
```python
def require_initialized(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not _gateway or not _config:
            raise HTTPException(status_code=503, detail="System not initialized")
        return await func(*args, **kwargs)
    return wrapper

def require_store(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not _store:
            raise HTTPException(status_code=503, detail="Store not initialized")
        return await func(*args, **kwargs)
    return wrapper

# Usage:
@app.post("/deliberate")
@require_initialized
async def deliberate(request: DeliberationRequest):
    ...
```

**Benefits:**
- Eliminates 11 duplicate checks
- Consistent error messages
- Single point of maintenance
- Cleaner endpoint code

---

#### 2. Clamp Float Utility Function
**Priority Score: 3.0** | Effort: 1 | Impact: 3

**Current State:** (`analysis.py:391,397,403`)
```python
overall = max(0.0, min(1.0, overall))
consensus = max(0.0, min(1.0, consensus))
dissent = max(0.0, min(1.0, dissent))
```

**Proposed Solution:**
```python
def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a value to the specified range."""
    return max(min_val, min(max_val, value))

# Usage:
overall = clamp(overall)
consensus = clamp(consensus)
dissent = clamp(dissent)
```

**Benefits:**
- Self-documenting code
- Reusable across codebase
- Prevents copy-paste errors

---

#### 3. Colon-Line Value Extractor
**Priority Score: 3.0** | Effort: 1 | Impact: 3

**Current State:** 11 occurrences in `analysis.py`:
```python
current_disagreement.topic = line.split(":", 1)[1].strip()
reasoning = line.split(":", 1)[1].strip()
```

**Proposed Solution:**
```python
def extract_value(line: str) -> str:
    """Extract the value after the first colon in a line."""
    if ":" not in line:
        return line.strip()
    return line.split(":", 1)[1].strip()

# Usage:
current_disagreement.topic = extract_value(line)
```

**Benefits:**
- Handles edge cases (missing colon) gracefully
- Single point for parsing logic changes
- Clearer intent

---

#### 4. Perspectives Text Formatter
**Priority Score: 3.0** | Effort: 1 | Impact: 3

**Current State:** (`council.py:425`, `analysis.py:166,206`)
```python
perspectives_text = "\n\n".join(
    f"### {p.member_id} ({p.character})\n{p.content}" for p in perspectives
)
```

**Proposed Solution:**
```python
def format_perspectives_for_prompt(
    perspectives: list[Perspective],
    include_character: bool = True
) -> str:
    """Format perspectives for LLM prompt consumption."""
    if include_character:
        return "\n\n".join(
            f"### {p.member_id} ({p.character})\n{p.content}"
            for p in perspectives
        )
    return "\n\n".join(
        f"### {p.member_id}\n{p.content}"
        for p in perspectives
    )
```

**Benefits:**
- Consistent formatting across all prompts
- Easy to modify format in one place
- Supports variations via parameter

---

#### 5. Member Identity Constants
**Priority Score: 3.0** | Effort: 1 | Impact: 3

**Current State:** (`perspective-card.component.ts:18-32`)
```typescript
private readonly memberColors: Record<string, string> = {
  phi: 'border-blue',
  psi: 'border-purple',
  // ... repeated elsewhere
};
```

**Proposed Solution:** Create `frontend/src/app/constants/member-identity.ts`:
```typescript
export const MEMBER_COLORS: Record<string, string> = {
  phi: 'border-blue',
  psi: 'border-purple',
  omega: 'border-amber',
  sigma: 'border-green',
  delta: 'border-red',
};

export const MEMBER_ICONS: Record<string, string> = {
  phi: 'Φ', psi: 'Ψ', omega: 'Ω', sigma: 'Σ', delta: 'Δ',
};

export const getMemberColor = (id: string): string =>
  MEMBER_COLORS[id] || 'border-gray';

export const getMemberIcon = (id: string): string =>
  MEMBER_ICONS[id] || '?';
```

**Benefits:**
- Single source of truth for member identities
- Easy to add new members
- Consistent across all components

---

#### 6. Temperature Constants
**Priority Score: 2.0** | Effort: 1 | Impact: 2

**Current State:** Hardcoded in 5 places across `council.py` and `analysis.py`:
```python
temperature=0.3,  # Lower temperature for more consistent analysis
temperature=0.2,  # Even lower for confidence
```

**Proposed Solution:** Add to `config.py` or create `constants.py`:
```python
class PromptTemperatures:
    """Temperature settings for different prompt types."""
    PERSPECTIVE = 0.7      # Creative individual responses
    SYNTHESIS = 0.5        # Balanced synthesis
    ANALYSIS = 0.3         # Consistent analysis
    CONFIDENCE = 0.2       # Deterministic confidence scoring
```

**Benefits:**
- Easy tuning without code search
- Self-documenting purpose
- Consistent across all LLM calls

---

### Tier 2: Moderate Value

#### 7. Gateway Health Check Helper
**Priority Score: 2.0** | Effort: 2 | Impact: 4

**Current State:** 5 locations perform health checks with similar error handling.

**Proposed Solution:**
```python
async def ensure_gateway_healthy() -> None:
    """Verify gateway is healthy or raise appropriate HTTPException."""
    if not _gateway:
        raise HTTPException(status_code=503, detail="Gateway not initialized")

    health = await _gateway.health_check()
    if not health.healthy:
        raise HTTPException(
            status_code=503,
            detail=f"Inference gateway unhealthy. Available models: {health.available_models}"
        )
```

**Benefits:**
- Consistent error messages
- Single point for health check logic
- Easier to add retry logic if needed

---

#### 8. Confidence Meter Component
**Priority Score: 1.5** | Effort: 2 | Impact: 3

**Current State:** (`synthesis-panel.component.html:16-48`) Three identical meter blocks.

**Proposed Solution:** Create `ConfidenceMeterComponent`:
```typescript
@Component({
  selector: 'app-confidence-meter',
  template: `
    <div class="meter">
      <span class="meter-label">{{ label() }}</span>
      <div class="meter-track">
        <div class="meter-fill"
             [class]="colorClass()"
             [style.width.%]="percentage()">
        </div>
      </div>
      <span class="meter-value">{{ percentage() }}%</span>
    </div>
  `
})
export class ConfidenceMeterComponent {
  label = input.required<string>();
  value = input.required<number>();

  percentage = computed(() => Math.round(this.value() * 100));
  colorClass = computed(() => {
    const v = this.value();
    if (v >= 0.7) return 'high';
    if (v >= 0.4) return 'medium';
    return 'low';
  });
}
```

**Benefits:**
- Reduces template by ~30 lines
- Reusable for other metrics
- Encapsulates display logic

---

#### 9. List Section Component
**Priority Score: 1.5** | Effort: 2 | Impact: 3

**Current State:** Three nearly identical list sections in `synthesis-panel.component.html`.

**Proposed Solution:** Create `ListSectionComponent`:
```typescript
@Component({
  selector: 'app-list-section',
  template: `
    @if (items().length > 0) {
      <div class="card" [class]="cardClass()">
        <h3><span>{{ icon() }}</span> {{ title() }}</h3>
        <ul>
          @for (item of items(); track item) {
            <li>
              <span class="bullet" [class]="bulletColor()">•</span>
              {{ item }}
            </li>
          }
        </ul>
      </div>
    }
  `
})
export class ListSectionComponent {
  title = input.required<string>();
  items = input.required<string[]>();
  icon = input<string>('');
  cardClass = input<string>('');
  bulletColor = input<string>('');
}
```

**Benefits:**
- Reduces template by ~40 lines
- Consistent styling
- Easy to add new list sections

---

#### 10. Observable Subscription Helper
**Priority Score: 1.3** | Effort: 3 | Impact: 4

**Current State:** Repeated subscription patterns with similar error handling.

**Proposed Solution:** Create utility function:
```typescript
export function handleApiCall<T>(
  observable: Observable<T>,
  onSuccess: (result: T) => void,
  onError?: (error: Error) => void
): Subscription {
  return observable.subscribe({
    next: onSuccess,
    error: (err) => {
      const message = err.message || 'An unexpected error occurred';
      console.error('API Error:', message);
      onError?.(err);
    },
  });
}
```

**Benefits:**
- Consistent error handling
- Reduces boilerplate in services
- Centralized error logging

---

### Tier 3: Strategic Improvements

#### 12. Unified Serialization Layer
**Priority Score: 1.0** | Effort: 4 | Impact: 4

**Current State:** `main.py:build_deliberation_response_dict()` and `persistence.py:DeliberationSerializer.to_dict()` have overlapping logic.

**Proposed Solution:** Create a canonical serialization in `persistence.py` that `main.py` imports:
```python
# persistence.py
class DeliberationSerializer:
    @staticmethod
    def to_api_response(deliberation: Deliberation) -> dict:
        """Serialize deliberation for API responses."""
        ...

    @staticmethod
    def to_storage(deliberation: Deliberation) -> dict:
        """Serialize deliberation for encrypted storage."""
        ...
```

**Benefits:**
- Single source of truth for serialization
- Guarantees API and storage formats stay aligned
- Easier to add new fields

---

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 hours)
1. Add `@require_initialized` decorator
2. Create `clamp()` and `extract_value()` utilities
3. Add temperature constants
4. Create member identity constants file

### Phase 2: Component Extraction (2-4 hours)
5. Create `ConfidenceMeterComponent`
6. Create `ListSectionComponent`
7. Create `format_perspectives_for_prompt()` utility

### Phase 3: Service Improvements (4-8 hours)
8. Add gateway health helper
9. Create subscription utility
10. Consolidate serialization layer

---

## Metrics Summary

| Tier | Count | Total Effort | Total Impact | Avg Priority |
|------|-------|--------------|--------------|--------------|
| Tier 1 (Quick Wins) | 6 | 6 | 19 | 3.17 |
| Tier 2 (Moderate) | 5 | 11 | 16 | 1.45 |
| Tier 3 (Strategic) | 4 | 14 | 10 | 0.71 |

**Recommendation:** Start with Tier 1 items for maximum ROI. The 6 quick wins require only ~6 hours of effort but eliminate 25+ instances of duplicated code.

---

## Appendix: Files Affected

| File | Violation Count |
|------|-----------------|
| `backend/src/main.py` | 4 |
| `backend/src/analysis.py` | 4 |
| `backend/src/council.py` | 2 |
| `backend/src/persistence.py` | 1 |
| `frontend/.../deliberation.service.ts` | 2 |
| `frontend/.../privacy.service.ts` | 1 |
| `frontend/.../perspective-card.component.ts` | 2 |
| `frontend/.../synthesis-panel.component.html` | 2 |
| `frontend/.../consent-banner.component.html` | 1 |
