# Legacy — transaction profiler demo

A separate, older proof of concept (Streamlit + LangGraph agent over transaction
data) that predates the marketplace POC in this repository. It is **not**
related to the Search & Vector marketplace demo — different collections,
different dependencies, different architecture.

Kept here for reference only. See `architecture.pdf` / `architecture.html` for
its own diagram.

## Run (standalone)

```bash
cd legacy-profiler-demo
pip install -r requirements.txt
streamlit run app.py
```

Requires its own `MONGODB_URI` / `DB_NAME` env vars pointing at a transactions
dataset, separate from the marketplace POC's `.env`.
