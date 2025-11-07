# 🚀 Hướng dẫn Build WorkFlow Tool

## 📋 Yêu cầu

### 1. Python 3.8+
- Download: https://www.python.org/downloads/
- Kiểm tra: `python --version`

### 2. Node.js 18+
- Download: https://nodejs.org/
- Kiểm tra: `node --version`

### 3. Dependencies
- Tất cả sẽ được cài đặt tự động bởi build script

---

## 🔨 Cách Build

### **Cách 1: Build tự động (Recommended)**

Chạy file `build.bat`:
```bash
build.bat
```

Script sẽ tự động:
1. ✅ Install Python dependencies
2. ✅ Install PyInstaller
3. ✅ Build Admin Panel (Next.js)
4. ✅ Build Python executable
5. ✅ Tạo distribution folder

### **Cách 2: Build đơn giản (chỉ Python tool)**

Chạy file `build-simple.bat`:
```bash
build-simple.bat
```

### **Cách 3: Build thủ công**

#### **Bước 1: Install Python dependencies**
```bash
pip install -r requirements.txt
pip install pyinstaller
```

#### **Bước 2: Build Admin Panel (nếu cần)**
```bash
cd admin-panel
npm install
npm run build
cd ..
```

#### **Bước 3: Build Python executable**
```bash
pyinstaller --name="WorkFlowTool" --onefile --windowed GenVideoPro.py
```

---

## 📦 Kết quả Build

Sau khi build xong, bạn sẽ có:

```
dist/
└── WorkFlowTool.exe    ← File executable chính
```

---

## 🎯 Build Options

### **One-file executable (khuyến nghị)**
```bash
pyinstaller --onefile --windowed GenVideoPro.py
```
- ✅ Tạo 1 file .exe duy nhất
- ✅ Dễ phân phối
- ❌ Chạy chậm hơn (unpack mỗi lần)

### **One-folder executable**
```bash
pyinstaller --windowed GenVideoPro.py
```
- ✅ Chạy nhanh hơn
- ✅ Dễ debug
- ❌ Nhiều files

### **Với icon**
```bash
pyinstaller --icon=image\logo.ico --onefile --windowed GenVideoPro.py
```

### **Với data files**
```bash
pyinstaller --add-data "image;image" --onefile --windowed GenVideoPro.py
```

---

## 📝 Tùy chỉnh Build

### **Thêm icon**
1. Tạo file `image/logo.ico` (hoặc convert từ .jpg)
2. Thêm `--icon=image\logo.ico` vào PyInstaller command

### **Bao gồm admin-panel**
Nếu muốn bundle admin-panel vào executable:
```bash
pyinstaller --add-data "admin-panel\.next;admin-panel\.next" --onefile GenVideoPro.py
```

### **Tối ưu kích thước**
```bash
pyinstaller --onefile --windowed --exclude-module matplotlib --exclude-module numpy GenVideoPro.py
```

---

## 🐛 Troubleshooting

### **Lỗi: Module not found**
Thêm hidden import:
```bash
pyinstaller --hidden-import=module_name --onefile GenVideoPro.py
```

### **Lỗi: PySide6 không load được**
Thêm:
```bash
pyinstaller --collect-all PySide6 --onefile GenVideoPro.py
```

### **Lỗi: File không tìm thấy khi chạy .exe**
- Sử dụng `--add-data` để include files
- Hoặc dùng relative path trong code

### **Giảm kích thước .exe**
```bash
pyinstaller --onefile --windowed --exclude-module PIL --exclude-module matplotlib GenVideoPro.py
```

---

## 📦 Phân phối

### **Distribution Package**
1. Copy `WorkFlowTool.exe` vào folder mới
2. Copy `admin-panel` folder (nếu cần)
3. Copy `image` folder (nếu cần)
4. Tạo README.txt với hướng dẫn

### **Folder Structure**
```
WorkFlowTool-v1.0/
├── WorkFlowTool.exe
├── admin-panel/        (nếu cần)
├── image/              (nếu cần)
└── README.txt
```

---

## ✅ Checklist Trước khi Build

- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed (nếu build admin panel)
- [ ] Tất cả dependencies đã install
- [ ] Test tool chạy OK trước khi build
- [ ] Đã test tất cả features
- [ ] Icon file đã sẵn sàng (nếu cần)
- [ ] Version number đã update

---

## 🎉 Done!

Sau khi build xong, test file `.exe` trên máy khác để đảm bảo không thiếu dependencies.

