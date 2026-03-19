import os
import sys
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return str(project_root() / relative_path)


def asset_path(relative_path: str) -> str:
    return str(Path(resource_path(f"assets/{relative_path}")).resolve())


def asset_url(relative_path: str) -> str:
    # Stylesheets work best with forward slashes on Windows.
    return asset_path(relative_path).replace("\\", "/")
