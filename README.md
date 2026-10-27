# PolicyPilot NZ

**A retrieval-augmented generation (RAG) prototype for exploring New Zealand legislation with evidence-linked answers.**

PolicyPilot NZ retrieves passages from an ingested version of the **New Zealand Bill of Rights Act 1990**, uses Google Gemini to generate answers grounded in that evidence, and validates supporting section labels before returning citations. If the evidence or citation labels are insufficient, the service abstains rather than presenting an unsupported answer.

> **Important:** This is a learning and portfolio project, not a legal advice service. Answers can be incomplete or wrong. Check the official legislation and consult a qualified legal professional for advice.

## Features

- Ingest and process official legislation XML into provision-aware text chunks.
- Keyword retrieval using BM25.
- Semantic retrieval using `sentence-transformers/all-MiniLM-L6-v2`.
- Hybrid retrieval combining BM25 and semantic rankings with Reciprocal Rank Fusion (RRF).
- FastAPI question-answering endpoint powered by Google Gemini.
- Validated section labels and links to version-specific official legislation pages.
- Abstention when retrieved evidence or supporting-section labels are inadequate.
- Automated tests and retrieval evaluation scripts.

**Current API note:** The question-answering service in `app/services/qa_service.py` currently uses BM25. Semantic and hybrid retrieval are separate implementations evaluated by scripts; they are not automatically used by `/ask`.

## Architecture

```text
Official NZ legislation XML
          |
          v
   XML parser and processor
          |
          v
 Provision-aware text chunks
          |
          +-------------------+
          |                   |
          v                   v
      BM25 index        Semantic embeddings
          |                   |
          |                   v
          |              Semantic ranking
          |                   |
          +--------+----------+
                   |
             Hybrid RRF
          (evaluation path)

Question --> BM25 retrieval --> Evidence-grounded Gemini answer
                                      |
                                      v
                         Validate supporting sections
                                      |
                         +------------+------------+
                         |                         |
                    Valid citations           Insufficient or
                         |                    invalid support
                         v                         v
                 Answer + source links          Abstention
```

## Technology

- Python 3.12
- FastAPI and Uvicorn
- Google Gen AI SDK (`google-genai`)
- BM25 keyword retrieval (`rank-bm25`)
- Sentence Transformers and PyTorch for semantic retrieval
- NumPy
- pytest and HTTPX for testing
- python-dotenv for environment configuration

## Legislation source

The current corpus is based on the **New Zealand Bill of Rights Act 1990**, using this pinned version of the official XML source:

