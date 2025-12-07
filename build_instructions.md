# Building God OwO Discord Bot Executable

**Made with ❤️ by Aditi and Ayush**

## Quick Build (Windows)

1. **Double-click `build_exe.bat`** - This will automatically:
   - Install all required dependencies
   - Build the executable using PyInstaller
   - Create `dist\God_Owo_DiscordBot.exe`

## Manual Build Steps

### Prerequisites
- Python 3.10 or higher installed
- pip package manager

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Build Executable
```bash
# Using the spec file (recommended)
pyinstaller build_exe.spec

# OR using command line directly
pyinstaller --onefile --windowed --name "God_Owo_DiscordBot" God_owo_discordbot.py
```

### Step 3: Find Your Executable
The executable will be created in the `dist` folder:
- `dist\God_Owo_DiscordBot.exe`

## Notes

- The executable is a single file (--onefile flag)
- No console window will appear (--windowed flag)
- The first run may be slower as files are extracted
- Antivirus software may flag it initially (false positive) - this is normal for PyInstaller executables

## Troubleshooting

**If build fails:**
1. Make sure Python 3.10+ is installed: `python --version`
2. Update pip: `python -m pip install --upgrade pip`
3. Install dependencies manually: `pip install pyautogui keyboard pillow pyinstaller`

**If executable doesn't run:**
1. Check Windows Defender/Antivirus isn't blocking it
2. Try running as administrator
3. Check that all dependencies are included

## File Sizes

- Source Python file: ~50 KB
- Executable: ~15-25 MB (includes Python runtime and all dependencies)
