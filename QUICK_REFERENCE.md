# 🚀 QUICK REFERENCE - Auto Workflow

## ⚡ Quick Start (3 Steps)

### 1️⃣ Create Project
```
📁 Projects Tab → ➕ New Project
  ├─ Name: "MyChannel"
  ├─ Prompts: 12
  └─ Voice: "Rachel (21m00Tcm4TlvDq8ikWAM)"
```

### 2️⃣ Import Script
```
📜 Import Script → Select script.txt → Yes
```

### 3️⃣ Done! 🎉
```
✓ Voice generating...
✓ Images generating...
✓ Check folders next to script.txt!
```

---

## 📂 Output Folder Structure

**OLD (Before):**
```
C:\WorkFlow\MyProject\
```

**NEW (After):**
```
[WHERE YOUR SCRIPT.TXT IS]\
  ├─ script.txt          (your file)
  ├─ voice\              (voice chunks)
  ├─ image\              (generated images)
  └─ video\              (for video output)
```

**Example:**
```
D:\MyScripts\Episode01\script.txt  ← You import this
                       \voice\     ← Voice outputs here
                       \image\     ← Images output here
                       \video\     ← Videos output here
```

---

## 🎙️ Voice Settings

### How to Add Voices
1. Go to **🎵 Audio Generator** tab
2. Click **Add Voice** button
3. Enter:
   - Voice ID: `21m00Tcm4TlvDq8ikWAM`
   - Voice Name: `Rachel`
4. Click OK

### Where are voices saved?
```
C:\TotalTool\Settings\voices.json
```

### How to use in project?
Select from dropdown when creating/editing project!

---

## 🎨 Image Prompts

### What you'll see:
```
✅ Prompts Generated

Generated 12 prompts:

1. Ultra-realistic photo, 16:9. A woman (fair ski...
2. Ultra-realistic photo, 16:9. A man (tan skin, ...
3. Ultra-realistic photo, 16:9. The woman (fair s...
4. Ultra-realistic photo, 16:9. The boat owner (t...
5. Ultra-realistic photo, 16:9. A man (weathered ...
... và 7 prompts khác

Adding to queue now...
```

### Queue shows all prompts
- Auto-scrolls to show new rows
- Each row has prompt text
- Status updates as generating

---

## ⚙️ Settings

### Groq API Keys
```
⚙️ Settings Tab → Groq Keys section
```

### Number of Prompts
```
📁 Projects Tab → Edit Project → Number of Prompts
```

### Voice Chunk Size
```
Default: 800 characters
(Auto-split by sentences)
```

---

## 🔧 Troubleshooting

### "No Groq API keys found"
→ Add keys in Settings tab

### "No voice ID set"
→ Edit project and select voice from dropdown

### "Queue doesn't show prompts"
→ Check console for "[ADDING ROW X]" messages
→ Look for popup message with prompt summary

### "Folders not created"
→ Check script.txt location
→ Folders created in SAME directory as script

### "Voice tab doesn't run"
→ Check if voice ID is selected in project
→ Check if ElevenLabs API keys are added

---

## 📊 Workflow Status Messages

| Message | Meaning |
|---------|---------|
| 📁 Creating project folders... | Making voice/image/video dirs |
| 🤖 Analyzing script with Groq AI... | Parsing script into prompts |
| ✅ Generated 12 prompts | Groq finished, prompts ready |
| 🎵 Switching to Audio tab... | Going to voice generation |
| 📝 Splitting script into chunks... | Preparing voice chunks |
| 🎙️ Generating X voice chunks... | Voice generation started |
| 🎨 Switching to Image tab... | Going to image generation |
| 📝 Adding 12 prompts to queue... | Adding prompts to UI |
| 🎨 Generating images... | Image generation started |
| ⏭️ Skipping voice (no voice ID set) | No voice, going to images |
| ⚠️ Voice error: ..., continuing | Error but continuing |

---

## 💡 Pro Tips

### Tip 1: Organize by Episode
```
D:\MyChannel\
  ├─ Episode01\
  │   ├─ script.txt
  │   ├─ voice\
  │   ├─ image\
  │   └─ video\
  └─ Episode02\
      ├─ script.txt
      ├─ voice\
      ├─ image\
      └─ video\
```

### Tip 2: Multiple Projects
Create separate projects for different channels:
- Project: "DramaChannel" → Voice: "Bella"
- Project: "FactsChannel" → Voice: "Josh"

### Tip 3: Test Workflow
Use a small script (3-5 prompts) first to test:
```
Number of Prompts: 3
Script: 500 characters
```

### Tip 4: Monitor Console
Watch console for debug messages:
```
[AUTO WORKFLOW] Created folders...
[WORKER] Starting analysis...
[ADDING ROW 1]: Ultra-realistic...
```

---

## 📞 Need Help?

Check console output for detailed logs:
- `[AUTO WORKFLOW]` = Workflow status
- `[WORKER]` = AI analysis
- `[ADDING ROW X]` = Queue updates
- `[VOICE ERROR]` = Voice issues
- `[GET ELEVENLABS ERROR]` = Widget issues

---

**Last Updated:** 2025-10-30
**Version:** 2.0 Full Automation





