# SLR Parser Studio

SLR Parser Studio is an interactive compiler design tool that takes a context-free grammar and walks through the full SLR(1) workflow. It validates the grammar, computes FIRST/FOLLOW sets, builds the LR(0) DFA, generates the SLR parsing table, traces input string parsing, and exports a PDF report.

## What this project does
- Parse and validate a CFG in a simple text format
- Augment the grammar and enumerate productions
- Compute FIRST and FOLLOW sets
- Build the LR(0) canonical collection and DFA transitions
- Generate the SLR(1) parsing table and detect conflicts
- Parse an input string using the generated table
- Export a PDF report (preview or download)

## Project layout
- backend: Flask API for all SLR operations
- frontend: Single-page HTML UI (no build step)

## Requirements
- Python 3.9+ recommended
- pip

## Local setup

### 1) Create and activate a virtual environment

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Start the backend API
```powershell
python backend\main.py
```

The API listens on http://127.0.0.1:5000 by default. The frontend is configured to call this base URL.

### 4) Open the frontend
Option A: Open the file directly
- Open frontend/index.html in your browser

Option B: Serve it locally (recommended)
```powershell
Set-Location frontend
python -m http.server 5500
```
Then open http://127.0.0.1:5500 in your browser.

If you need a different API host or port, update the constant in frontend/index.html:
- const API_URL = 'http://127.0.0.1:5000/api';

## Grammar format
- One production per line
- Use -> between LHS and RHS
- Use | for alternatives
- Tokens can be space-separated or concatenated

Example:
```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

Notes:
- The parser recognizes a literal epsilon symbol if you include it in your grammar for empty productions.
- The first non-terminal is treated as the start symbol.

## API endpoints
Base URL: http://127.0.0.1:5000/api

All endpoints accept JSON and return JSON unless noted.

- POST /parse-grammar
  - body: { "grammar": "..." }
  - response: grammar, terminals, non_terminals

- POST /augment-grammar
  - body: { "grammar": "..." }
  - response: augmented_grammar, productions

- POST /compute-first-follow
  - body: { "grammar": "..." }
  - response: first_sets, follow_sets

- POST /build-dfa
  - body: { "grammar": "..." }
  - response: states, transitions, num_states

- POST /generate-dfa-diagram
  - body: { "grammar": "..." }
  - response: diagram (base64 PNG)

- POST /build-parsing-table
  - body: { "grammar": "..." }
  - response: parsing_table, conflicts, is_slr1

- POST /parse-string
  - body: { "grammar": "...", "input_string": "..." }
  - response: success, steps, message

- POST /generate-pdf-preview
  - body: { "grammar": "...", "input_string": "..." }
  - response: pdf_base64

- POST /export-pdf
  - body: { "grammar": "...", "input_string": "..." }
  - response: PDF file download

## Example curl
```bash
curl -X POST http://127.0.0.1:5000/api/parse-grammar \
  -H "Content-Type: application/json" \
  -d "{\"grammar\": \"E -> E + T | T\\nT -> T * F | F\\nF -> ( E ) | id\"}"
```


