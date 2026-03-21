import hashlib
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass
from typing import Dict

from services.subprocess_utils import run_hidden_subprocess


logger = logging.getLogger(__name__)

_HWID_SALT_ENV = "KONACH_HWID_SALT"
_DEFAULT_HWID_SALT = "konach-hwid-v1"


@dataclass(frozen=True)
class MachineIdentity:
    bios_uuid: str
    disk_serial: str
    windows_machine_guid: str
    mac_address: str
    machine_name: str


def _normalize(value: str) -> str:
    cleaned = (value or "").strip().lower()
    return re.sub(r"[^a-z0-9]", "", cleaned)


def _run_powershell(command: str, timeout: int = 8) -> str:
    try:
        completed = run_hidden_subprocess(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                command,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0:
            return ""
        return completed.stdout.strip()
    except Exception:
        logger.exception("PowerShell command failed while collecting fingerprint data")
        return ""


def _read_bios_uuid() -> str:
    return _normalize(_run_powershell("(Get-CimInstance Win32_ComputerSystemProduct).UUID"))


def _read_disk_serial() -> str:
    cmd = (
        "$disk = Get-CimInstance Win32_DiskDrive | "
        "Sort-Object DeviceID | Select-Object -First 1 -ExpandProperty SerialNumber;"
        "if ($disk) { $disk }"
    )
    return _normalize(_run_powershell(cmd))


def _read_windows_machine_guid() -> str:
    cmd = "(Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Cryptography' -Name MachineGuid).MachineGuid"
    return _normalize(_run_powershell(cmd))


def _read_mac_address() -> str:
    return _normalize(f"{uuid.getnode():012x}")


def collect_machine_identity() -> MachineIdentity:
    identity = MachineIdentity(
        bios_uuid=_read_bios_uuid(),
        disk_serial=_read_disk_serial(),
        windows_machine_guid=_read_windows_machine_guid(),
        mac_address=_read_mac_address(),
        machine_name=_normalize(os.environ.get("COMPUTERNAME", "unknown")),
    )
    return identity


def build_machine_fingerprint(identity: MachineIdentity) -> str:
    # Deterministic fingerprint with salt; missing values are normalized to "na".
    payload = {
        "bios_uuid": identity.bios_uuid or "na",
        "disk_serial": identity.disk_serial or "na",
        "windows_machine_guid": identity.windows_machine_guid or "na",
        "mac_address": identity.mac_address or "na",
        "machine_name": identity.machine_name or "na",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    salt = os.getenv(_HWID_SALT_ENV, _DEFAULT_HWID_SALT)
    raw = f"{canonical}|{salt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def collect_machine_fingerprint_payload() -> Dict[str, str]:
    identity = collect_machine_identity()
    return {
        "bios_uuid": identity.bios_uuid,
        "disk_serial": identity.disk_serial,
        "windows_machine_guid": identity.windows_machine_guid,
        "mac_address": identity.mac_address,
        "machine_name": identity.machine_name,
        "hardware_fingerprint": build_machine_fingerprint(identity),
    }
