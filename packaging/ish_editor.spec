from pathlib import Path
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


project_root = Path(SPECPATH).parent
datas = [
    (str(project_root / "editor" / "ui" / "dist"), "editor/ui/dist"),
    *collect_data_files("keyring"),
]
hiddenimports = sorted(
    set(
        collect_submodules("keyring.backends")
        + collect_submodules("PIL")
        + collect_submodules("uvicorn")
        + ["scripts.build_site", "scripts.validate_site"]
    )
)

analysis = Analysis(
    [str(project_root / "packaging" / "entrypoint.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest"],
    noarchive=False,
)
pyz = PYZ(analysis.pure)
executable = EXE(
    pyz,
    analysis.scripts,
    analysis.binaries,
    analysis.datas,
    [],
    name="ISH-Editor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

if sys.platform == "darwin":
    app = BUNDLE(
        executable,
        name="ISH-Editor.app",
        bundle_identifier="org.hantavirussociety.editor",
        info_plist={
            "CFBundleDisplayName": "ISH Editor",
            "CFBundleName": "ISH Editor",
            "NSHighResolutionCapable": True,
        },
    )
