# Lessons

## 2026-05-16

- A newborn research repository can still have strong intent. When the code
  tree is empty, the correct first artifact is a source-backed orientation
  scaffold, not premature implementation.
- In this project, "autarkic" has two coupled meanings that must remain joined:
  formal self-confidence and embodied control of the computational substrate.
- When one repo log points to adjacent implementation work, verify the public
  branch before treating it as current. In this case, SJAS describes newer
  Proflog work than public `jpt4/proflog` exposes on `main`.
- For this repo's standard-library Python tests, keep `tests/__init__.py` so
  plain `python -m unittest discover` finds the suite from the repository root.
