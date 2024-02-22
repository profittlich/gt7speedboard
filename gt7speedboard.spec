# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gt7speedboard.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    name='gt7speedboard',
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
    name='gt7speedboard',
)
app = BUNDLE(
    coll,
    name='gt7speedboard.app',
    icon=None,
    bundle_identifier=None,
)
