# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for building the Housing Loan Manager macOS app bundle."""

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Only pyqtgraph needs collect_all (its colormaps/icons are data files that
# import-analysis misses). PySide6 is handled by PyInstaller's own hooks,
# which follow actual imports — collect_all("PySide6") would bundle every Qt
# module (WebEngine's Chromium, Quick3D, Multimedia, ...) and triple the app
# size for a plain QtWidgets app.
datas, binaries, hiddenimports = collect_all("pyqtgraph")

a = Analysis(
    ["run.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6.QtWebEngineCore",
        "PySide6.QtWebEngineWidgets",
        "PySide6.QtQuick",
        "PySide6.QtQuick3D",
        "PySide6.QtQml",
        "PySide6.QtMultimedia",
        "PySide6.QtCharts",
        "PySide6.QtDataVisualization",
        "PySide6.Qt3DCore",
        "PySide6.Qt3DRender",
        "PySide6.QtPdf",
        "PySide6.QtWebChannel",
        "PySide6.QtNetworkAuth",
        "PySide6.QtRemoteObjects",
        "PySide6.QtSensors",
        "PySide6.QtSerialPort",
        "PySide6.QtBluetooth",
        "PySide6.QtPositioning",
        "PySide6.QtLocation",
    ],
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
