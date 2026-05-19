# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Interview preparation repository covering Python and SQL/PostgreSQL theory (`Text_Docs/`) alongside practical coding exercises (`Coding/`).

## Running Tests

Tests live in `Coding/tests/` and are configured via `Coding/pytest.ini`:

```bash
# Run all tests from the Coding directory
cd Coding && pytest

# Run a specific test file
cd Coding && pytest tests/test_example.py

# Run a single test by name
cd Coding && pytest tests/test_example.py::test_add
```

The `pytest.ini` sets `testpaths = tests`, so pytest must be invoked from `Coding/`, not the repo root.

## Virtual Environment

The repo uses `.venv` at the project root:

```bash
source .venv/bin/activate
```

## Repository Structure

```
Coding/          # Python coding exercises and scratch files
  tests/         # pytest test files (test_*.py convention)
  pytest.ini     # pytest config — testpaths=tests, -v --tb=short
  basics.py      # Python fundamentals: decorators, iterators, context managers, asyncio
  async_impl.py  # Manual event loop built with generators + select(), socket-based server
  generator.py   # Generator-based cooperative multitasking demo
  algo_prep.py   # LeetCode solutions (greedy algorithms etc.)
  t_bank_internship.py  # Competitive programming tasks
  final_sobes_sber.py   # Sber interview prep scratch file

Text_Docs/       # Markdown theory notes for interviews
  python_theory.md   # Python internals, concurrency, OOP, GIL, etc.
  README.md          # SQL/PostgreSQL theory (30+ questions)

claude_code_practice/  # Claude Code experiments (currently empty)
```

## Key Patterns

- Python files in `Coding/` are **standalone scripts**, not importable modules — they run top-level code and use `breakpoint()` for debugging. Don't extract them into packages unless explicitly asked.
- The `async_impl.py` intentionally reimplements async I/O primitives from scratch using `select()` and generators — this is educational, not production code.
- Tests in `test_example.py` deliberately contain failing assertions — they are exercises for learning pytest output formats, not a passing test suite.
- Commit messages follow the pattern: `Category: description in Russian` (e.g., `Training:`, `Feature:`, `Refactor:`).
