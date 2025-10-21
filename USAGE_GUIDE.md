# God OwO Discord Bot - Usage Guide

## 📦 What Was Delivered

A single, production-ready file: **`God_owo_discordbot.py`** (1410 lines)

This file merges and improves upon:
- `owo_autotyper_enhanced.py` from GitHub
- `SimpleOwoAutoTyper` (your pasted code)

## ✅ All Requirements Met

### Core Features
- ✅ **Two Main Modes**:
  - **Simple Bot**: One-click, 5 hardcoded commands, 15s interval (no config needed)
  - **Advanced Bot**: Configurable command sets, intervals, modes, WPM, target user
- ✅ **Modern Responsive tkinter GUI** with tabs (Main Controls, Statistics, Logs, Help)
- ✅ **Type hints everywhere** (Python 3.10+ compatible, tested for 3.12)
- ✅ **Comprehensive docstrings** for all public methods and classes
- ✅ **Thread-safe** with proper `threading.Event` usage and clean shutdown
- ✅ **Graceful shutdown**: Removes hotkeys, joins threads, saves stats
- ✅ **Single-file deliverable**: Everything in one file, ready to run

### Safety & Robustness
- ✅ **Minimum interval enforcement**: 5s default, validated before start
- ✅ **ToS warning dialog**: Explicit acceptance required before starting
- ✅ **Dry-run / Preview mode**: Shows commands without typing
- ✅ **pyautogui.FAILSAFE**: Enabled (move mouse to corner to abort)
- ✅ **Error handling**: Try/except blocks with logging for all pyautogui calls
- ✅ **Dependency check**: Shows installation dialog if missing deps
- ✅ **Rate limiting**: Configurable intervals with minimum enforcement

### UX & Controls
- ✅ **Hotkey support**: Ctrl+P toggles start/stop for current mode
- ✅ **Start / Stop / Pause** buttons for each mode
- ✅ **Status display**: Shows current state, next command, countdown
- ✅ **Command preview**: Shows next command before typing
- ✅ **Recent commands log**: Shows last 50 commands with timestamps
- ✅ **Statistics tracking**: Total commands, runtime, sessions, errors
- ✅ **Comprehensive logging**: File-based logging with export/clear options

### Testing & Verification
- ✅ **--self-test mode**: Run unit tests without GUI (`python God_owo_discordbot.py --self-test`)
- ✅ **Pure functions**: Testable command generation functions
- ✅ **No syntax errors**: Verified with `python -m py_compile`
- ✅ **No linter errors**: Clean code, passes linter checks

### Code Quality
- ✅ **Type hints**: All functions have proper type annotations
- ✅ **Docstrings**: Every class and public method documented
- ✅ **Clean structure**: Classes (`GodOwoBotApp`, `BotStats`), helper functions
- ✅ **No global mutable state**: State encapsulated in class instances
- ✅ **Credits & sources**: Header includes original source URLs and changelog

## 🚀 Installation

### Dependencies
```bash
pip install pyautogui keyboard pillow
```

**Note**: The `keyboard` library requires administrator/root privileges on some systems.

### Platform Compatibility
- ✅ **Windows**: Full support (Python 3.10+)
- ✅ **Linux**: Full support (Python 3.10+, may need `python3-tk`)
- ⚠️ **macOS**: pyautogui works, but keyboard may have limitations

## 📖 How to Run

### Normal Mode (GUI)
```bash
python God_owo_discordbot.py
```
or
```bash
python3 God_owo_discordbot.py
```

### Self-Test Mode (Unit Tests)
```bash
python God_owo_discordbot.py --self-test
```

## 🎮 Using the Bot

### Simple Mode (Recommended for Beginners)
1. Click **"Start Simple Bot"**
2. Accept the ToS warning
3. Focus the Discord message box
4. The bot will run these 5 commands every 15 seconds:
   - `owo hunt`
   - `owo coinflip [1-500]`
   - `owo slots [1-500]`
   - `owo battle`
   - `owo cash`

### Advanced Mode (For Power Users)
1. Configure settings:
   - Base interval (min 5s)
   - Enable Ultra Mode (action commands)
   - Enable Meme Mode (meme generation)
   - Enable Utility Mode (ping, stats, rules)
   - Random prefix mode (owo/o)
   - Typing speed (WPM)
   - Target user for give/clover/cookie
2. Click **"Start Advanced Bot"**
3. Accept the ToS warning
4. Focus Discord message box

### Dry Run Mode (Testing)
1. Check the **"Dry Run"** checkbox
2. Start either mode
3. Commands will be logged but NOT typed
4. Perfect for testing configurations safely

## ⌨️ Hotkeys
- **Ctrl+P**: Toggle start/stop for current mode
- **Move mouse to corner**: Emergency abort (pyautogui failsafe)

## 📊 Statistics & Logs
- **Statistics Tab**: View total commands sent, runtime, sessions, errors
- **Logs Tab**: View application logs with timestamps
- **Recent Commands**: See last 50 commands in main window

## ⚠️ Discord ToS Warnings

### Critical Warnings
- ⚠️ **Automating Discord input may VIOLATE Discord Terms of Service**
- ⚠️ **Using this bot may result in account suspension or ban**
- ⚠️ **This tool is for EDUCATIONAL PURPOSES ONLY**
- ⚠️ **Use responsibly and at your own risk**

