# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gt7playbackserver.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['_salsa20', 'wakepy._deprecated._windows'],
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
    a.binaries,
    a.datas,
    [],
    name='GT7 telemetry playback server',
    icon='doc/104. steer wheel-yellow.png',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
