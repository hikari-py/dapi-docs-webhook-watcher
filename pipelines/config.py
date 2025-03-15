from __future__ import annotations

import pathlib

SCRIPT_NAME = "runner.py"
PYPROJECT_TOML = "pyproject.toml"

# Reformatting paths
REFORMATTING_FILE_EXTS = {
    ".py",
    ".pyx",
    ".pyi",
    ".c",
    ".cpp",
    ".cxx",
    ".hpp",
    ".hxx",
    ".h",
    ".yml",
    ".yaml",
    ".html",
    ".htm",
    ".js",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".css",
    ".md",
    ".dockerfile",
    "Dockerfile",
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    ".dockerignore",
    ".flake8",
    ".txt",
    ".sh",
    ".bat",
    ".ps1",
    ".rb",
    ".pl",
}

PYTHON_REFORMATTING_PATHS = (SCRIPT_NAME, "pipelines", "noxfile.py")

FULL_REFORMATTING_PATHS = (
    *PYTHON_REFORMATTING_PATHS,
    *(f for f in pathlib.Path().glob("*") if f.is_file() and f.suffix in REFORMATTING_FILE_EXTS),
    ".github",
    "docs",
    "changes",
)
