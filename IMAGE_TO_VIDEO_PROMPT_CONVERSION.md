# 🎬 Image to Video Prompt Conversion - Auto Convert với Gemini AI

## ✅ Đã thêm

### 🎯 **Tính năng:**

Khi click "🎬 to Video" để chuyển images sang Image to Video tab, **tự động convert** image prompts thành **video prompts** bằng Gemini AI.

---

## 🔧 **Cách hoạt động:**

### **1. Function convert_image_prompt_to_video()**

```python
def convert_image_prompt_to_video(client: genai.Client, image_prompt: str) -> str:
    """
    Convert image generation prompt to video generation prompt using Gemini AI.
    
    - Takes image prompt
    - Adds MOTION, CAMERA MOVEMENT, DYNAMIC ELEMENTS
    - Keeps visual details
    - Makes it CINEMATIC
    """
```

### **2. System Prompt cho Gemini:**

```
You are an expert at converting image generation prompts to video generation prompts.

Your task:
- Take an image prompt and convert it to a VIDEO prompt
- Add MOTION, CAMERA MOVEMENT, and DYNAMIC ELEMENTS
- Keep the VISUAL DETAILS from the original prompt
- Make it CINEMATIC and engaging for video
- Output ONLY the video prompt, no explanations

Rules:
1. Always add camera movement (pan, tilt, dolly, zoom, aerial, etc.)
2. Add natural motion to subjects (wind, breathing, subtle movements)
3. Keep all visual details from original prompt
4. Make it cinematic and professional
5. Output ONLY the video prompt
```

### **3. Example Conversions:**

| Image Prompt | Video Prompt |
|--------------|--------------|
| "A serene mountain landscape with snow-capped peaks, blue sky, photorealistic" | "Smooth aerial drone shot flying over serene mountain landscape with snow-capped peaks against blue sky, camera slowly panning right, gentle wind moving clouds, cinematic 4K" |
| "Portrait of a woman with long blonde hair, elegant dress, studio lighting" | "Cinematic portrait shot of woman with long blonde hair in elegant dress, slow push-in camera movement, hair gently flowing, soft studio lighting with subtle shadows shifting, 4K photorealistic" |
| "A golden retriever sitting in a park" | "Medium shot of golden retriever sitting alertly in grassy park, dog turns head slightly, tail wagging gently, camera slowly dollying forward, natural daylight, cinematic depth of field" |

---

## 📋 **Workflow:**

```
1. User clicks "🎬 to Video" in Image Generator tab
   ↓
2. Collect all successful images (with image prompts)
   ↓
3. Load Gemini API key from server (via rotator)
   ↓
4. Convert each image prompt → video prompt using Gemini AI
   ↓
5. Add to Image to Video queue with VIDEO PROMPTS
   ↓
6. Refresh table & switch to Image to Video tab
   ↓
7. User generates videos with optimized prompts
```

---

## 🔑 **API Key Management:**

- **Nguồn:** Gemini API keys từ admin panel server
- **Auto-load:** Keys được load tự động khi login
- **Rotation:** Tự động rotate keys nếu quota hết
- **Fallback:** Nếu không có key hoặc lỗi, giữ nguyên image prompt

---

## 📊 **Logs:**

### **Khi convert prompts:**

```
[SEND TO VIDEO] Converting 3 image prompts to video prompts...
[CONVERT PROMPT] Using Gemini API key: AIzaSyDoCllssgPY3ucN...
[CONVERT PROMPT] Converting prompt 1/3
[CONVERT PROMPT]   Original: A serene mountain landscape with snow-capped peaks, blue sky...
[CONVERT PROMPT]   Video: Smooth aerial drone shot flying over serene mountain landscape...
[CONVERT PROMPT] ✅ Converted prompt 1
[CONVERT PROMPT] Converting prompt 2/3
[CONVERT PROMPT]   Original: Portrait of a woman with long blonde hair, elegant dress...
[CONVERT PROMPT]   Video: Cinematic portrait shot of woman with long blonde hair in elegant dress...
[CONVERT PROMPT] ✅ Converted prompt 2
[CONVERT PROMPT] Converting prompt 3/3
...
[SEND TO VIDEO] Adding 3 images to queue...
[SEND TO VIDEO] ✅ Added image 1 to queue (total in queue: 1)
[SEND TO VIDEO] ✅ Added image 2 to queue (total in queue: 2)
[SEND TO VIDEO] ✅ Added image 3 to queue (total in queue: 3)
```

