# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

project_root = Path.cwd()


def _data_tuple(path: str, target: str):
    return (str(project_root / path), target)


datas = [
    _data_tuple("assets", "assets"),
    _data_tuple("src", "src"),
    _data_tuple("theme", "theme"),
    _data_tuple("services", "services"),
    _data_tuple("sql", "sql"),
    _data_tuple("deployment/windows/scripts", "deployment/windows/scripts"),
    _data_tuple(".env.example", "."),
    _data_tuple("config/license_public_key.pem", "config"),
    _data_tuple("resource.qrc", "."),
]

hiddenimports = [
    "sqlalchemy",
    "sqlalchemy.orm",
    "sqlalchemy.sql",
    "pymysql",
    "dotenv",
    "jinja2",
    "weasyprint",
    "PyQt5.QtSvg",
]
hiddenimports += collect_submodules("src")
hiddenimports += collect_submodules("services")

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    [],
    name="KONACH",
    exclude_binaries=True,
    icon=str(project_root / "assets" / "icons" / "exe_icon.ico"),
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="KONACH",
)
