# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gt7playbackserver.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    name='GT7 telemetry playback server',
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
    name='GT7 telemetry playback server',
)
app = BUNDLE(
    coll,
    name='GT7 telemetry playback server.app',
    icon='doc/104. steer wheel.png',
    bundle_identifier=None,
)
