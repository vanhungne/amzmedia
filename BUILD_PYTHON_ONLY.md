# 🐍 Build Python Tool Only

## ⚡ Cách nhanh nhất

Chạy file:
```bash
build-python-only.bat
```

Hoặc:
```bash
build-simple.bat
```

---

## 📋 Yêu cầu

- ✅ Python 3.8+
- ✅ Internet connection (để download dependencies)

---

## 🔨 Các bước Build

### **Tự động (Recommended)**
1. Chạy `build-python-only.bat`
2. Đợi build xong
3. File `.exe` sẽ ở `dist\WorkFlowTool.exe`

### **Thủ công**
```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 2. Build
pyinstaller --name="WorkFlowTool" --onefile --windowed GenVideoPro.py
```

---

## 📦 Kết quả

```
dist/
└── WorkFlowTool.exe  ← File executable này
```

**File size:** ~50-200MB (tùy vào dependencies)

---

## 🎯 Build Options

### **One-file (khuyến nghị)**
```bash
pyinstaller --onefile --windowed GenVideoPro.py
```
→ Tạo 1 file .exe duy nhất

### **Với data files (image folder)**
```bash
pyinstaller --add-data "image;image" --onefile --windowed GenVideoPro.py
```

### **Với icon**
```bash
pyinstaller --icon=image\logo.ico --onefile --windowed GenVideoPro.py
```

---

## 🐛 Troubleshooting

### Module not found
Thêm hidden import:
```bash
pyinstaller --hidden-import=module_name --onefile GenVideoPro.py
```

### PySide6 không load
Thêm:
```bash
pyinstaller --collect-all PySide6 --onefile GenVideoPro.py
```

### File quá lớn
Exclude modules không cần:
```bash
pyinstaller --exclude-module matplotlib --exclude-module numpy --onefile GenVideoPro.py
```

---

## ✅ Test

Sau khi build, test file `.exe`:
1. Copy `dist\WorkFlowTool.exe` ra desktop
2. Double-click để chạy
3. Kiểm tra tất cả features hoạt động

---

**Done!** 🎉

