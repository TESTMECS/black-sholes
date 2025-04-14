streamlit:
  streamlit run streamlit_app.py
test:
  pytest tests/
lint:
  ruff check
tsc:
  mypy .
runapp:
  uvicorn api.fastapi_app:app --reload
testall:
  pytest
