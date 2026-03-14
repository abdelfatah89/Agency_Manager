import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.db_services.backup_service import run_backup_now


def main() -> int:
    ok, path, message = run_backup_now(reason="manual-script")
    if ok:
        print(f"[Backup] {message}: {path}")
        return 0

    print(f"[Backup] {message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())