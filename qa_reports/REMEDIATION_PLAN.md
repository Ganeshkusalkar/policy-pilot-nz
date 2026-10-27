# PolicyPilot NZ — Remediation Plan & Prioritized Action Checklist

**Date:** 2026-10-27  
**Author:** Senior QA Engineer, Test Automation Engineer & Application Security Auditor  
**Status:** Completed Initial Remediation (Batch 1) & Roadmap (Batch 2 & 3)

---

## 1. Executive Remediation Overview

This document outlines the prioritized engineering fixes identified during the comprehensive QA and security audit of PolicyPilot NZ. Issues are categorized by severity (P0 to P3), with status tracking across three phases:
- **Phase 1 (Immediate / Completed):** Critical bugs, input validation bypasses, citation parser brittleness, working directory dependencies, and security enhancements resolved locally during the audit.
- **Phase 2 (Pre-Launch / Required for Public Production):** Infrastructure resilience, CORS hardening, rate limiting, and automated corpus ingestion CI/CD pipelines.
- **Phase 3 (Post-Launch / Enhancement):** Advanced retrieval expansions (hybrid RRF activation in API, cross-encoder reranking, multi-act corpus scaling).

---

## 2. Prioritized Action Table

| Issue ID | Severity | Category | Component | Description & Root Cause | Est. Complexity | Status |
| :--- | :---: | :--- | :--- | :--- | :---: | :---: |
| **ISSUE-01** | **P1** | Input Validation | `app/api/ask.py` | Whitespace-only strings and sub-minimum questions accepted as HTTP 200. Pydantic `min_length=3` checked before stripping. | Low (1 pt) | **RESOLVED** |
| **ISSUE-02** | **P1** | RAG / Legal Integrity | `app/services/qa_service.py` | Citation label parser discarded legitimate answers when Gemini output natural language section lists (e.g. `Section 22 and 23`). | Low (2 pts) | **RESOLVED** |
| **ISSUE-03** | **P1** | Architecture / Reliability | `app/services/qa_service.py` | `DATA_PATH` used relative path `"data/processed/..."` breaking on non-root execution with 503. | Low (1 pt) | **RESOLVED** |
| **ISSUE-04** | **P2** | Retrieval / Localization | `app/retrieval/bm25.py` | ASCII regex `[a-z0-9]+` chopped Māori macrons (e.g. `Māori` -> `['m', 'ori']`), degrading NZ legal search. | Low (2 pts) | **RESOLVED** |
| **ISSUE-05** | **P2** | Reliability / Resilience | `app/services/qa_service.py` | Gemini 429 quota exhaustion or transient glitches caused immediate 503 errors without backoff. | Low (2 pts) | **RESOLVED** |
| **ISSUE-06** | **P2** | Developer Ergonomics | `scripts/*` | Direct execution of scripts failed with `ModuleNotFoundError: No module named 'app'`. | Low (1 pt) | **RESOLVED** |
| **ISSUE-07** | **P2** | Security (XSS / Tabnabbing) | `frontend/src/App.jsx` | Citation URLs lacked protocol verification and `rel="noopener"` on external links. | Low (1 pt) | **RESOLVED** |
| **ISSUE-08** | **P2** | Configuration / Deployment | `app/config.py`, `app/main.py` | CORS origins were hardcoded in `app/main.py` without environment variable support. | Low (1 pt) | **RESOLVED** |
| **ISSUE-09** | **P3** | Documentation | `README.md` | Missing reproducible deployment documentation for Render and Vercel. | Low (1 pt) | **RESOLVED** |
| **ISSUE-10** | **P3** | Security / Secret Mgmt | `frontend/.gitignore` | `frontend/.gitignore` omitted `.env*` entries, risking standalone repository leaks. | Low (1 pt) | **RESOLVED** |
| **ISSUE-11** | **P3** | Retrieval Quality | `app/retrieval/bm25.py` | Synonym gaps for civil liberties (e.g. "protest", "demonstrate" failed to find Section 16). | Low (1 pt) | **RESOLVED** |
| **ISSUE-12** | **P2** | Rate Limiting & DoS | Backend API | Public `/ask` endpoint has no IP-based rate limiting (SlowAPI), exposing Gemini key to exhaustion. | Medium (3 pts) | **RECOMMENDED** |
| **ISSUE-13** | **P2** | Deployment Automation | CI / Render | `data/processed/` is Git-ignored; Render must execute build script to avoid empty corpus. | Medium (2 pts) | **RECOMMENDED** |
| **ISSUE-14** | **P3** | Retrieval Evolution | `app/services/qa_service.py` | API only uses BM25; semantic and hybrid embeddings are evaluated in scripts but not exposed in `/ask`. | Medium (5 pts) | **RECOMMENDED** |

---

## 3. Detailed Remediation Specifications

### ISSUE-01: Input Validation Hardening (Completed)
- **Rationale:** API contracts must be strictly enforced at the perimeter to reject malformed, empty, or whitespace queries before invoking downstream language models.
- **Implementation:** Added Pydantic `field_validator(mode="before")` on `AskRequest.question` to strip leading/trailing whitespace prior to evaluating `min_length=3` and `max_length=1000`.
- **Validation:** `tests/test_audit_regressions.py::test_ask_rejects_whitespace_only_question` and `test_ask_rejects_sub_minimum_stripped_question` confirm HTTP 422.

