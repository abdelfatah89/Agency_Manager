from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def asset_path(relative_path: str) -> str:
    return str((project_root() / "assets" / relative_path).resolve())


def asset_url(relative_path: str) -> str:
    # Stylesheets work best with forward slashes on Windows.
    return asset_path(relative_path).replace("\\", "/")
