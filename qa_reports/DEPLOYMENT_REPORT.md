# PolicyPilot NZ — Production Deployment & CI/CD Verification Report

**Report Date:** 2026-10-27  
**DevOps & QA Engineer:** Senior QA Engineer, DevOps & CI/CD Agent  
**Repository:** [https://github.com/Ganeshkusalkar/policy-pilot-nz](https://github.com/Ganeshkusalkar/policy-pilot-nz)  
**Target Branch:** `main`  
**Base Commit:** `d2091d9` ("Allow deployed frontend origin")  

---

## 1. Executive Deployment Summary

This report documents the CI/CD pipeline establishment, pre-deployment safety gates, automated build verification, and live production smoke tests conducted for PolicyPilot NZ across Render (FastAPI Backend) and Vercel (React Frontend).

### Deployment Status: **VERIFIED & OPERATIONAL**
- **Production Backend URL:** `https://policy-pilot-nz.onrender.com`
- **Backend Documentation:** `https://policy-pilot-nz.onrender.com/docs`
- **Health Check Endpoint:** `https://policy-pilot-nz.onrender.com/health` (HTTP 200 `{"status": "ok"}`)
- **Production API Smoke Test:** Verified live `POST /ask` responding with section citations and verified abstention behavior.
- **Frontend Target URL:** `https://policy-pilot-nz.vercel.app` (configured in CORS allowlist and Vercel blueprint)

---

## 2. CI/CD Infrastructure Configured

| Configuration File | Target Platform | Purpose |
| :--- | :--- | :--- |
| `.github/workflows/ci.yml` | GitHub Actions | Automated 3-stage pipeline: (1) Python 3.12 backend compilation & pytest, (2) Node 22 frontend linting & production build, (3) Git tracked secret leak scanner. |
| `render.yaml` | Render | Infrastructure-as-code blueprint: builds dependencies, triggers `python scripts/process_legislation.py` for corpus generation, sets Python 3.12, defines health check at `/health`. |
| `vercel.json` | Vercel | Root configuration directing Vercel to `frontend/`, running `npm install && npm run build` and outputting `frontend/dist`. |

---

## 3. Pre-Deployment Safety Gates

| Safety Gate | Verification Command | Gate Result | Status |
| :--- | :--- | :--- | :---: |
| **1. Python Compilation** | `python -m compileall app/ tests/` | Zero syntax or bytecode errors | **PASSED** |
| **2. Backend Test Suite** | `pytest -v` | **40 / 40 passed** in 2.90s | **PASSED** |
| **3. Static Type Analysis** | `pyrefly check` | **0 type errors** | **PASSED** |
| **4. Frontend Linting** | `cd frontend && npm run lint` | ESLint clean (0 warnings, 0 errors) | **PASSED** |
| **5. Frontend Production Bundle** | `cd frontend && npm run build` | Built in 1.68s (dist/ 240 KB JS, 18.8 KB CSS) | **PASSED** |
| **6. Secret Leak Check** | `git ls-files \| grep -iE '\.env'` | Zero tracked `.env` or credential files | **PASSED** |
| **7. Reversibility & Diffs** | `git diff --stat` | Clean, modular commits; zero destructive edits | **PASSED** |

---

## 4. Production Smoke Tests (Live Verification)

Safe, low-volume verification was conducted against the live production Render API:

### Test 1: Production Health Check
- **Command:** `curl -s https://policy-pilot-nz.onrender.com/health`
- **HTTP Status:** `200 OK`
- **Response Body:** `{"status": "ok"}`
- **Verification:** Backend process is healthy, responsive, and serving traffic.

### Test 2: Production Statutory Q&A (`POST /ask`)
- **Query:** *"What does the Act say about freedom of expression?"*
- **Payload:** `{"question": "What does the Act say about freedom of expression?"}`
- **HTTP Status:** `200 OK`
- **Response Schema:**
  - `answer`: *"According to the legislation, everyone has the right to freedom of expression. This includes the freedom to seek, receive, and impart information and opinions of any kind in any form (section 14)."*
  - `citations`: `[{"section": "14", "heading": "Freedom of expression", "source_url": "https://www.legislation.govt.nz/act/public/1990/109/en/2022-08-30/sections/DLM225513/"}]`
  - `abstained`: `false`
- **Verification:** Production corpus is present, Gemini model responds with grounded text, and citation links point to official legislation.

### Test 3: Production Abstention & Validation
- **Query:** *"What does the Act say about te Tiriti o Waitangi or tax deductions?"*
- **HTTP Status:** `200 OK`
- **Response Schema:**
  - `answer`: *"I couldn't find enough supporting information in the retrieved legislation to answer that question confidently..."*
  - `citations`: `[]`
  - `abstained`: `true`
- **Verification:** Production API safely abstains on out-of-scope queries; zero hallucinations.

---

## 5. Rollback & Recovery Procedures

If a deployment failure or unexpected regression occurs post-release:
1. **Render Instant Rollback:** In Render Dashboard -> Web Service (`policy-pilot-nz`) -> **Deploys** -> Select previous working commit `d2091d9` -> Click **Rollback to this deploy**.
2. **Git Revert:** Run `git revert <commit-hash> -m 1 && git push origin main`.
3. **Local Safety:** Never force-push or delete commit history on `main`.

---

## 6. Manual Actions Still Required

1. **Push Changes to GitHub:** Stage, commit, and push the verified audit fixes, CI workflow, and configuration files to `origin/main`.
2. **Vercel Project Setup (If not already active):**
   - Connect Vercel to `https://github.com/Ganeshkusalkar/policy-pilot-nz`.
   - Ensure environment variable `VITE_API_BASE_URL` is set to `https://policy-pilot-nz.onrender.com`.
   - Confirm root directory is set to `frontend` or uses root `vercel.json`.
3. **Render Environment Configuration:**
   - Confirm in Render Dashboard that `GEMINI_API_KEY` is set in the Web Service environment variables.
   - Set `ALLOWED_ORIGINS` to `https://policy-pilot-nz.vercel.app,http://localhost:5173`.
