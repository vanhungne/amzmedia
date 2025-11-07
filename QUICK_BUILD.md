# 🚀 Quick Build Guide

## ⚡ Cách nhanh nhất

### **Option 1: Build đơn giản (chỉ Python tool)**
```bash
build-simple.bat
```
→ Tạo `dist\WorkFlowTool.exe`

### **Option 2: Build đầy đủ (có Admin Panel)**
```bash
build.bat
```
→ Tạo executable + admin-panel build

### **Option 3: Build production (chuẩn bị phân phối)**
```bash
build-production.bat
```
→ Tạo folder distribution hoàn chỉnh với version number

---

## 📋 Yêu cầu trước khi build

1. ✅ Python 3.8+ đã cài
2. ✅ Node.js 18+ đã cài (nếu build admin panel)
3. ✅ Internet connection để download dependencies

---

## 🎯 Kết quả

Sau khi build xong:

**build-simple.bat:**
- `dist\WorkFlowTool.exe`

**build.bat:**
- `dist\WorkFlowTool.exe`
- Admin panel đã build (`.next` folder)

**build-production.bat:**
- `dist\WorkFlowTool-v20241105\` (folder hoàn chỉnh)
  - `WorkFlowTool.exe`
  - `admin-panel/` (đã build)
  - `image/`
  - `README.txt`

---

## 🔧 Troubleshooting

### Lỗi "Python not found"
→ Cài Python và thêm vào PATH

### Lỗi "Module not found"
→ Chạy: `pip install -r requirements.txt`

### Lỗi "PyInstaller not found"
→ Script sẽ tự động cài, hoặc chạy: `pip install pyinstaller`

### File .exe quá lớn
→ Chỉnh file `WorkFlowTool.spec` để exclude modules không cần

---

## 📦 Phân phối

1. Zip folder `dist\WorkFlowTool-v*` 
2. Gửi cho user
3. User giải nén và chạy `WorkFlowTool.exe`

---

**Done!** 🎉

