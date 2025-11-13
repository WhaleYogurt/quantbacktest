# Continuous Integration

quantbacktest ships with a GitHub Actions workflow (`.github/workflows/ci.yml`) that enforces code quality and regression testing on every push/pull request.

## Jobs

1. **lint (Ubuntu)**
   - Installs the package with `pip install -e .[dev]`.
   - Runs `ruff check .` for style/lint violations.
   - Runs `mypy quantbacktest` for static type checking.

2. **tests (Windows)**
   - Installs the package in editable mode.
   - Executes `python -m pytest`.
   - Executes `test.bat`, which in turn runs the example suite, engine diagnostics, and profiler, ensuring the same coverage developers rely on locally.

## Local Parity

Before opening a pull request, run:

```bash
ruff check .
mypy quantbacktest
python -m pytest
test.bat
```

This mirrors the CI workflow so failures are caught early. See `docs/examples.md` for the scripts `test.bat` executes automatically.