### Safer Alternatives (Recommended)
Instead of automation, consider:
1. **Official Discord Bot API**: https://discord.com/developers/docs (LEGAL)
2. **Manual command execution**: Type commands yourself
3. **Server-approved automation**: Get explicit permission from server admins
4. **Rate-limited bots**: Use proper Discord bot framework

### What the Bot Does to Mitigate Risk
- ✅ Enforces minimum 5s interval (prevents spam)
- ✅ Shows ToS warning before every start
- ✅ Logs all actions for transparency
- ✅ Dry-run mode for testing without risk
- ✅ Graceful shutdown to prevent hanging processes

## 🐛 Bug Fixes Applied

From your requirements, here are the bugs that were fixed:

1. ✅ **Thread safety**: Worker threads use `threading.Event` and are cleanly joined on stop
2. ✅ **Hotkey leaks**: `keyboard.unhook_all()` called on exit to remove hotkeys
3. ✅ **Stop event checks**: pyautogui loops check stop event between operations
4. ✅ **UI thread safety**: All UI operations from worker threads use `root.after()`
5. ✅ **Unique amount loops**: Max retries (10) to prevent infinite loops
6. ✅ **No time.sleep in UI thread**: Worker threads use `_calm_sleep()` with event checks
7. ✅ **Deduplicated code**: No duplicate blocks (merged cleanly)
8. ✅ **Fixed typos**: Consistent command spacing and formatting
9. ✅ **Ctrl+P behavior**: Documented that it toggles current mode

## 📝 Test Checklist

Before running on Discord:
- [ ] Run `python God_owo_discordbot.py --self-test` (should pass all tests)
- [ ] Start Simple Mode with **Dry Run** enabled
- [ ] Verify commands appear in log but are NOT typed
- [ ] Test Ctrl+P hotkey (start/stop toggle)
- [ ] Test Pause button
- [ ] Test Stop button
- [ ] Check Statistics tab shows correct counts
- [ ] Disable Dry Run and test with a single 15s cycle in a test channel
- [ ] Verify minimum interval enforcement (try setting interval to 3s, should error)
- [ ] Check logs for any errors

## 🔧 Troubleshooting

### "Missing Dependencies" error
```bash
pip install pyautogui keyboard pillow
```

### Keyboard library requires admin
- **Windows**: Run terminal as Administrator
- **Linux**: May need `sudo` or add user to input group

### No module named 'tkinter'
- **Linux**: `sudo apt-get install python3-tk`
- **macOS**: Should be included with Python

### Bot types in wrong window
- Make sure Discord message box is focused before starting
- Use Dry Run mode first to verify commands

### Hotkey (Ctrl+P) doesn't work
- Keyboard library may require elevated privileges
- Try running with sudo/admin
- Or use GUI buttons instead

## 📂 File Structure

```
/workspace/
├── God_owo_discordbot.py  (Main file - 1410 lines)
├── USAGE_GUIDE.md         (This file)
└── ~/.god_owo_bot/        (Created on first run)
    ├── bot.log            (Application logs)
    └── stats.json         (Statistics)
```

## 🎯 Architecture Overview

### Classes
- **`GodOwoBotApp`**: Main application class, handles GUI and bot logic
- **`BotStats`**: Dataclass for statistics tracking

### Key Methods
- `_start_simple_mode()`: Launches Simple Bot
- `_start_advanced_mode()`: Launches Advanced Bot
- `_run_simple_mode()`: Worker thread for Simple Mode
- `_run_advanced_mode()`: Worker thread for Advanced Mode
- `_generate_simple_command()`: Pure function for command generation
- `_type_and_send()`: Types command with human-like timing
- `_calm_sleep()`: Sleep with frequent event checks

### Pure Functions (Unit Tested)
- `_generate_unique_amount()`: Generates unique random amounts
- `_generate_simple_command()`: Command generation for Simple Mode
- `_generate_advanced_command()`: Command generation for Advanced Mode

## 🔐 Security Notes

1. **No network requests**: Bot only types locally (no external connections)
2. **No credential storage**: No passwords or tokens stored
3. **Transparent logging**: All actions logged to file
4. **Open source**: Single file, easy to audit
5. **No obfuscation**: Clean, readable Python code

## 📈 Future Enhancements (Out of Scope)

These were considered but not implemented (you can add if needed):
- Focus detection (requires win32gui on Windows, xdotool on Linux)
- GUI theming / dark mode
- Configuration profiles (save/load multiple configs)
- Advanced scheduling (cron-like)
- OCR-based Discord response detection
- Multi-server support

## 📄 License & Credits

- **License**: Use at your own risk (no warranty)
- **Original sources**:
  - https://github.com/ayushrawat220804/autotypefordiscord/blob/cursor/refine-discord-auto-typer-script-1ef8/owo_autotyper_enhanced.py
  - SimpleOwoAutoTyper (user-provided enhanced version)
- **Merged and enhanced by**: AI Assistant (Claude Sonnet 4.5)
- **Date**: 2025-10-21

## ❓ Support

For issues or questions:
1. Check this usage guide
2. Run `--self-test` mode
3. Check application logs in `~/.god_owo_bot/bot.log`
4. Review source code (heavily commented)

## ⚖️ Legal Disclaimer

By using this software, you acknowledge and agree that:
1. You are solely responsible for your actions
2. The authors are not liable for any damages or consequences
3. You will comply with all applicable laws and terms of service
4. This is for educational purposes only

**USE AT YOUR OWN RISK. YOU HAVE BEEN WARNED.**

---

**Enjoy responsibly! 🎮**
