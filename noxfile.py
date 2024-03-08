import itertools
import pathlib

import nox


def _install_dev_deps(session: nox.Session) -> None:
    session.install("-r", "dev-requirements.txt")


def _to_txt(path: pathlib.Path, /) -> pathlib.Path:
    return path.with_name(path.name[:-3] + ".txt")



_REQUIREMENTS_IN_FILES = [pathlib.Path("./requirements.in"), pathlib.Path("./dev-requirements.in")]
_REQUIREMENTS_FILES = [_to_txt(path) for path in _REQUIREMENTS_IN_FILES]


@nox.session(name="freeze-locks", reuse_venv=True)
def freeze_locks(session: nox.Session) -> None:
    """Freeze the dependency locks."""
    _install_dev_deps(session)

    for path in _REQUIREMENTS_IN_FILES:
        target = _to_txt(path)
        target.unlink(missing_ok=True)
        session.run(
            "pip-compile-cross-platform",
            "-o",
            str(target),
            "--min-python-version",
            "3.8",
            str(path),
        )


@nox.session(name="verify-locks", reuse_venv=True)
def verify_locks(session: nox.Session) -> None:
    """Verify the dependency locks by installing them."""
    for path in _REQUIREMENTS_FILES:
        session.install("--dry-run", "-r", str(path.relative_to(path.parent)))

