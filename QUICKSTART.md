# OwO Auto Typer - Quick Start Guide

## Installation

1. **Install Python 3.7+**

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Enable Focus Detection**
   - **Windows**: `pip install pywin32`
   - **Linux**: `sudo apt install xdotool` (or equivalent)

## First Run

```bash
python owo_autotyper_enhanced.py
```

## Basic Usage

### Quick Start (Minute Plan Mode)
1. Leave "Minute Plan" enabled (default)
2. Set run duration (default: 1 hour)
3. Click **Start**
4. Click "Yes" on the ToS warning
5. Alt-Tab to Discord within 3 seconds
6. Watch the magic happen!

### Cash Farm Mode
1. Disable "Minute Plan"
2. Enable "Cash Farm"
3. Set "Hunts per sell" (default: 10)
4. Optional: Enable "Tiny CF sometimes"
5. Click **Start**
6. Switch to Discord

### Custom Per-Command Mode
1. Disable both "Minute Plan" and "Cash Farm"
2. Enable specific commands (hunt, coinflip, slots, battle, pray)
3. Set individual intervals for each command
4. Click **Start**
5. Switch to Discord

## Hotkeys

- **Ctrl+P**: Start/Stop the auto typer
- **Ctrl+Space**: Pause/Resume (when running)

## Tabs Overview

### Main Controls
- Configure run mode (duration or iterations)
- Select automation mode (Minute Plan, Cash Farm, or Custom)
- Set command intervals
- View cooldown timers
- Control buttons (Start, Pause, Stop)
- Preview of current configuration

### Statistics
- View total commands sent
- See runtime statistics
- Command breakdown by type
- Error and focus loss tracking
- Export statistics

### Advanced Settings
- Enable/disable human-like behaviors:
  - Typing speed variance
  - Random typos with corrections
  - Random pauses
- Configure focus detection
- View safety limits

### Logs
- View application logs in real-time
- Refresh logs
- Clear logs
- Export logs for debugging

## Safety Features

### Built-in Protections
- ✅ Minimum 3-second interval (enforced)
- ✅ Maximum 24-hour runtime (enforced)
- ✅ Focus detection and auto-pause
- ✅ Emergency stop mechanisms
- ✅ ToS acceptance warning

### Best Practices
1. **Start with conservative intervals** (15+ seconds)
2. **Test with short durations first** (5-10 minutes)
3. **Monitor the first session** to ensure correct behavior
4. **Use focus detection** to prevent accidents
5. **Keep logs enabled** for troubleshooting
6. **Respect rate limits** - don't spam!

## Common Scenarios

### "I want to farm while AFK"
```
Mode: Cash Farm
Hunts per sell: 10
Tiny CF: Enabled
CF every N hunts: 7
Duration: 2 hours
```

### "I want balanced command execution"
```
Mode: Minute Plan
Duration: 1 hour
(Uses optimal mix of commands)
```

### "I want to focus on hunting"
```
Mode: Per-Command
Enable: Hunt only
Interval: 15 seconds
Duration: 30 minutes
```

### "I want to gamble safely"
```
Mode: Per-Command
Enable: Coinflip, Slots
Intervals: 20 seconds each
Duration: 1 hour
```

## Troubleshooting

### "Commands not sending"
- ✅ Check Discord window is focused
- ✅ Verify you clicked in the text channel
- ✅ Check logs for errors
- ✅ Ensure focus detection isn't pausing

### "Too fast/slow"
- ✅ Adjust base interval
- ✅ Check per-command intervals
- ✅ Disable human variance for consistent speed

### "Auto-pausing unexpectedly"
- ✅ Disable "Auto-pause on focus loss" in Advanced Settings
- ✅ Keep Discord window focused
- ✅ Check focus detection is working correctly

### "Typos in commands"
- ✅ Disable "Random typos" in Advanced Settings
- ✅ This is intentional human-like behavior
- ✅ Commands are corrected automatically

### "Can't stop"
- ✅ Click Stop button
- ✅ Press Ctrl+P
- ✅ Close the application window
- ✅ All methods will stop safely

## Configuration

### Saving Your Settings
1. Configure all desired settings
2. Click **Save Config** button
3. Config saved to `~/.owo_autotyper/config.json`
4. Loaded automatically on next start

### Sharing Configurations
1. Click **Save Config**
2. Navigate to `~/.owo_autotyper/`
3. Copy `config.json` to share
4. Others: Click **Load Config** and select the file

## Statistics & Logs

### Viewing Statistics
- Switch to **Statistics** tab
- See comprehensive session data
- Export as JSON or TXT for analysis

### Checking Logs
- Switch to **Logs** tab
- View last 500 log lines
- Refresh to see latest entries
- Export for troubleshooting

### Data Location
All data stored in your home directory:
```
~/.owo_autotyper/
├── config.json          # Your settings
├── statistics.json      # Usage statistics  
└── autotyper.log       # Application logs
```

## Advanced Tips

### Maximize Randomness
Enable all human-like features:
- ✅ Typing speed variance
- ✅ Random typos
- ✅ Random pauses

This makes your usage less detectable!

### Optimize for Efficiency
Disable variance features:
- ❌ Typing speed variance
- ❌ Random typos
- ❌ Random pauses

Commands execute faster and more consistently.

### Monitor Performance
1. Run for 10 minutes
2. Check Statistics tab
3. Note commands per minute rate
4. Adjust intervals as needed

### Debug Issues
1. Check Logs tab for errors
2. Export logs if needed
3. Lower intervals if commands missed
4. Enable focus detection if accidental typing

## Warning

⚠️ **IMPORTANT**: Automating Discord may violate:
- Discord Terms of Service
- Server rules
- Bot usage policies

**Use at your own risk!** Account bans are possible.

### Responsible Use
- ✅ Use reasonable intervals (15+ seconds)
- ✅ Don't run 24/7
- ✅ Respect server rules
- ✅ Monitor your usage
- ✅ Stop if asked by moderators

## Getting Help

### Check These First
1. Read this guide
2. Check `IMPROVEMENTS.md` for feature details
3. Review logs for error messages
4. Verify Discord is open and focused

### Still Stuck?
- Review the logs in Logs tab
- Export logs and statistics
- Check GitHub issues (if available)

## Update Notes

**Enhanced Version** includes:
- All bugs from previous versions fixed
- 10+ major new features
- Comprehensive safety mechanisms
- Production-ready code quality

See `IMPROVEMENTS.md` for complete changelog.

---

**Happy automating!** 🎮

*Remember: Use responsibly and respect Discord's Terms of Service.*
