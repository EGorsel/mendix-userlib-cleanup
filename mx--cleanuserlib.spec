# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\core\\manager.py'],
    pathex=[],
    binaries=[],
    datas=[('src/core', 'src/core'), ('src/engines', 'src/engines'), ('config', 'config'), ('docs', 'docs')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['unittest', 'email', 'pydoc', 'http', 'html', 'xml'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='mx--cleanuserlib',
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
