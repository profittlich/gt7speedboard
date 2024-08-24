# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['graphicallapcomparison.py'],
    pathex=[],
    binaries=[],
    datas=[('cars.csv', '.'), ('makers.csv', '.')],
    hiddenimports=['_salsa20'],
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
    name='Graphical lap comparison',
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
    name='Graphical lap comparison',
)
app = BUNDLE(
    coll,
    name='Graphical lap comparison.app',
    icon='doc/104. steer wheel-blue.png',
    bundle_identifier=None,
)
