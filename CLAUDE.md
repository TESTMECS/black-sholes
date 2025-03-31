# Black-Scholes Project Development Guide

## Commands
- **Run app with Streamlit**: `streamlit run app.py`
- **Run app with Flask**: `python flask_app.py`
- **Install dependencies**: `pip install -r requirements.txt`
- **Run tests**: `pytest`
- **Run specific test file**: `pytest test_black_scholes.py`
- **Run single test**: `pytest test_black_scholes.py::TestBlackScholes::test_put_call_parity`
- **Lint code**: `ruff check .`
- **Format code**: `black .`
- **Type checking**: `mypy .`

## Code Style Guidelines
- **Imports**: Group imports: stdlib → third-party → local modules, sorted alphabetically within groups
- **Formatting**: Use Black formatting, max line length 88 chars
- **Types**: Include type hints for function parameters and return values
- **Docstrings**: Use NumPy style docstrings for functions and classes
- **Naming**: Use snake_case for variables/functions, PascalCase for classes
- **Error handling**: Use try/except for expected failures, raise ValueError with descriptive messages
- **Streamlit**: Use st.columns for layout, st.markdown for text, px for interactive charts

## Project Structure
- **black_scholes.py**: Core pricing functions
- **app.py**: Streamlit UI application
- **flask_app.py**: Flask server wrapper

# Next Items TODO:
- [ ] Add tests to ensure mathmatical correctness of the Black-Scholes model
- [ ] Add a "CALCULATE" button where the user calculates the put and the call price.
- [ ] This "CALCULATE" button will store the values in an in-memory sqlite database.
- The tables for the database are pictured in "table1.png" and "table2.png"
