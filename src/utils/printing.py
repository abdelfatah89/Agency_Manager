import os
import subprocess
import sys


def open_pdf_file(pdf_path: str) -> bool:
    """Open a PDF with the system default viewer."""
    if not pdf_path or not os.path.exists(pdf_path):
        return False

    try:
        if sys.platform.startswith("win"):
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", pdf_path])
        else:
            subprocess.Popen(["xdg-open", pdf_path])
        return True
    except Exception:
        return False
