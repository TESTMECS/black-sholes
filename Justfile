streamlit:
  streamlit run app.py
flask:
  uv run flask_app.py
test:
  pytest tests/
lint:
  ruff check 
tsc:
  mypy . 

