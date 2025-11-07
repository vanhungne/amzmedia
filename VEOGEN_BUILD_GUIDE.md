# VeoProGen Build Guide - Bundle Playwright Browsers

## ❌ Vấn đề hiện tại
Bạn gặp lỗi: `chromium_headless_shell-1187/chrome-win/headless_shell.exe` không tồn tại vì:
1. Build script chỉ copy ms-playwright vào `datas` mà không kiểm tra cấu trúc
2. Runtime code chưa set `PLAYWRIGHT_BROWSERS_PATH` đúng
3. PyInstaller đưa vào sai vị trí (không phải `_internal/ms-playwright`)

## ✅ Giải pháp

### 1. Thay build.bat cũ bằng `veogen_build.bat` mới

File `veogen_build.bat` đã được tạo với các cải tiến:
- Tự động detect ms-playwright root directory đúng
- Export biến môi trường `PLAYWRIGHT_MS_ROOT` cho spec file
- Verify ms-playwright tồn tại trước khi build

### 2. Thay veogen.spec cũ bằng `veogen.spec` mới

File `veogen.spec` mới:
- Đọc `PLAYWRIGHT_MS_ROOT` từ environment
- Copy toàn bộ ms-playwright vào `_internal/ms-playwright`
- Verify có chromium-* folders trước khi build

```python
# Phần quan trọng trong veogen.spec:
datas += [(str(mp), '_internal/ms-playwright')]
```

### 3. Thêm runtime setup vào GenVideoPro_v2.py

**Thêm đoạn code này vào đầu file `GenVideoPro_v2.py` (sau phần imports):**

```python
import sys
import os
from pathlib import Path

# ========== Playwright Runtime Setup ==========
if getattr(sys, 'frozen', False):
    # Running as packaged executable
    APP_DIR = Path(sys.executable).parent
    base = Path(getattr(sys, "_MEIPASS", APP_DIR))
    
    possible_paths = [
        APP_DIR / "_internal" / "ms-playwright",   # Primary bundle
        base / "ms-playwright",                     # Temp _MEIPASS
        APP_DIR / "_external" / "ms-playwright",   # Fallback
    ]
    
    for mp in possible_paths:
        if mp.exists():
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(mp)
            print(f"[OK] Found Playwright browsers at: {mp}")
            break
    else:
        print("[WARNING] Playwright browsers not found in bundle")
```

## 📝 Cách build

### Bước 1: Copy 2 files mới vào thư mục project của bạn
- `veogen_build.bat` → thay thế build.bat cũ
- `veogen.spec` → thay thế veogen.spec cũ

### Bước 2: Thêm runtime code vào GenVideoPro_v2.py
Copy đoạn code ở trên vào đầu file `GenVideoPro_v2.py` (sau imports, trước code chính)

### Bước 3: Build
```cmd
veogen_build.bat
```

Build sẽ:
1. Tạo venv (nếu chưa có)
2. Cài dependencies
3. Cài Playwright Chromium
4. Detect ms-playwright location
5. Build với PyInstaller
6. Bundle ms-playwright vào `dist\VeoProGen\_internal\ms-playwright`

### Bước 4: Verify sau khi build xong

Kiểm tra file sau phải tồn tại:
```
dist\VeoProGen\_internal\ms-playwright\chromium-XXXX\chrome-win\chrome.exe
```

(XXXX là version number, ví dụ: chromium-1187)

### Bước 5: Test
```cmd
dist\VeoProGen\VeoProGen.exe
```

App sẽ:
- ✅ Không yêu cầu "playwright install"
- ✅ Không hiện lỗi "chromium_headless_shell not found"
- ✅ Chạy Playwright automation ngay lập tức

## 🎯 Cấu trúc thư mục sau khi build

```
dist/
└── VeoProGen/
    ├── VeoProGen.exe
    ├── _internal/
    │   ├── ms-playwright/           ← Browsers bundle
    │   │   ├── chromium-1187/
    │   │   │   └── chrome-win/
    │   │   │       └── chrome.exe   ← Chromium browser
    │   │   ├── firefox-.../ (nếu có)
    │   │   └── webkit-.../ (nếu có)
    │   ├── PySide6/
    │   ├── playwright/
    │   └── ... (các dependencies khác)
    └── ffmpeg.exe (nếu có)
```

## 🚀 Deploy

Khi deploy sang máy khác:
1. Copy **TOÀN BỘ** thư mục `dist\VeoProGen`
2. Không cần cài Python
3. Không cần cài Playwright
4. Không cần internet
5. Chạy `VeoProGen.exe` trực tiếp

## 🔧 Troubleshooting

### Nếu vẫn báo lỗi "chromium not found":

1. **Kiểm tra `_internal\ms-playwright` có tồn tại không:**
   ```cmd
   dir dist\VeoProGen\_internal\ms-playwright
   ```

2. **Kiểm tra có chromium-* folder không:**
   ```cmd
   dir dist\VeoProGen\_internal\ms-playwright\chromium-*
   ```

3. **Nếu không có, rebuild lại:**
   ```cmd
   rmdir /s /q dist build
   veogen_build.bat
   ```

4. **Nếu vẫn lỗi, chạy với console=True để xem log:**
   - Sửa `veogen.spec`: `console=True`
   - Build lại
   - Chạy exe và xem log in ra

### Nếu build báo "ms-playwright not found":

1. **Cài Playwright browsers thủ công:**
   ```cmd
   .venv\Scripts\python.exe -m playwright install chromium
   ```

2. **Verify đã cài:**
   ```cmd
   dir %LOCALAPPDATA%\ms-playwright\chromium-*
   ```

3. **Build lại:**
   ```cmd
   veogen_build.bat
   ```

## 📌 Notes

- File `playwright_runtime_setup.py` là file mẫu, bạn chỉ cần copy nội dung vào `GenVideoPro_v2.py`
- Không cần import `playwright_runtime_setup.py`, chỉ cần copy code
- Runtime setup phải chạy **TRƯỚC** khi bạn import hoặc sử dụng Playwright
- Build size sẽ tăng ~150-200MB do bundle Chromium browser

## 📚 Reference

Logic này được áp dụng từ WorkFlow Tool build system đã hoạt động ổn định.




