import json
from pathlib import Path
from typing import Dict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPANY_INFO_PATH = PROJECT_ROOT / "config" / "company_info.json"

DEFAULT_COMPANY_INFO: Dict[str, str] = {
    "company_name": "STE VISA SERVICES EXPESSES SAR",
    "phone": "0123 45 67 89",
    "address": "123 شارع الرئيسي، الجزائر العاصمة",
    "ice": "123 456 789",
    "if_code": "06994700",
    "rc": "2241",
}


def _ensure_parent_dir() -> None:
    COMPANY_INFO_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_company_info() -> Dict[str, str]:
    if not COMPANY_INFO_PATH.exists():
        return DEFAULT_COMPANY_INFO.copy()

    try:
        data = json.loads(COMPANY_INFO_PATH.read_text(encoding="utf-8"))
        result = DEFAULT_COMPANY_INFO.copy()
        for key in result.keys():
            value = data.get(key)
            if value is not None:
                result[key] = str(value)
        return result
    except Exception:
        return DEFAULT_COMPANY_INFO.copy()


def save_company_info(data: Dict[str, str]) -> None:
    _ensure_parent_dir()
    payload = DEFAULT_COMPANY_INFO.copy()
    for key in payload.keys():
        payload[key] = str(data.get(key, payload[key])).strip()
    COMPANY_INFO_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def to_invoice_context(data: Dict[str, str]) -> Dict[str, str]:
    return {
        "company_name": data.get("company_name", DEFAULT_COMPANY_INFO["company_name"]),
        "adresse": data.get("address", DEFAULT_COMPANY_INFO["address"]),
        "telephone": data.get("phone", DEFAULT_COMPANY_INFO["phone"]),
        "num_rc": data.get("rc", DEFAULT_COMPANY_INFO["rc"]),
        "ste_ICE": data.get("ice", DEFAULT_COMPANY_INFO["ice"]),
        "if_code": data.get("if_code", DEFAULT_COMPANY_INFO["if_code"]),
    }