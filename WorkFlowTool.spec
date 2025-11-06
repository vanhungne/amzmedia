# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os
from pathlib import Path

datas = []
binaries = []
hiddenimports = ['requests', 'cryptography', 'PIL', 'PIL.Image', 'playwright', 'playwright.sync_api']

# Collect PySide6
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Collect Playwright
tmp_ret = collect_all('playwright')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Add Playwright browsers if they exist
try:
    import subprocess
    import sys
    
    # Find Playwright browsers location
    result = subprocess.run(
        [sys.executable, "-c", 
         "from playwright.sync_api import sync_playwright; "
         "p = sync_playwright().start(); "
         "exe = p.chromium.executable_path; "
         "p.stop(); "
         "print(exe)"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    if result.returncode == 0:
        browser_exe = Path(result.stdout.strip())
        
        # Find ms-playwright root folder
        ms_playwright_dir = browser_exe
        while ms_playwright_dir.name != "ms-playwright" and ms_playwright_dir.parent != ms_playwright_dir:
            ms_playwright_dir = ms_playwright_dir.parent
        
        if ms_playwright_dir.name == "ms-playwright" and ms_playwright_dir.exists():
            # Add browsers to datas (will be placed in _internal/)
            datas.append((str(ms_playwright_dir), 'ms-playwright'))
            print(f"[BUILD INFO] Adding Playwright browsers from: {ms_playwright_dir}")
        else:
            print("[BUILD WARNING] Playwright browsers not found - will download on first run")
    else:
        print("[BUILD WARNING] Could not detect Playwright browsers - will download on first run")
        
except Exception as e:
    print(f"[BUILD WARNING] Error checking Playwright browsers: {e}")
    print("[BUILD INFO] Browsers will be downloaded on first run")


a = Analysis(
    ['GenVideoPro.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WorkFlowTool',
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
    icon=['logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WorkFlowTool',
)
