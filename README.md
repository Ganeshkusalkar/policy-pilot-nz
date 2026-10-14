# PolicyPilot NZ

**A retrieval-augmented generation (RAG) prototype for exploring New Zealand legislation with evidence-linked answers.**

PolicyPilot NZ retrieves passages from an ingested version of the **New Zealand Bill of Rights Act 1990**, asks Google Gemini to answer using that evidence, and validates the supporting section labels before returning citations. If the evidence or citation labels are insufficient, the service abstains instead of presenting an unsupported answer.

> **Important:** This is a learning and portfolio project, not a legal advice service. Answers can be incomplete or wrong. Check the official legislation and consult a qualified legal professional for advice.

## Features

- Ingest and process official legislation XML into provision-aware text chunks.
- Keyword retrieval with BM25.
- Semantic retrieval using `sentence-transformers/all-MiniLM-L6-v2`.
- Hybrid retrieval combining BM25 and semantic rankings with Reciprocal Rank Fusion (RRF).
- FastAPI question-answering endpoint powered by Gemini.
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

- Python
- FastAPI and Uvicorn
- Google Gen AI SDK (`google-genai`)
- BM25 keyword retrieval (`rank-bm25`)
- Sentence Transformers and PyTorch for semantic retrieval
- NumPy
- pytest and HTTPX for testing

## Legislation source

The current corpus is based on the **New Zealand Bill of Rights Act 1990**, using this versioned official XML source:

[Official legislation XML — version dated 30 August 2022](https://www.legislation.govt.nz/act/public/1990/109/en/2022-08-30.xml)

The ingestion scripts and local corpus files are separate from the code. Downloaded or processed legislation data may be excluded from Git, so follow the ingestion steps below to recreate it. Verify the current legal status and applicable version independently before relying on any content.

## Setup (Windows PowerShell)

### 1. Create and activate a virtual environment

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If PowerShell blocks activation, use your normal Python environment activation policy or run the virtual environment's Python executable directly.

### 2. Install dependencies

Install the project dependencies listed in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

Semantic retrieval also requires `sentence-transformers` and its PyTorch/NumPy dependencies; Gemini answering requires `google-genai`. Ensure these are included in `requirements.txt` before relying on a fresh environment. A project dependency manifest should be the source of truth for reproducible installs.

### 3. Configure environment variables

Create a local `.env` file in the repository root. Do not commit this file or share its API keys.

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_available_gemini_model
LEGISLATION_API_KEY=your_legislation_api_key
```

`GEMINI_API_KEY` is required for generated answers. `GEMINI_MODEL` defaults in code to `gemini-3.8-flash`; configure a model identifier available to your Gemini account. `LEGISLATION_API_KEY` is used by the legislation-fetching workflow when required.

### 4. Fetch and process the legislation corpus

The scripts are designed to be run as Python modules from the repository root:

```powershell
python -m scripts.fetch_legislation
python -m scripts.process_legislation
```

Review `scripts/fetch_legislation.py` and `scripts/process_legislation.py` if you need to confirm available options or expected output paths. The question-answering service expects the processed corpus at:

```text
data/processed/new-zealand-bill-of-rights-act-1990.jsonl
```

### 5. Start the API

```powershell
python -m uvicorn app.main:app --reload
```

- API documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

The root path `/` is not necessarily defined. Use `/docs` to explore the API and `/ask` to submit questions.

## API usage

### `POST /ask`

Request:

```json
{
  "question": "What protection does the Act provide against arbitrary arrest or detention?"
}
```

PowerShell example:

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

The response includes an answer, citations, and an `abstained` flag. A successful answer should include links to the supporting official section pages. Exact answer text and retrieved sections can vary.

Example response shape (illustrative):

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

- `200`: the question was processed; the answer may either be supported or an abstention.
- `422`: request validation failed, such as a question shorter than 3 characters or longer than 1,000 characters.
- `503`: required answer-service configuration or corpus is unavailable, or Gemini cannot complete the request.

An HTTP `200` response does **not** by itself mean the answer is legally correct.

## Retrieval evaluation

The current local evaluation set contains **25 questions** with expected section labels. Previously observed results:

| Retrieval method | Recall@3 | MRR | Average query time |
|---|---:|---:|---:|
| BM25 | 1.000 | 1.000 | Not recorded here |
| Semantic (`all-MiniLM-L6-v2`) | 1.000 | 0.953 | 25.56 ms |
| Hybrid (BM25 + semantic RRF) | 1.000 | 0.980 | 28.70 ms |

These are results from the project's current small evaluation set and local environment, not a broad benchmark. Timing depends on hardware, model warm-up, and runtime conditions. Recall@3 measures whether the expected section appears in the top three results; MRR rewards the expected result appearing nearer the top. High retrieval scores do not establish answer correctness, citation entailment, or legal reliability.

Re-run the evaluations from the repository root:

```powershell
python -m scripts.evaluate_retrieval
python -m scripts.evaluate_semantic
python -m scripts.evaluate_hybrid
```

Semantic retrieval downloads/loads the embedding model as needed and may take longer on the first run.

## Tests

Run the automated test suite:

```powershell
python -m pytest -q
```

At the latest recorded checkpoint, **31 tests passed**. Run the command again after changes to verify the current checkout.

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
- Validating a section label confirms that it was retrieved, not that it truly entails every claim in the generated answer.
- Model output and retrieval can fail; abstention is a safeguard, not a guarantee.
- The current evaluation set is small and does not measure all aspects of legal answer quality.
- This project is not legal advice and should not be used as the sole basis for legal decisions.

Potential improvements include broader legislation coverage, stronger citation-entailment evaluation, version-aware corpus management, more adversarial tests, and a configurable retrieval strategy for the API.

## License

Add a project license before redistributing this repository. Check the applicable terms for source legislation and third-party dependencies separately.
