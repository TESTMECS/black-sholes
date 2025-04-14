streamlit:
  streamlit run streamlit_app.py
test:
  pytest tests/
lint:
  ruff check
tsc:
  mypy .
runapp:
  uv run app_fastapi.py
testall:
  pytest