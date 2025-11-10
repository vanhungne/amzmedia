#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Workflow Orchestrator
Automates: Script Import → Groq Parse → Voice Generation → Image Generation
"""

import os
import sys
import json
import threading
import shutil
from pathlib import Path
from typing import List, Optional
from PySide6.QtCore import QObject, Signal, QTimer, Qt, QMetaObject, Slot
from PySide6.QtWidgets import QMessageBox, QProgressDialog

# Import from image_tab_full for AI analysis
try:
    from image_tab_full import (
        analyze_script_with_groq,
        analyze_script_with_openai,
        analyze_script_with_gemini
    )
except:
    analyze_script_with_groq = None
    analyze_script_with_openai = None
    analyze_script_with_gemini = None


class AutoWorkflowOrchestrator(QObject):
    """
    Orchestrates automatic workflow across tabs:
    1. Parse script with AI (Groq/ChatGPT/Gemini - from project settings)
    2. Generate voice with ElevenLabs  
    3. Generate images with Imagen/Gemini
    """
    
    # Signals for progress tracking
    step_changed = Signal(str)  # Step description
    progress_changed = Signal(int, int)  # current, total
    workflow_complete = Signal()
    workflow_error = Signal(str)
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.project = None
        self.script_text = ""
        self.script_path = ""
        self.prompts = []
        self.voice_path = None
        self.project_dir = None
        
        self.progress_dialog = None
        
    def start_workflow(self, project, script_path: str):
        """
        Main entry point for automatic workflow
        
        Args:
            project: Project object with channel settings
            script_path: Path to script.txt file
        """
        self.project = project
        self.script_path = script_path
        
        # Step 1: Read script
        self.step_changed.emit("📖 Reading script...")
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                self.script_text = f.read().strip()
        except Exception as e:
            self.workflow_error.emit(f"Failed to read script: {e}")
            return
        
        if not self.script_text:
            self.workflow_error.emit("Script file is empty!")
            return
        
        # Step 2: Create folder structure
        self.step_changed.emit("📁 Creating project folders...")
        try:
            self.project_dir = self.create_folder_structure()
        except Exception as e:
            self.workflow_error.emit(f"Failed to create folders: {e}")
            return
        
        # Step 3: Parse script with AI (provider from Image tab UI OR project)
        # Priority: Image tab UI (current selection) > Project settings > Default (Groq)
        provider = None
        model = None
        
        # Try to get from Image tab UI first (user's current selection in combo boxes)
        image_widget = self.get_image_generator_widget()
        if image_widget:
            # Get from UI combo boxes (current selection, even if not saved)
            if hasattr(image_widget, 'toolbar_provider_cb'):
                ui_provider = image_widget.toolbar_provider_cb.currentText().strip()
                if ui_provider:
                    provider = ui_provider
                    print(f"[AUTO WORKFLOW] Using provider from Image tab UI: {provider}")
            
            if hasattr(image_widget, 'toolbar_model_cb'):
                ui_model = image_widget.toolbar_model_cb.currentText().strip()
                if ui_model:
                    model = ui_model
                    print(f"[AUTO WORKFLOW] Using model from Image tab UI: {model}")
        
        # Fallback to project settings if Image tab UI doesn't have selection
        if not provider:
        provider = getattr(self.project, 'prompt_provider', 'Groq') or 'Groq'
            print(f"[AUTO WORKFLOW] Using provider from project: {provider}")
        
        if not model:
        model = getattr(self.project, 'prompt_model', 'llama-3.3-70b-versatile') or 'llama-3.3-70b-versatile'
            print(f"[AUTO WORKFLOW] Using model from project: {model}")
        
        self.step_changed.emit(f"🤖 Analyzing script with {provider} ({model})...")
        self.parse_script_with_ai(provider, model)
    
    def create_folder_structure(self) -> Path:
        """
        Create project folder structure at the SAME LEVEL as imported script file.
        
        If auto_organize_folders is enabled:
        [parent_directory]\\
            ├─ script.txt (imported file)
            └─ script\\          ← Same level as script.txt
                ├─ voice\\
                ├─ image\\
                └─ video\\
        
        Otherwise (default):
        [parent_directory]\\
            ├─ script.txt
            ├─ voice\\
            ├─ image\\
            └─ video\\
        """
        # Base directory = parent of script file
        script_file = Path(self.script_path)
        base_dir = script_file.parent
        print(f"[AUTO WORKFLOW] Script location: {script_file}")
        print(f"[AUTO WORKFLOW] Parent directory: {base_dir}")
        
        # Create project folder (named after script) at SAME LEVEL as script
        # Always create a folder named after the script (e.g., LD280)
        # It will contain 3 subfolders: voice/image/video
        project_folder_name = script_file.stem
        
        project_folder = base_dir / project_folder_name
        project_folder.mkdir(parents=True, exist_ok=True)
        print(f"[AUTO WORKFLOW] Created project folder: {project_folder}")
        
        # Subdirectories inside project folder
        voice_dir = project_folder / "voice"
        image_dir = project_folder / "image"
        video_dir = project_folder / "video"
        
        voice_dir.mkdir(parents=True, exist_ok=True)
        image_dir.mkdir(parents=True, exist_ok=True)
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # Update project paths
        self.project.voice_output = str(voice_dir)
        self.project.image_output = str(image_dir)
        self.project.video_output = str(video_dir)
        
        print(f"[AUTO WORKFLOW] Created folders:")
        print(f"  - Project: {project_folder}")
        print(f"    ├─ Voice: {voice_dir}")
        print(f"    ├─ Image: {image_dir}")
        print(f"    └─ Video: {video_dir}")
        return project_folder
    
    def parse_script_with_ai(self, provider: str, model: str):
        """Parse script with AI (Groq/ChatGPT/Gemini) in background thread"""
        def worker():
            try:
                # Use num_prompts from project (already randomized 12-24 on import)
                num_prompts = self.project.num_prompts
                print(f"[AUTO WORKFLOW] Using num_prompts: {num_prompts} (from project)")
                
                # Get custom system prompt from project (if available)
                custom_prompt = self.project.script_template or ""
                if custom_prompt:
                    print(f"[AUTO WORKFLOW] Using custom system prompt from project")
                else:
                    print(f"[AUTO WORKFLOW] Using default system prompt")
                
                prompts = None
                
                # Call appropriate AI based on provider
                if provider == "ChatGPT":
                    # Load OpenAI keys
                    openai_keys = self.load_openai_keys()
                    if not openai_keys:
                        self.workflow_error.emit("No OpenAI API keys found! Add keys in Settings tab.")
                        return
                    
                    if analyze_script_with_openai:
                        prompts = analyze_script_with_openai(
                            script=self.script_text,
                            num_parts=num_prompts,
                            openai_api_key=openai_keys[0],
                            model=model,
                            custom_system_prompt=custom_prompt
                        )
                        print(f"[AUTO WORKFLOW] Got {len(prompts)} prompts from ChatGPT ({model})")
                    else:
                        self.workflow_error.emit("OpenAI integration not available")
                        return
                        
                elif provider == "Gemini":
                    # Load Gemini keys
                    gemini_keys = self.load_gemini_keys()
                    if not gemini_keys:
                        self.workflow_error.emit("No Gemini API keys found! Add keys in Settings tab.")
                        return
                    
                    if analyze_script_with_gemini:
                        prompts = analyze_script_with_gemini(
                            script=self.script_text,
                            num_parts=num_prompts,
                            gemini_api_key=gemini_keys[0],
                            model=model,
                            custom_system_prompt=custom_prompt
                        )
                        print(f"[AUTO WORKFLOW] Got {len(prompts)} prompts from Gemini ({model})")
                    else:
                        self.workflow_error.emit("Gemini integration not available")
                        return
                        
                else:  # Groq (default)
                    # Load Groq keys
                    groq_keys = self.load_groq_keys()
                    if not groq_keys:
                        self.workflow_error.emit("No Groq API keys found! Add keys in Settings tab.")
                        return
                    
                    if analyze_script_with_groq:
                        prompts = analyze_script_with_groq(
                            script=self.script_text,
                            num_parts=num_prompts,
                            groq_api_key=groq_keys[0],
                            custom_system_prompt=custom_prompt
                        )
                        print(f"[AUTO WORKFLOW] Got {len(prompts)} prompts from Groq ({model})")
                    else:
                        self.workflow_error.emit("Groq integration not available")
                        return
                
                if prompts:
                    self.prompts = prompts
                    # Continue to voice generation first, then images
                    self.step_changed.emit(f"✅ Generated {len(prompts)} prompts")
                    print("[AUTO WORKFLOW] Invoking generate_voice on main thread")
                    QMetaObject.invokeMethod(self, "generate_voice", Qt.QueuedConnection)
                else:
                    self.workflow_error.emit(f"Failed to generate prompts with {provider}")
                    
            except Exception as e:
                self.workflow_error.emit(f"{provider} AI error: {e}")
                import traceback
                traceback.print_exc()
        
        threading.Thread(target=worker, daemon=True).start()
    
    @Slot()
    def generate_voice(self):
        """Auto generate voice in Audio tab"""
        try:
            print("[GENERATE_VOICE] Starting voice generation")
            
            # Check if voice_id is set
            if not self.project.voice_id:
                print("[GENERATE_VOICE] No voice ID set, skipping")
                self.step_changed.emit("⏭️ Skipping voice (no voice ID set)")
                # Continue to images
                QMetaObject.invokeMethod(self, "generate_images", Qt.QueuedConnection)
                return
            
            print(f"[GENERATE_VOICE] Voice ID: {self.project.voice_id}")
            self.step_changed.emit("🎵 Switching to Audio tab...")
            
            # Switch to Audio tab
            audio_tab_index = self.get_audio_tab_index()
            print(f"[GENERATE_VOICE] Audio tab index: {audio_tab_index}")
            
            if audio_tab_index < 0:
                print("[GENERATE_VOICE] Audio tab not found")
                self.step_changed.emit("⏭️ Audio tab not available, skipping to images")
                QMetaObject.invokeMethod(self, "generate_images", Qt.QueuedConnection)
                return
            
            self.main_window.tabs.setCurrentIndex(audio_tab_index)
            
            # Give UI time to switch tabs
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            
            # Get ElevenLabs widget
            audio_widget = self.get_elevenlabs_widget()
            print(f"[GENERATE_VOICE] Audio widget: {audio_widget}")
            
            if not audio_widget:
                print("[GENERATE_VOICE] Audio widget not found")
                self.step_changed.emit("⏭️ Audio widget not available, skipping to images")
                QMetaObject.invokeMethod(self, "generate_images", Qt.QueuedConnection)
                return
            
            # Split script into chunks
            self.step_changed.emit("📝 Splitting script into chunks...")
            chunks = self.split_script_into_chunks(self.script_text)
            print(f"[GENERATE_VOICE] Split into {len(chunks)} chunks")
            
            # Load chunks into ElevenLabs
            audio_widget.chunks = []
            for i, chunk_text in enumerate(chunks, start=1):
                audio_widget.chunks.append({
                    'number': i,
                    'content': chunk_text,  # ElevenLabs uses 'content', not 'text'
                    'status': 'Queue',
                    'file': None
                })
            
            audio_widget._index_chunks()
            audio_widget.update_chunks_display()
            print(f"[GENERATE_VOICE] Loaded {len(audio_widget.chunks)} chunks into widget")
            
            # Set voice ID - Validate first, then use
            voice_set = False
            
            # First, validate voice ID exists on ElevenLabs (even if in cache)
            print(f"[GENERATE_VOICE] Validating voice ID: {self.project.voice_id}")
            voice_valid = self.validate_voice_id(audio_widget, self.project.voice_id)
            
            if not voice_valid:
                error_msg = f"Voice ID '{self.project.voice_id}' không hợp lệ hoặc không tồn tại trên ElevenLabs!"
                print(f"[GENERATE_VOICE] ❌ {error_msg}")
                print(f"[GENERATE_VOICE] Possible reasons:")
                print(f"  1. Voice ID is incorrect: {self.project.voice_id}")
                print(f"  2. Voice was deleted from ElevenLabs")
                print(f"  3. Voice belongs to a different account")
                print(f"  4. API keys don't have access to this voice")
                print(f"[GENERATE_VOICE] 🛑 Stopping workflow - Voice validation failed")
                
                self.step_changed.emit(f"❌ Voice error: {error_msg}")
                self.workflow_error.emit(error_msg)
                return  # Stop workflow completely
            
            # Voice is valid on ElevenLabs API, now check if it's in local cache
            print(f"[GENERATE_VOICE] ✅ Voice ID '{self.project.voice_id}' is valid on ElevenLabs API")
            
            for idx in range(audio_widget.voice_combo.count()):
                if audio_widget.voice_combo.itemData(idx) == self.project.voice_id:
                    audio_widget.voice_combo.setCurrentIndex(idx)
                    voice_set = True
                    print(f"[GENERATE_VOICE] ✅ Voice found in local cache at index {idx}")
                    break
            
            if not voice_set:
                # Voice is valid on ElevenLabs API but not in local cache, add it
                print(f"[GENERATE_VOICE] ℹ️ Voice ID '{self.project.voice_id}' exists on ElevenLabs but not in local cache")
                print(f"[GENERATE_VOICE] Adding voice to local cache for future use...")
                voice_name = self.get_project_abbreviation(self.project.name)
                print(f"[GENERATE_VOICE] Voice name: {voice_name}")
                
                new_voice = {
                    'id': self.project.voice_id,
                    'name': voice_name
                }
                
                # Add to voices cache
                audio_widget.voices_cache.append(new_voice)
                audio_widget.save_voices()
                audio_widget.update_voice_list()
                
                # Set the newly added voice
                for idx in range(audio_widget.voice_combo.count()):
                    if audio_widget.voice_combo.itemData(idx) == self.project.voice_id:
                        audio_widget.voice_combo.setCurrentIndex(idx)
                        voice_set = True
                        print(f"[GENERATE_VOICE] ✅ Voice '{voice_name}' added to cache and ready to use (index {idx})")
                        print(f"[GENERATE_VOICE] ✅ Voice validated on ElevenLabs API → Added to local cache → Ready to generate")
                        break
                
                self.step_changed.emit(f"✅ Voice validated and added to cache: {voice_name}")
            
            # Set output directory and script path (for file naming)
            if hasattr(audio_widget, 'project_chunks_audio_dir'):
                audio_widget.project_chunks_audio_dir = self.project.voice_output
                print(f"[GENERATE_VOICE] Set output dir: {self.project.voice_output}")
            
            # Set script path so merge_audio_files can use it for file naming
            if hasattr(audio_widget, 'project_text_path'):
                audio_widget.project_text_path = self.script_path
                print(f"[GENERATE_VOICE] Set script path: {self.script_path}")
            elif hasattr(audio_widget, 'script_path'):
                audio_widget.script_path = self.script_path
                print(f"[GENERATE_VOICE] Set script path: {self.script_path}")
            
            self.step_changed.emit(f"🎙️ Generating {len(chunks)} voice chunks...")
            
            # Start generation (auto_mode=True to skip dialogs)
            target = [c for c in audio_widget.chunks if c['status'] != 'Success']
            print(f"[GENERATE_VOICE] Starting generation for {len(target)} chunks")
            audio_widget._start_generation(target, auto_mode=True)
            
            # Continue to images after a short delay (voice generation runs in background)
            print("[GENERATE_VOICE] Scheduling image generation in 2 seconds")
            QTimer.singleShot(2000, self.generate_images)
            
        except Exception as e:
            print(f"[VOICE ERROR] {e}")
            import traceback
            traceback.print_exc()
            # Continue to images even if voice fails
            self.step_changed.emit(f"⚠️ Voice error: {e}, continuing to images...")
            QMetaObject.invokeMethod(self, "generate_images", Qt.QueuedConnection)
    
    def split_script_into_chunks(self, script: str, chunk_size: int = 800) -> List[str]:
        """Split script into chunks for voice generation"""
        import re
        
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', script)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [c for c in chunks if c]
    
    @Slot()
    def generate_images(self):
        """Auto generate images in Image tab"""
        try:
            self.step_changed.emit("🎨 Switching to Image tab...")
            
            # Get image generator widget first
            image_widget = self.get_image_generator_widget()
            if not image_widget:
                self.workflow_error.emit("Image Generator tab not available")
                return
            
            # Switch to Image tab
            image_tab_index = self.get_image_tab_index()
            self.main_window.tabs.setCurrentIndex(image_tab_index)
            
            # Give UI time to update tab switch
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()
            
            # Set output folder
            image_widget.settings.set("output_dir", self.project.image_output)
            image_widget.output_dir = Path(self.project.image_output)
            image_widget.output_edit.setText(self.project.image_output)
            
            # Clear existing rows
            for row in list(image_widget.rows):
                row.deleteLater()
            image_widget.rows.clear()
            
            # Give UI time to clear
            QApplication.processEvents()
            
            # Add all prompts to queue
            self.step_changed.emit(f"📝 Adding {len(self.prompts)} prompts to queue...")
            print(f"[GENERATE_IMAGES] Adding {len(self.prompts)} prompts")
            
            for i, prompt in enumerate(self.prompts):
                print(f"[GENERATE_IMAGES] Adding prompt {i+1}: {prompt[:60]}...")
                image_widget.add_row(prompt)
                self.progress_changed.emit(i + 1, len(self.prompts))
                # Process events every 3 prompts for UI responsiveness
                if (i + 1) % 3 == 0:
                    QApplication.processEvents()
            
            # Final process events to ensure all rows are added
            QApplication.processEvents()
            
            print(f"[GENERATE_IMAGES] Total rows in widget: {len(image_widget.rows)}")
            
            # Connect completion signal
            image_widget.worker = None  # Reset worker
            
            # Start generation
            self.step_changed.emit("🎨 Generating images...")
            print(f"[GENERATE_IMAGES] Calling on_run_all()")
            image_widget.on_run_all()
            
            # Note: We can't easily wait for completion without modifying ImageGeneratorTab
            # For now, show message that generation has started
            self.workflow_complete.emit()
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.workflow_error.emit(f"Image generation error: {e}")
    
    def validate_voice_id(self, audio_widget, voice_id: str) -> bool:
        """
        Validate if voice ID exists and is accessible via ElevenLabs API
        
        Args:
            audio_widget: ElevenLabs widget with API manager
            voice_id: Voice ID to validate
        
        Returns:
            True if voice exists and is accessible, False otherwise
        """
        if not voice_id or not voice_id.strip():
            return False
        
        # Try to get an API key
        if not hasattr(audio_widget, 'api_manager'):
            print(f"[VALIDATE VOICE] No API manager available")
            return False
        
        api_manager = audio_widget.api_manager
        if not api_manager or not hasattr(api_manager, 'get_next'):
            print(f"[VALIDATE VOICE] API manager not properly initialized")
            return False
        
        import requests
        
        # Try up to 3 API keys to validate voice
        original_key_index = None
        if hasattr(api_manager, 'current_key_index'):
            original_key_index = api_manager.current_key_index
        
        for attempt in range(min(3, len(api_manager.keys) if hasattr(api_manager, 'keys') else 3)):
            try:
                api_key = api_manager.get_next()
                if not api_key:
                    print(f"[VALIDATE VOICE] No API key available for attempt {attempt + 1}")
                    continue
                
                # Call ElevenLabs API to get voice details
                url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
                headers = {
                    "xi-api-key": api_key,
                    "Content-Type": "application/json"
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Restore original key index if we saved it
                    if original_key_index is not None and hasattr(api_manager, 'current_key_index'):
                        api_manager.current_key_index = original_key_index
                    print(f"[VALIDATE VOICE] ✅ Voice {voice_id} exists and is accessible")
                    return True
                elif response.status_code == 404:
                    # Restore original key index
                    if original_key_index is not None and hasattr(api_manager, 'current_key_index'):
                        api_manager.current_key_index = original_key_index
                    print(f"[VALIDATE VOICE] ❌ Voice {voice_id} not found (404)")
                    return False
                elif response.status_code == 401:
                    print(f"[VALIDATE VOICE] ⚠️ API key invalid, trying next key...")
                    continue
                else:
                    print(f"[VALIDATE VOICE] ⚠️ API returned status {response.status_code}, trying next key...")
                    continue
                    
            except Exception as e:
                print(f"[VALIDATE VOICE] Error validating voice: {e}")
                continue
        
        # Restore original key index if we saved it
        if original_key_index is not None and hasattr(api_manager, 'current_key_index'):
            api_manager.current_key_index = original_key_index
        
        # If all attempts failed, assume voice is invalid
        print(f"[VALIDATE VOICE] ❌ Could not validate voice {voice_id} after 3 attempts")
        return False
    
    def get_project_abbreviation(self, project_name: str) -> str:
        """
        Get project name abbreviation (max 3 characters)
        
        Examples:
            "Simple Woman" -> "SW"
            "My Project" -> "MP"
            "Test" -> "Tes"
        """
        if not project_name:
            return "PRJ"
        
        # Split by spaces and take first letters
        words = project_name.strip().split()
        if len(words) >= 2:
            # Multi-word: take first letter of each word (max 3)
            abbr = ''.join([w[0].upper() for w in words[:3] if w])
            return abbr[:3]
        else:
            # Single word: take first 3 characters
            return project_name[:3].upper()
    
    def load_groq_keys(self) -> List[str]:
        """Load Groq API keys from settings"""
        try:
            settings_file = Path(__file__).parent / "vgp_settings.json"
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    keys = data.get("groq_keys", [])
                    return [k.strip() for k in keys if k.strip()]
        except Exception as e:
            print(f"Error loading Groq keys: {e}")
        return []
    
    def load_openai_keys(self) -> List[str]:
        """Load OpenAI API keys from server or settings"""
        try:
            # Try to load from server first (if API client available)
            if hasattr(self.main_window, 'api_client') and self.main_window.api_client:
                try:
                    keys = self.main_window.api_client.get_openai_keys()
                    if keys:
                        return [k.get('api_key', '').strip() for k in keys if k.get('api_key', '').strip()]
                except:
                    pass
            
            # Fallback to settings file
            settings_file = Path(__file__).parent / "vgp_settings.json"
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    keys = data.get("openai_keys", [])
                    return [k.strip() for k in keys if k.strip()]
        except Exception as e:
            print(f"Error loading OpenAI keys: {e}")
        return []
    
    def load_gemini_keys(self) -> List[str]:
        """Load Gemini API keys from server or settings"""
        try:
            # Try to load from server first (if API client available)
            if hasattr(self.main_window, 'api_client') and self.main_window.api_client:
                try:
                    keys = self.main_window.api_client.get_gemini_keys()
                    if keys:
                        return [k.get('api_key', '').strip() for k in keys if k.get('api_key', '').strip()]
                except:
                    pass
            
            # Fallback to settings file
            settings_file = Path(__file__).parent / "vgp_settings.json"
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    keys = data.get("gemini_keys", [])
                    return [k.strip() for k in keys if k.strip()]
        except Exception as e:
            print(f"Error loading Gemini keys: {e}")
        return []
    
    def get_audio_tab_index(self) -> int:
        """Get index of Audio Generator tab"""
        for i in range(self.main_window.tabs.count()):
            tab_text = self.main_window.tabs.tabText(i)
            if "Audio" in tab_text:
                return i
        return -1  # Not found
    
    def get_elevenlabs_widget(self):
        """Get ElevenLabsGUI widget"""
        try:
            # Try to get from main window attribute
            if hasattr(self.main_window, 'elevenlabs_widget'):
                return self.main_window.elevenlabs_widget
            
            # Try to find in tab
            idx = self.get_audio_tab_index()
            if idx < 0:
                return None
            
            widget = self.main_window.tabs.widget(idx)
            
            # If it's a container, search for ElevenLabsGUI
            if hasattr(widget, 'findChild'):
                from ElevenlabsV15 import ElevenLabsGUI
                found = widget.findChild(ElevenLabsGUI)
                if found:
                    return found
            
            return widget
        except Exception as e:
            print(f"[GET ELEVENLABS ERROR] {e}")
            return None
    
    def get_image_tab_index(self) -> int:
        """Get index of Image Generator tab"""
        # Search for tab by title
        for i in range(self.main_window.tabs.count()):
            tab_text = self.main_window.tabs.tabText(i)
            if "Image" in tab_text:
                return i
        return 2  # Default fallback
    
    def get_image_generator_widget(self):
        """Get ImageGeneratorTab widget"""
        try:
            # Try to get from main window attribute
            if hasattr(self.main_window, 'image_generator_widget'):
                return self.main_window.image_generator_widget
            
            # Try to find in tab
            idx = self.get_image_tab_index()
            widget = self.main_window.tabs.widget(idx)
            
            # If it's a container, search for ImageGeneratorTab
            if hasattr(widget, 'findChild'):
                from image_tab_full import ImageGeneratorTab
                found = widget.findChild(ImageGeneratorTab)
                if found:
                    return found
            
            return widget
        except:
            return None
    


def create_project_folder_structure(project, script_path: str) -> Path:
    """
    Standalone helper to create folder structure
    Returns: base directory path
    """
    base_dir = Path(r"C:\WorkFlow") / project.name
    base_dir.mkdir(parents=True, exist_ok=True)
    
    voice_dir = base_dir / "voice"
    image_dir = base_dir / "image"
    video_dir = base_dir / "video"
    
    voice_dir.mkdir(exist_ok=True)
    image_dir.mkdir(exist_ok=True)
    video_dir.mkdir(exist_ok=True)
    
    script_dest = base_dir / "script.txt"
    shutil.copy(script_path, script_dest)
    
    project.voice_output = str(voice_dir)
    project.image_output = str(image_dir)
    project.video_output = str(video_dir)
    
    return base_dir

