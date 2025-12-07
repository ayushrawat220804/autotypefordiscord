#!/usr/bin/env python3
"""
Build script to convert God_owo_discordbot.py into a standalone executable.
This script handles all dependencies and creates a distributable package.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        print("✓ PyInstaller is already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file with optimized settings."""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['God_owo_discordbot.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'pyautogui',
        'keyboard',
        'threading',
        'time',
        'random',
        'json',
        'datetime',
        'typing',
        'pathlib',
        'sys',
        'os'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='God_owo_discordbot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
    version_file=None,
)
'''
    
    with open('God_owo_discordbot.spec', 'w') as f:
        f.write(spec_content)
    print("✓ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    try:
        # Clean previous builds
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('dist'):
            shutil.rmtree('dist')
        
        # Build with spec file
        cmd = [sys.executable, "-m", "PyInstaller", "--clean", "God_owo_discordbot.spec"]
        subprocess.check_call(cmd)
        print("✓ Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False

def create_distribution_package():
    """Create a distribution package with documentation."""
    dist_dir = Path("dist_package")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Copy executable
    exe_path = Path("dist/God_owo_discordbot.exe")
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / "God_owo_discordbot.exe")
        print("✓ Copied executable to distribution package")
    
    # Create README for distribution
    readme_content = """# God OwO Discord Bot - Executable Version

## Quick Start
1. Double-click `God_owo_discordbot.exe` to run
2. No Python installation required!

## Features
- Simple Bot Mode: One-click automation with 5 core commands
- Advanced Bot Mode: Full configuration with 4 command categories
- Hotkey Support: Ctrl+P to toggle start/stop
- Dry-run Mode: Test commands without typing
- Safety Features: Rate limiting, failsafe, ToS warnings

## Usage
1. **Simple Mode**: Click "Start Simple Bot" - no configuration needed
2. **Advanced Mode**: Configure commands, intervals, and modes as needed
3. **Hotkey**: Press Ctrl+P to toggle the currently selected mode
4. **Safety**: Always read ToS warnings before starting automation

## Requirements
- Windows 10/11 (tested)
- Discord application must be open and focused
- Administrator privileges may be required for some features

## Safety Notice
- This tool automates Discord commands
- Use responsibly and follow Discord's Terms of Service
- Start with dry-run mode to test
- Use minimum 5-second intervals
- Monitor your Discord account for any issues

## Troubleshooting
- If the GUI doesn't appear, try running as administrator
- For keyboard issues, ensure Discord is the active window
- If commands don't work, check Discord is focused and not minimized

## Support
- Check the built-in help section in the application
- Use dry-run mode to test before real automation
- Start with simple mode for basic functionality

Version: 1.1
Built with PyInstaller
"""
    
    with open(dist_dir / "README.txt", 'w') as f:
        f.write(readme_content)
    
    # Copy additional documentation if available
    docs_to_copy = ["USAGE_GUIDE.md", "DELIVERY_SUMMARY.md", "IMPROVEMENTS_v1.1.md"]
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy2(doc, dist_dir)
    
    print("✓ Created distribution package")
    return dist_dir

def main():
    """Main build process."""
    print("=== God OwO Discord Bot - Executable Builder ===\n")
    
    # Check if source file exists
    if not os.path.exists("God_owo_discordbot.py"):
        print("✗ God_owo_discordbot.py not found in current directory")
        return False
    
    # Step 1: Check/install PyInstaller
    if not check_pyinstaller():
        return False
    
    # Step 2: Create spec file
    create_spec_file()
    
    # Step 3: Build executable
    if not build_executable():
        return False
    
    # Step 4: Create distribution package
    dist_dir = create_distribution_package()
    
    print(f"\n=== BUILD COMPLETE ===")
    print(f"✓ Executable: dist/God_owo_discordbot.exe")
    print(f"✓ Distribution package: {dist_dir}/")
    print(f"✓ Size: {os.path.getsize('dist/God_owo_discordbot.exe') / (1024*1024):.1f} MB")
    
    print(f"\n=== NEXT STEPS ===")
    print("1. Test the executable: dist/God_owo_discordbot.exe")
    print("2. Distribute the entire 'dist_package' folder")
    print("3. Users can run God_owo_discordbot.exe directly")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)