[Official legislation XML — version dated 30 August 2022](https://www.legislation.govt.nz/act/public/1990/109/en/2022-08-30.xml)

The downloaded XML and processed corpus are local data files and may be excluded from Git. Follow the ingestion instructions below to recreate them.

The application uses a specific legislation version. Verify the current legal status and applicable version independently before relying on any content.

## Setup (Windows PowerShell)

### 1. Clone the repository

Clone the repository and navigate into its root directory:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd policy-pilot-nz
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your actual repository URL. If you already have the project locally, continue from its root directory.

### 2. Create and activate a virtual environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell blocks activation, use your normal Python environment activation policy or run the virtual environment's Python executable directly.

### 3. Install dependencies

Install the project's direct dependencies:

```powershell
python -m pip install -r requirements.txt
```

Check for dependency conflicts:

```powershell
python -m pip check
```

The dependency file includes the packages required for the API, Gemini integration, BM25 retrieval, semantic retrieval, and testing. Semantic retrieval may download its embedding model the first time it runs.

### 4. Configure environment variables

Create a local `.env` file in the repository root. Do not commit this file or share its API keys.

Example `.env`:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_available_gemini_model
LEGISLATION_API_KEY=your_legislation_api_key
```

- `GEMINI_API_KEY` is required for generated answers.
- `GEMINI_MODEL` specifies the Gemini model identifier available to your account. The application has a default configured in `app/config.py`.
- `LEGISLATION_API_KEY` is used by the legislation-fetching workflow when required.

Use your own valid API credentials. Never put real keys in source code, README files, screenshots, or Git commits.

### 5. Fetch and process the legislation corpus

Run the scripts as Python modules from the repository root:

```powershell
python -m scripts.fetch_legislation
python -m scripts.process_legislation
```

The fetching script uses the legislation API configuration and may require a valid API key. Check `scripts/fetch_legislation.py` for the available options and expected output paths.

The question-answering service expects the processed corpus at:

```text
data/processed/new-zealand-bill-of-rights-act-1990.jsonl
```

The raw XML and processed JSONL files are local data and may not be included in the Git repository. Recreate them using the ingestion scripts before starting the API in a fresh environment.

### 6. Run the tests

```powershell
python -m pytest -q
```

The latest recorded project checkpoint had 31 passing tests. Run the test command again after making changes to verify the current checkout.

### 7. Start the API

```powershell
python -m uvicorn app.main:app --reload
```

Open these URLs in your browser:

- Interactive API documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

The root path `/` is not necessarily defined. Use `/docs` to explore the API and `/ask` to submit questions.

## API usage

### `POST /ask`

Example request:

```json
{
  "question": "What protection does the Act provide against arbitrary arrest or detention?"
}
```

### PowerShell example

With the API running in another terminal:

```powershell
$body = @{
    question = "What protection does the Act provide against arbitrary arrest or detention?"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/ask" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

The response includes an answer, citations, and an `abstained` flag. Exact answer text and retrieved sections can vary.

### Illustrative response

```json
{
  "answer": "The Act protects against arbitrary arrest or detention. Supporting legal information is set out in the cited section.",
  "citations": [
    {
      "section": "22",
      "heading": "Liberty of the person",
      "source_url": "https://www.legislation.govt.nz/act/public/1990/109/en/2022-08-30/sections/DLM225524/"
    }
  ],
  "abstained": false
}
```

This example illustrates the response structure, not a guarantee of a particular generated answer.

### Response behaviour

- `200`: The question was processed. The answer may be supported or may be an abstention.
- `422`: Request validation failed, such as a question shorter than 3 characters or longer than 1,000 characters.
- `503`: Required configuration or corpus is unavailable, or the Gemini service cannot complete the request.

An HTTP `200` response does **not** by itself mean the answer is legally correct.

## Retrieval evaluation

The current local evaluation set contains **25 questions** with expected section labels. Previously observed results:

| Retrieval method | Recall@3 | MRR | Average query time |
|---|---:|---:|---:|
| BM25 | 1.000 | 1.000 | Not recorded |
| Semantic (`all-MiniLM-L6-v2`) | 1.000 | 0.953 | 25.56 ms |
| Hybrid (BM25 + semantic RRF) | 1.000 | 0.980 | 28.70 ms |

These results come from the project's small evaluation set and local environment; they are not a broad benchmark. Timing depends on hardware, model warm-up, and runtime conditions.

- **Recall@3** measures whether the expected section appears among the top three results.
- **MRR (Mean Reciprocal Rank)** rewards the expected result appearing closer to the top.

High retrieval scores do not establish answer correctness, citation entailment, or legal reliability.

Re-run the evaluations from the repository root:

```powershell
python -m scripts.evaluate_retrieval
python -m scripts.evaluate_semantic
python -m scripts.evaluate_hybrid
```

Semantic retrieval may download or load the embedding model on its first run and can take longer initially.

## Tests

Run the automated test suite:

```powershell
python -m pytest -q
```

The tests cover API behaviour, configuration, QA service behaviour, XML parsing, chunking, and retrieval-related functionality.

Run the tests after making changes. Passing tests indicate that the tested behaviour works; they do not guarantee that every generated answer is factually or legally correct.

## Repository map

```text
app/
  api/          FastAPI endpoints and request/response models
  ingestion/    XML parsing and provision-aware chunking
  retrieval/    BM25, semantic, and hybrid retrieval
  services/     Gemini-backed QA and citation validation
  config.py     Environment-based settings
  main.py       FastAPI application

scripts/
  fetch_legislation.py
  process_legislation.py
  query_legislation.py
  evaluate_retrieval.py
  query_semantic.py
  evaluate_semantic.py
  evaluate_hybrid.py

tests/          Automated tests
data/           Local source and processed corpus files
```

## Known limitations and next steps

- The corpus currently covers one Act and one pinned version, not all New Zealand legislation.
- The `/ask` service currently uses BM25; semantic and hybrid retrieval are evaluated separately.
- Validating a section label confirms that it was retrieved, not that it entails every claim in the generated answer.
- Retrieval and model generation can fail; abstention is a safeguard, not a guarantee.
- The evaluation set is small and does not measure all aspects of legal answer quality.
- The project is not legal advice and should not be used as the sole basis for legal decisions.

Potential improvements include broader legislation coverage, stronger citation-entailment evaluation, version-aware corpus management, more adversarial tests, a configurable retrieval strategy for the API, and evaluation against a larger set of questions.

## Deployment (Render & Vercel)

### Backend Deployment (Render)
1. Create a new **Web Service** on Render connected to this repository.
2. Configure settings:
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && python scripts/process_legislation.py` *(ensures corpus is generated)*
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Configure Environment Variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `GEMINI_MODEL`: `gemini-3.5-flash-lite` (or desired model).
   - `ALLOWED_ORIGINS`: `https://policy-pilot-nz.vercel.app,http://localhost:5173`

### Frontend Deployment (Vercel)
1. Import the repository on Vercel.
2. Configure project settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Configure Environment Variables:
   - `VITE_API_BASE_URL`: `https://policy-pilot-nz.onrender.com`

## License

No project license has been added yet. Before redistributing this repository, choose and add an appropriate license. Check the applicable terms for the source legislation and third-party dependencies separately.
