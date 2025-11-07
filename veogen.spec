# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all
from pathlib import Path
import os

datas = []
binaries = []
hiddenimports = []

# ========== ffmpeg (đặt cùng thư mục với .py) ==========
if Path('ffmpeg.exe').exists():
    binaries += [(str(Path('ffmpeg.exe')), '.')]
else:
    print('WARNING: ffmpeg.exe not found in current directory')

# ========== PySide6: plugins, QtMultimedia, v.v… ==========
pyside_datas, pyside_bins, pyside_hidden = collect_all('PySide6')
datas += pyside_datas
binaries += pyside_bins
hiddenimports += pyside_hidden

# ========== Playwright (mã Python) ==========
datas += collect_data_files('playwright')
hiddenimports += collect_submodules('playwright')

# ========== Bundle ms-playwright browsers ==========
# Detect ms-playwright root (PLAYWRIGHT_MS_ROOT from build.bat environment)
ms_playwright_root = os.environ.get('PLAYWRIGHT_MS_ROOT')

if not ms_playwright_root:
    # Fallback: try to detect from LOCALAPPDATA
    ms_playwright_root = str(Path(os.environ.get('LOCALAPPDATA', '')) / 'ms-playwright')

mp = Path(ms_playwright_root) if ms_playwright_root else None

if mp and mp.exists():
    print(f'[OK] Bundling ms-playwright from: {mp}')
    # Copy entire ms-playwright directory into _internal/ms-playwright
    # This will be accessible at runtime via APP_DIR/_internal/ms-playwright
    datas += [(str(mp), '_internal/ms-playwright')]
    
    # Verify chromium exists
    chromium_dirs = list(mp.glob('chromium-*'))
    if chromium_dirs:
        print(f'[OK] Found {len(chromium_dirs)} chromium browser(s)')
    else:
        print('[WARNING] No chromium-* folders found in ms-playwright')
else:
    print('=' * 60)
    print('[ERROR] ms-playwright not found!')
    print('Please run: python -m playwright install chromium')
    print('=' * 60)

a = Analysis(
    ['GenVideoPro_v2.py'],
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
    name='VeoProGen',
    icon='veoicon.ico',
    console=False,   # đổi True nếu muốn hiện console để debug
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='VeoProGen'
)




