#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Helper script to copy Playwright browsers to dist folder
"""
import os
import sys
import shutil
from pathlib import Path

def find_playwright_browsers():
    """Find Playwright browsers installation directory"""
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Get chromium executable path
            browser = p.chromium.launch(headless=True)
            browser.close()
            
            # Find the ms-playwright directory
            # Typical path: C:\Users\USER\AppData\Local\ms-playwright
            import subprocess
            result = subprocess.run(
                [sys.executable, "-c", 
                 "from playwright.sync_api import sync_playwright; "
                 "import os; "
                 "p = sync_playwright().start(); "
                 "exe = p.chromium.executable_path; "
                 "p.stop(); "
                 "print(os.path.dirname(os.path.dirname(exe)))"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                browser_dir = Path(result.stdout.strip())
                
                # Go up to find ms-playwright folder
                while browser_dir.name != "ms-playwright" and browser_dir.parent != browser_dir:
                    browser_dir = browser_dir.parent
                
                if browser_dir.name == "ms-playwright" and browser_dir.exists():
                    return browser_dir
            
            # Fallback: check common locations
            common_paths = [
                Path.home() / "AppData" / "Local" / "ms-playwright",
                Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright",
            ]
            
            for path in common_paths:
                if path.exists():
                    return path
                    
    except Exception as e:
        print(f"Error finding Playwright browsers: {e}")
    
    return None

def copy_browsers_to_dist(dist_folder="dist/WorkFlowTool"):
    """Copy Playwright browsers to dist folder"""
    dist_path = Path(dist_folder)
    
    if not dist_path.exists():
        print(f"[ERROR] Dist folder not found: {dist_path}")
        return False
    
    # Find browsers
    print("[INFO] Finding Playwright browsers...")
    browser_dir = find_playwright_browsers()
    
    if not browser_dir:
        print("[ERROR] Playwright browsers not found!")
        print("        Please run: playwright install chromium")
        return False
    
    print(f"[OK] Found browsers at: {browser_dir}")
    
    # Create _external folder
    external_dir = dist_path / "_external"
    external_dir.mkdir(exist_ok=True)
    
    # Destination path
    dest_dir = external_dir / "ms-playwright"
    
    # Remove old browsers if exists
    if dest_dir.exists():
        print(f"[INFO] Removing old browsers...")
        shutil.rmtree(dest_dir)
    
    # Copy browsers
    print(f"[INFO] Copying browsers to: {dest_dir}")
    print("       This may take a few minutes...")
    
    try:
        shutil.copytree(browser_dir, dest_dir)
        
        # Calculate size
        total_size = sum(
            f.stat().st_size 
            for f in dest_dir.rglob('*') 
            if f.is_file()
        )
        
        size_mb = total_size / (1024 * 1024)
        print(f"[OK] Browsers copied successfully! ({size_mb:.1f} MB)")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error copying browsers: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  Playwright Browsers Copy Tool")
    print("=" * 50)
    print()
    
    success = copy_browsers_to_dist()
    
    print()
    if success:
        print("=" * 50)
        print("  SUCCESS!")
        print("=" * 50)
        print()
        print("The application is ready to distribute.")
        print("Copy entire 'dist/WorkFlowTool' folder to target machine.")
    else:
        print("=" * 50)
        print("  FAILED!")
        print("=" * 50)
        print()
        print("Please install Playwright browsers first:")
        print("  playwright install chromium")
    
    print()
    input("Press Enter to exit...")

