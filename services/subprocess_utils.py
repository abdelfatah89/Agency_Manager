import subprocess
import sys
from typing import Any, Sequence


def run_hidden_subprocess(cmd: Sequence[str], **kwargs: Any) -> subprocess.CompletedProcess:
    """Run subprocess commands without flashing a console window on Windows."""
    run_kwargs = dict(kwargs)
    if sys.platform.startswith("win"):
        # Windows-only flag to prevent console window flashing.
        run_kwargs["creationflags"] = int(run_kwargs.get("creationflags", 0)) | int(subprocess.CREATE_NO_WINDOW)
        startupinfo = run_kwargs.get("startupinfo")
        if startupinfo is None:
            startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        run_kwargs["startupinfo"] = startupinfo
    return subprocess.run(cmd, **run_kwargs)
