from dataclasses import dataclass
from typing import Any, Dict, Optional, Set


ROLE_ADMIN = "admin"
ROLE_TPE_EMPLOYER = "tpe_employer"
ROLE_CASHPLUS_EMPLOYER = "cashplus_employer"

ALL_ROLES = {
    ROLE_ADMIN,
    ROLE_TPE_EMPLOYER,
    ROLE_CASHPLUS_EMPLOYER,
}


PERM_OPEN_ACCOUNT_REVIEW = "open_account_review"
PERM_OPEN_CLIENTS_REVIEW = "open_clients_review"
PERM_OPEN_CMI_TRANS = "open_cmi_trans"
PERM_OPEN_DAILY_BALANCE = "open_daily_balance"
PERM_OPEN_DAILY_ENTRY = "open_daily_entry"
PERM_OPEN_FACTURES = "open_factures"
PERM_OPEN_COMPANY_INFO = "open_company_info"
PERM_OPEN_USER_MANAGER = "open_user_manager"
PERM_RUN_BACKUP = "run_backup"


ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    ROLE_ADMIN: {
        PERM_OPEN_ACCOUNT_REVIEW,
        PERM_OPEN_CLIENTS_REVIEW,
        PERM_OPEN_CMI_TRANS,
        PERM_OPEN_DAILY_BALANCE,
        PERM_OPEN_DAILY_ENTRY,
        PERM_OPEN_FACTURES,
        PERM_OPEN_COMPANY_INFO,
        PERM_OPEN_USER_MANAGER,
        PERM_RUN_BACKUP,
    },
    ROLE_TPE_EMPLOYER: {
        PERM_OPEN_CMI_TRANS,
        PERM_OPEN_DAILY_ENTRY,
        PERM_RUN_BACKUP,
    },
    ROLE_CASHPLUS_EMPLOYER: {
        PERM_OPEN_DAILY_BALANCE,
        PERM_OPEN_DAILY_ENTRY,
        PERM_RUN_BACKUP,
    },
}


BUTTON_PERMISSIONS: Dict[str, str] = {
    "Button_AccountReview": PERM_OPEN_ACCOUNT_REVIEW,
    "Button_ClientsReview": PERM_OPEN_CLIENTS_REVIEW,
    "Button_CMITrans": PERM_OPEN_CMI_TRANS,
    "Button_DailyBalance": PERM_OPEN_DAILY_BALANCE,
    "Button_DailyEntry": PERM_OPEN_DAILY_ENTRY,
    "Button_Factures": PERM_OPEN_FACTURES,
    "InfoBtn": PERM_OPEN_COMPANY_INFO,
    "UserManagerBtn": PERM_OPEN_USER_MANAGER,
    "BackupBtn": PERM_RUN_BACKUP,
}


def normalize_role(role: Optional[str]) -> str:
    role_value = (role or "").strip().lower()

    if role_value in {ROLE_ADMIN, "full_access", "manager"}:
        return ROLE_ADMIN
    if role_value in {ROLE_TPE_EMPLOYER, "tpe_eployer", "tpe", "tpe_operations"}:
        return ROLE_TPE_EMPLOYER
    if role_value in {
        ROLE_CASHPLUS_EMPLOYER,
        "cashplus_eployer",
        "employer",
        "user",
        "",
    }:
        return ROLE_CASHPLUS_EMPLOYER
    return ROLE_CASHPLUS_EMPLOYER


def has_permission(role: Optional[str], permission: str) -> bool:
    normalized_role = normalize_role(role)
    return permission in ROLE_PERMISSIONS.get(normalized_role, set())


@dataclass(frozen=True)
class AuthenticatedUser:
    id: Optional[int]
    username: str
    role: str

    @classmethod
    def from_payload(cls, payload: Optional[Any]) -> "AuthenticatedUser":
        if isinstance(payload, AuthenticatedUser):
            return payload

        if isinstance(payload, dict):
            return cls(
                id=payload.get("id"),
                username=str(payload.get("username") or ""),
                role=normalize_role(payload.get("role")),
            )

        return cls(id=None, username="", role=ROLE_CASHPLUS_EMPLOYER)
