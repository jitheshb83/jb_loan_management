# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for building the Housing Loan Manager macOS app bundle."""

from PyInstaller.utils.hooks import collect_all

block_cipher = None

datas = []
binaries = []
hiddenimports = []

for pkg in ("pyqtgraph", "PySide6"):
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hiddenimports

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="HousingLoanManager",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="HousingLoanManager",
)

app = BUNDLE(
    coll,
    name="Housing Loan Manager.app",
    icon="assets/AppIcon.icns",
    bundle_identifier="com.jithesh.housingloanmanager",
    version="0.1.0",
    info_plist={
        "CFBundleName": "Housing Loan Manager",
        "CFBundleDisplayName": "Housing Loan Manager",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "0.1.0",
        "NSHighResolutionCapable": True,
        "NSHumanReadableCopyright": "© 2026 Jithesh Bharathan",
    },
)
