import os
import tempfile
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from admin_license_tool.license_generator import issue_license
from services.license.license_service import get_request_code, import_license_blob, validate_current_license


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["KONACH_LICENSE_DIR"] = tmp

        request_code = get_request_code()
        _, blob = issue_license(
            request_code=request_code,
            customer="smoke-test",
            days=30,
            status="active",
            private_key_path=Path("keys/private_key.pem"),
            expected_public_key_path=Path("config/license_public_key.pem"),
            out_path=Path(tmp) / "license.json",
        )
        import_license_blob(blob)
        result = validate_current_license()
        if not result.is_valid:
            raise RuntimeError(f"Validation failed: {result.reason}")

    print("license_smoke_test_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
