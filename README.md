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

## OwO Auto Typer (new)

An additional utility is provided to automatically send OwO bot commands at a fixed interval.

### Run

```bash
python owo_autotyper.py
```

### Features
- Select categories: Economy, Animals/Hunt, Gambling
- Default interval 15 seconds (configurable 5–120s)
- Random command selection each interval
- Sends command and presses Enter automatically
- Start/Stop controls with global hotkey Ctrl+P to stop

### Tips
- Open Discord and focus the desired channel before starting
- Keep the interval reasonable to avoid spam limits

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
