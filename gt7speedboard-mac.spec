# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SpeedBoard for GT7.py'],
    pathex=[],
    binaries=[],
    datas=[('cars.csv', '.'), ('makers.csv', '.'), ('tracks/', './tracks/'), ('layouts/', './layouts/')],
    hiddenimports=['_salsa20', 'wakepy._deprecated._darwin'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SpeedBoard for GT7',
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
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SpeedBoard for GT7',
)
app = BUNDLE(
    coll,
    name='SpeedBoard for GT7.app',
    icon='doc/104. steer wheel.png',
    bundle_identifier=None,
)