---

## ⚠️ **Error Handling:**

### **1. No API Key:**
```
[CONVERT PROMPT] ⚠️ No Gemini API key available, using original prompts
```
→ Giữ nguyên image prompts

### **2. Conversion Error:**
```
[CONVERT PROMPT] ⚠️ Error converting prompt 1: API error
```
→ Giữ nguyên image prompt cho item đó, tiếp tục với items khác

### **3. Client Initialization Error:**
```
[CONVERT PROMPT] ⚠️ Error initializing Gemini client: ...
```
→ Giữ nguyên tất cả image prompts

---

## 🎯 **Lợi ích:**

### **TRƯỚC (Image Prompt):**
```
"A beautiful sunset over the ocean with orange and pink colors"
```
→ Thiếu motion, thiếu camera movement → video nhạt

### **SAU (Video Prompt):**
```
"Cinematic aerial shot slowly descending towards beautiful sunset over ocean with 
vibrant orange and pink colors spreading across sky, gentle waves rolling, 
camera panning left, reflections shimmering on water surface, 4K photorealistic"
```
→ Có motion, camera movement, dynamic elements → video chất lượng cao

---

## 📁 **Files đã sửa:**

### **1. `image_tab_full.py`:**

#### **Line 442-499: Function convert_image_prompt_to_video()**
```python
def convert_image_prompt_to_video(client: genai.Client, image_prompt: str) -> str:
    # Convert image prompt to video prompt using Gemini AI
    # Add motion, camera movement, dynamic elements
    # Keep visual details, make it cinematic
```

#### **Line 2724-2752: Auto-convert trong _finish_send_to_video()**
```python
# Convert image prompts to video prompts using Gemini AI
api_key = self.rotator.current()
client = genai.Client(api_key=api_key)

for idx, img_data in enumerate(successful_images):
    video_prompt = convert_image_prompt_to_video(client, img_data['prompt'])
    img_data['prompt'] = video_prompt  # Replace with video prompt
```

---

## 🧪 **Test Scenarios:**

### **Test 1: Normal Conversion**
```
1. Generate images với prompts
2. Click "🎬 to Video"
3. Kiểm tra console logs
4. Verify: Prompts trong Image to Video table có camera movement
```

### **Test 2: No API Key**
```
1. Logout khỏi admin panel (no keys loaded)
2. Generate images
3. Click "🎬 to Video"
4. Verify: Fallback to original prompts, no error
```

### **Test 3: Multiple Images**
```
1. Generate 10 images
2. Click "🎬 to Video"
3. Verify: All 10 prompts được convert
4. Check logs: Each conversion logged
```

---

## 💡 **Tips:**

1. **Image prompts càng chi tiết → Video prompts càng tốt**
   - Good: "Portrait of a woman with long blonde hair, elegant navy dress, studio lighting"
   - Better after convert: "Cinematic portrait shot of woman with long blonde hair in elegant navy dress, slow push-in camera movement, hair gently flowing, soft studio lighting with subtle shadows shifting"

2. **Gemini AI tự động thêm:**
   - Camera movements: pan, tilt, dolly, zoom, aerial
   - Natural motion: wind, breathing, subtle movements
   - Cinematic elements: depth of field, lighting shifts

3. **Nếu muốn custom conversion:**
   - Sửa `system_hint` trong `convert_image_prompt_to_video()`
   - Thêm rules hoặc examples cho Gemini

---

## 🔗 **Related:**

- Gemini API Keys: Admin Panel → API Keys Management
- Auto-load keys: Triggers khi login thành công
- Key rotation: Tự động khi quota exceeded

---

**Perfect! Giờ prompts được optimize tự động cho video generation!** 🎬✨