### ISSUE-02: Citation Label Robustness & Fail-Closed Validation (Completed)
- **Rationale:** Discarding a legally accurate answer due to trivial label styling (e.g., Gemini adding `"Section 22"` instead of `"22"`) damages user trust.
- **Implementation:** Implemented `normalize_section_label()` using regex `re.sub(r"^(?:sections?|s\.?)\s*", "", label)` and token splitting by `[,;]|\band\b`. Maintained strict subset check against retrieved evidence to preserve anti-hallucination guarantees.
- **Validation:** `tests/test_audit_regressions.py::test_filter_citations_handles_natural_language_section_lists` passes; hallucinated section injection `TC-SEC-02` reliably triggers abstention.

### ISSUE-03: Absolute Corpus Resolution (Completed)
- **Rationale:** Server startup commands vary by platform (`uvicorn app.main:app` vs containerized paths). A relative path causes catastrophic 503 failures if `cwd` is altered.
- **Implementation:** Set `DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / ...` with override support via `CORPUS_PATH` environment variable.
- **Validation:** `tests/test_audit_regressions.py::test_get_documents_resilient_to_working_directory` executes `os.chdir(tmp_path)` and confirms corpus loads without error.

### ISSUE-04: Unicode & Māori Macron Normalization (Completed)
- **Rationale:** New Zealand legislation frequently incorporates Māori concepts and names. Stripping accented characters into disjoint ASCII fragments breaks keyword matching.
- **Implementation:** Integrated `unicodedata.normalize("NFKD", text)` into `tokenize()`, removing combining diacritic marks before regex evaluation (`Māori` -> `Maori`).
- **Validation:** `tests/test_audit_regressions.py::test_bm25_tokenize_normalizes_maori_macrons` passes (`tokenize("Māori") == tokenize("Maori")`).

### ISSUE-05: Transient Retry Wrapper for Model Generation (Completed)
- **Rationale:** Public LLM APIs experience transient 429 quota spikes or network timeouts. Immediate 503 failure degrades user experience.
- **Implementation:** Wrapped `client.models.generate_content()` with exponential backoff (up to 3 attempts with 1.0s, 2.0s delay on 429 / RESOURCE_EXHAUSTED).
- **Validation:** Verified via sequential query evaluation script where burst requests recovered automatically.

### ISSUE-07: Frontend Link Protocol & Window Security (Completed)
- **Rationale:** Rendering unsanitized `href={url}` from third-party or LLM output introduces XSS risk (`javascript:`). Opening links in new tabs without `noopener` exposes the window object.
- **Implementation:** Updated `getCitationUrl()` in `App.jsx` with strict regex `/^https?:\/\//i`. Added `rel="noopener noreferrer"` to all outbound anchor tags.
- **Validation:** Verified in `frontend/src/App.jsx` and production build verification (`npm run build`).

### ISSUE-08: Configurable CORS Allowed Origins (Completed)
- **Rationale:** Supporting multiple frontend environments (local, Vercel preview URLs, production custom domains) requires dynamic configuration.
- **Implementation:** Configured `allowed_origins` in `app/config.py` sourced from `ALLOWED_ORIGINS` environment variable, defaulting to development and production domains.
- **Validation:** Verified in `app/main.py` middleware initialization and API startup tests.

---

## 4. Phase 2 & 3 Remediation Recommendations

### Recommendation 1: Rate Limiting & Denial-of-Service Defense (ISSUE-12)
- **Problem:** Anyone can submit hundreds of expensive AI queries to `POST /ask`.
- **Recommendation:** Implement `slowapi` with IP-based rate limiting (e.g., 20 requests per minute per IP):
  ```python
  from slowapi import Limiter, _rate_limit_exceeded_handler
  from slowapi.util import get_remote_address
  limiter = Limiter(key_func=get_remote_address)
  @router.post("/ask")
  @limiter.limit("20/minute")
  def ask(...): ...
  ```

### Recommendation 2: CI/CD Pipeline for Corpus Verification (ISSUE-13)
- **Problem:** Because `data/processed/` is Git-ignored, a Render redeploy without running `python scripts/process_legislation.py` results in an empty corpus.
- **Recommendation:** Add a GitHub Actions workflow `.github/workflows/ci.yml` that:
  1. Installs dependencies.
  2. Runs `python scripts/fetch_legislation.py` or verifies fixture XML.
  3. Executes `python scripts/process_legislation.py`.
  4. Runs full test suite `pytest`.

### Recommendation 3: Hybrid Retrieval Integration in API (ISSUE-14)
- **Problem:** BM25 keyword matching cannot capture semantic phrasing where words differ entirely. While `HybridIndex` exists in `app/retrieval/hybrid.py`, the production API only calls `BM25Index`.
- **Recommendation:** Provide an environment flag `RETRIEVAL_STRATEGY=hybrid` in `app/config.py` allowing Render or local environments with adequate memory (>=1GB RAM) to leverage the already implemented semantic embeddings.
