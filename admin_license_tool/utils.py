import sys
from pathlib import Path


def runtime_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resolve_existing_path(path_value: Path, label: str) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        if candidate.exists():
            return candidate
        raise ValueError(f"{label} file not found: {candidate}")

    base = runtime_base_dir()
    candidates = [
        Path.cwd() / candidate,
        base / candidate,
        base.parent / candidate,
    ]
    for item in candidates:
        if item.exists():
            return item

    searched = "\n".join(str(x) for x in candidates)
    raise ValueError(f"{label} file not found: {candidate}\nSearched:\n{searched}")
