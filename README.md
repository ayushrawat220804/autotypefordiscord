# Discord Auto Typer - 100 WPM

A simple Python program that automatically types text in Discord at 100 words per minute with customizable settings.

## Features

- **100 Words Per Minute**: Types at exactly 100 WPM (0.6 seconds per word)
- **Customizable Words Per Line**: Set 6-10 words per line before pressing Enter
- **Multiple Content Types**:
  - Sample paragraphs
  - Cross-talk conversations between two characters
  - Generated 1000-word paragraph
  - Generated 10000-word comprehensive passage
- **Repeat Functionality**: Automatically repeats the content when finished
- **Easy Controls**: Start/Stop and Repeat buttons
- **Content Preview**: See what will be typed before starting

## Installation

1. Install Python 3.7 or higher
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the program:
   ```bash
   python autotype_discord.py
   ```

2. Configure settings:
   - Set words per line (6-10)
   - Select content type (sample, cross_talk, generated_1k, or generated_10k)

3. Open Discord and focus on the chat window

4. Click "Start Typing" - the program will wait 3 seconds before starting

5. Use "Repeat" to restart the content when finished

## OwO Auto Typer

Three versions available with increasing features:

### 1. Original Version (`owo_autotyper.py`)
Basic functionality with simple command automation.

### 2. Refactored Version (`owo_autotyper_refactored.py`)
Improved scheduling, cleaner code, better UI.

### 3. **Enhanced Version (`owo_autotyper_enhanced.py`)** ⭐ RECOMMENDED
Production-ready with extensive features.

### Run Enhanced Version

```bash
python owo_autotyper_enhanced.py
```

### Enhanced Features ✨
- **Bug Fixes**: All critical bugs from previous versions fixed
- **Configuration System**: Save/load settings as JSON profiles
- **Statistics Dashboard**: Track commands sent, runtime, success rates
- **Pause/Resume**: Pause without losing progress (Ctrl+Space)
- **Cooldown Tracking**: Live countdown display for pray, daily, hunt, battle
- **Focus Detection**: Auto-pause when Discord loses focus (Windows/Linux)
- **Comprehensive Logging**: File logging with export functionality
- **Human-like Behavior**: 
  - Typing speed variance (±20%)
  - Random typos with corrections (5% chance)
  - Random pauses (2% chance)
  - Anti-pattern randomization
- **Advanced UI**: Tabbed interface with Statistics, Settings, and Logs
- **Error Handling**: Robust error recovery and reporting
- **Multiple Modes**:
  - Minute Plan: 4 hunt, 5 cf, 3 slots, 2 bj per minute
  - Cash Farm: Hunt → Sell cycle with optional coinflips
  - Per-Command: Individual scheduling for each command type
- **Safety Features**:
  - Maximum 24-hour runtime limit
  - Minimum 3-second interval enforcement
  - Focus validation before typing
  - Emergency stop mechanisms
  - Clean shutdown handling

### Hotkeys
- **Ctrl+P**: Toggle Start/Stop
- **Ctrl+Space**: Toggle Pause/Resume (when running)

### Tips
- Open Discord and focus the desired channel before starting
- Keep intervals reasonable to avoid rate limits
- Use pause/resume for temporary breaks
- Check logs tab for debugging information
- Export statistics to track your usage patterns
- Save your favorite configurations for quick loading

### Configuration Files
All data stored in `~/.owo_autotyper/`:
- `config.json` - Your settings
- `statistics.json` - Usage statistics
- `autotyper.log` - Application logs

### Optional Dependencies
For enhanced focus detection:
- **Windows**: `pip install pywin32`
- **Linux**: Install `xdotool` package

See `IMPROVEMENTS.md` for complete feature documentation.

## Controls

- **Start Typing**: Begins the auto-typing process
- **Stop Typing**: Stops the current typing session
- **Repeat**: Restarts the content from the beginning

## Safety Features

- 3-second delay before starting to allow you to focus on Discord
- Easy stop functionality
- Error handling for unexpected issues

## Content Types

### Sample
Short paragraphs about various topics like technology, music, and life.

### Cross Talk
Conversations between two characters (Alice and Bob) discussing projects and collaboration.

### Generated 1K
A randomly generated 1000-word paragraph covering various topics like technology, science, nature, and philosophy.

### Generated 10K
A comprehensive 10000-word passage covering extensive topics including technology, science, society, philosophy, economics, environment, arts, and health. This provides substantial content for extended typing sessions.

## Notes

- Make sure Discord is open and focused before starting
- The program types at exactly 100 WPM (0.6 seconds per word)
- Press Ctrl+P to stop typing at any time
- Each line contains 6-10 words (configurable) followed by Enter
