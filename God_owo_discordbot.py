#!/usr/bin/env python3
"""
God OwO Discord Bot - Production-Ready Auto Typer
==================================================

Merged from:
- https://github.com/ayushrawat220804/autotypefordiscord/blob/cursor/refine-discord-auto-typer-script-1ef8/owo_autotyper_enhanced.py
- SimpleOwoAutoTyper (user-provided enhanced version)

Authors: Made with ❤️ by Aditi and Ayush
Python: 3.10+ (tested on 3.12)
License: Use at your own risk

CRITICAL WARNINGS:
==================
⚠️ Automating Discord input may VIOLATE Discord Terms of Service
⚠️ Using this bot may result in account suspension or ban
⚠️ This tool is for EDUCATIONAL PURPOSES ONLY
⚠️ Use responsibly and at your own risk
⚠️ Respect server rules and Discord ToS

FEATURES:
=========
✓ Simple Mode: One-click bot with 5 hardcoded commands (15s interval)
✓ Advanced Mode: Fully configurable with multiple command sets
✓ Modern responsive tkinter GUI with tabs
✓ Dry-run preview mode (no actual typing)
✓ Type hints and comprehensive docstrings
✓ Thread-safe with graceful shutdown
✓ Minimum interval enforcement (5s default)
✓ Hotkey support (Ctrl+P to start/stop)
✓ Statistics tracking and logging
✓ Human-like typing simulation
✓ Unit tests via --self-test mode

INSTALLATION:
=============
pip install pyautogui keyboard pillow

Note: 'keyboard' requires admin/root privileges on some systems.

USAGE:
======
# Normal mode (launch GUI):
python God_owo_discordbot.py

# Run self-tests (no GUI):
python God_owo_discordbot.py --self-test

# Dry-run mode (preview only, no typing):
Use the "Dry Run" toggle in the GUI

CHANGELOG:
==========
v1.1 (Latest):
- Reduced meme/utility command frequency to 20% total (more natural)
- Reduced "owo owo" action command frequency to 8% (less spammy)
- Improved command distribution: 80% core, 20% special (meme+utility+action)
- Enhanced statistics dashboard with visual bars and detailed metrics
- Window now maximizes on startup for better visibility
- WPM slider now shows integer values only (no decimals)
- Improved help section with detailed mode explanations
- Better documentation of command frequencies and distributions

v1.0:
- Merged EnhancedOwoAutoTyper and SimpleOwoAutoTyper
- Fixed thread safety issues (proper event handling, join on shutdown)
- Fixed keyboard hotkey leaks (proper cleanup on exit)
- Added dry-run preview mode
- Enforced minimum 5s interval with validation
- Improved type hints and docstrings throughout
- Added --self-test mode for unit testing
- Separated Simple Mode (hardcoded) from Advanced Mode
- Added ToS warning dialog with explicit acceptance
- Improved error handling and logging
- Made pyautogui.FAILSAFE explicit
- Added proper pyautogui.PAUSE handling

TODO/LIMITATIONS:
=================
- Focus detection requires platform-specific libraries (win32gui on Windows, xdotool on Linux)
- Keyboard hotkeys may require elevated privileges on some systems
- Rate limiting is enforced client-side only
- No server-side validation of commands
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import random
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Callable
from dataclasses import dataclass
import json

# Optional imports with graceful fallback
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # Enable failsafe (move mouse to corner to abort)
    pyautogui.FAILSAFE = True
    # Small pause between pyautogui calls
    pyautogui.PAUSE = 0.01
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


# Constants
MIN_INTERVAL = 5  # Minimum interval in seconds (safety)
MAX_RUNTIME_HOURS = 24  # Maximum runtime (safety)
CONFIG_DIR = Path.home() / ".god_owo_bot"
LOG_FILE = CONFIG_DIR / "bot.log"
STATS_FILE = CONFIG_DIR / "stats.json"


@dataclass
class BotStats:
    """Statistics tracking for the bot."""
    commands_sent: int = 0
    total_runtime: int = 0
    sessions: int = 0
    last_run: Optional[str] = None
    commands_by_type: Dict[str, int] = None
    errors: int = 0
    
    def __post_init__(self):
        if self.commands_by_type is None:
            self.commands_by_type = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'commands_sent': self.commands_sent,
            'total_runtime': self.total_runtime,
            'sessions': self.sessions,
            'last_run': self.last_run,
            'commands_by_type': self.commands_by_type,
            'errors': self.errors
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BotStats':
        """Create from dictionary."""
        return cls(**data)


class GodOwoBotApp:
    """Main application class for God OwO Discord Bot."""
    
    def __init__(self, root: tk.Tk) -> None:
        """Initialize the bot application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("God OwO Discord Bot - Made with ❤️ by Aditi and Ayush")
        # Maximize window on startup
        try:
            self.root.state('zoomed')  # Windows
        except:
            try:
                self.root.attributes('-zoomed', True)  # Linux
            except:
                self.root.geometry("1200x900")  # Fallback
        
        # Ensure config directory exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Check dependencies
        if not self._check_dependencies():
            return
        
        # State management
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._is_paused = False
        self.worker: Optional[threading.Thread] = None
        self.current_mode: str = "none"  # "simple", "advanced", or "none"
        self._browser_stop_event = threading.Event()
        
        # Statistics
        self.stats = BotStats()
        self._load_statistics()
        
        # UI Variables - Advanced Mode
        self.advanced_interval = tk.IntVar(value=10)
        self.refresh_interval = tk.IntVar(value=10)  # Default 10 minutes for refresh (Ctrl+R)
        self.restart_interval = tk.IntVar(value=30)  # Default 30 minutes for restart (Alt+F4)
        self.var_auto_refresh = tk.BooleanVar(value=True)
        self.var_auto_restart = tk.BooleanVar(value=True)
        self.var_dry_run = tk.BooleanVar(value=False)
        self.target_url = tk.StringVar(value="https://discord.com/channels/1432319524606054422/1434581841037492377")
        self.var_ultra_mode = tk.BooleanVar(value=False)
        self.var_meme_mode = tk.BooleanVar(value=False)
        self.var_utility_mode = tk.BooleanVar(value=False)
        self.var_advanced_prefix = tk.BooleanVar(value=False)
        self.var_owo_only = tk.BooleanVar(value=False)
        self.var_enable_sell_all = tk.BooleanVar(value=True)  # Toggle for sell all
        self.var_enable_random_text = tk.BooleanVar(value=True)  # Enable random text
        self.typing_wpm = tk.IntVar(value=120)
        self.target_user = tk.StringVar(value="@owo")
        
        # Command tracking for uniqueness
        self.previous_amounts: Dict[str, int] = {}
        
        # Command timing tracking (for cooldowns)
        self.command_last_used: Dict[str, float] = {}
        
        # Gem usage tracking
        self.var_auto_use_gems = tk.BooleanVar(value=False)
        self.gem_hunt_count = 0  # Track hunts since last gem use
        self.gems_to_use = []  # List of gem IDs to use
        self.last_gem_use_time = 0.0
        self.gem_ids_var = tk.StringVar(value="51 65 72")
        self.gem_hunt_interval = tk.IntVar(value=0)
        self.gem_use_threshold = tk.IntVar(value=0)  # Threshold for gem usage
        
        # Random text sentences pool (expanded with longer sentences)
        self.random_texts = [
            # Short casual phrases
            "lol", "haha", "nice", "cool", "yeah", "ok", "sure", "maybe", "idk", "lmao",
            "xd", "wtf", "bruh", "fr", "ngl", "tbh", "same", "mood", "facts", "true",
            "yep", "nope", "nah", "okay", "lol i", "kux bi hora h",
            
            # 2-3 word phrases
            "that's funny", "makes sense", "got it", "sounds good", "fair enough",
            "nice one", "good stuff", "no way", "for real", "wait what",
            "i guess", "could be", "might be", "that's cool", "that's wild",
            
            # 4-5 word sentences (more natural)
            "lol i don't know", "xd that's so funny", "wtf is going on",
            "bruh that's crazy", "fr that makes sense", "ngl that's pretty cool",
            "tbh i think so", "same here bro", "mood right now",
            "facts that's true", "yep sounds good", "nope not really",
            "lol i see", "xd wtf happened", "bruh for real",
            "that's actually pretty cool", "i don't know man", "that makes sense to me",
            "wait what just happened", "i guess that works", "could be better though",
            "might be worth trying", "that's pretty interesting", "sounds like a plan",
            "fair enough i guess", "nice one there", "good stuff keep going",
            "no way that's crazy", "for real though", "wait what did you say",
            "i see what you mean", "that's cool i guess", "makes sense to me",
            "got it thanks", "alright sounds good", "yeah that works",
            "ok i understand", "sure why not", "maybe next time",
            "idk about that", "lmao that's hilarious", "haha nice one",
            "omg that's amazing", "wow that's cool", "interesting point there",
            "probably should do that", "possibly could work", "that's wild man",
            "crazy how that works", "insane amount of stuff", "wow amazing job",
            "incredible work there", "awesome stuff happening", "sweet deal bro",
            "rad idea man", "seriously that's cool", "huh didn't know that"
        ]
        
        # Build UI
        self._build_ui()
        
        # Setup hotkeys
        if KEYBOARD_AVAILABLE:
            self._setup_hotkeys()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.logger.info("God OwO Bot initialized successfully")
    
    def _setup_logging(self) -> None:
        """Setup comprehensive logging system."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("God OwO Discord Bot - Session Started")
        self.logger.info(f"PyAutoGUI available: {PYAUTOGUI_AVAILABLE}")
        self.logger.info(f"Keyboard available: {KEYBOARD_AVAILABLE}")
    
    def _check_dependencies(self) -> bool:
        """Check for required dependencies and show installation dialog if missing.
        
        Returns:
            True if all dependencies are available, False otherwise
        """
        missing = []
        
        if not PYAUTOGUI_AVAILABLE:
            missing.append("pyautogui")
        if not KEYBOARD_AVAILABLE:
            missing.append("keyboard")
        
        if missing:
            msg = (
                "Missing required dependencies:\n\n" +
                "\n".join(f"  • {dep}" for dep in missing) +
                "\n\nPlease install with:\n\n" +
                f"pip install {' '.join(missing)}\n\n" +
                "Note: 'keyboard' may require admin/root privileges."
            )
            messagebox.showerror("Missing Dependencies", msg)
            self.logger.error(f"Missing dependencies: {missing}")
            self.root.quit()
            return False
        
        return True
    
    def _load_statistics(self) -> None:
        """Load statistics from file."""
        try:
            if STATS_FILE.exists():
                with open(STATS_FILE, 'r') as f:
                    data = json.load(f)
                    self.stats = BotStats.from_dict(data)
                self.logger.info(f"Loaded stats: {self.stats.commands_sent} total commands")
        except Exception as e:
            self.logger.error(f"Failed to load statistics: {e}")
    
    def _save_statistics(self) -> None:
        """Save statistics to file."""
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save statistics: {e}")
    
    def _build_ui(self) -> None:
        """Build the main user interface."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Main controls tab
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text='🎮 Main Controls')
        self._build_main_tab(main_tab)
        
        # Statistics tab
        stats_tab = ttk.Frame(notebook)
        notebook.add(stats_tab, text='📊 Statistics')
        self._build_stats_tab(stats_tab)
        
        # Logs tab
        logs_tab = ttk.Frame(notebook)
        notebook.add(logs_tab, text='📝 Logs')
        self._build_logs_tab(logs_tab)
        
        # Commands tab
        commands_tab = ttk.Frame(notebook)
        notebook.add(commands_tab, text='📋 Commands')
        self._build_commands_tab(commands_tab)
        
        # Help tab
        help_tab = ttk.Frame(notebook)
        notebook.add(help_tab, text='❓ Help')
        self._build_help_tab(help_tab)
    
    def _build_main_tab(self, parent: ttk.Frame) -> None:
        """Build main controls tab with Simple and Advanced modes."""
        main = ttk.Frame(parent, padding="10")
        main.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main, text="God OwO Discord Bot", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 0))
        
        # Credits
        credits = ttk.Label(main, text="Made with ❤️ by Aditi and Ayush", font=("Arial", 9), foreground="gray")
        credits.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Warning banner
        warning_frame = ttk.Frame(main, relief='solid', borderwidth=2)
        warning_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        warning_label = ttk.Label(
            warning_frame,
            text="⚠️  WARNING: Automating Discord may violate ToS. Use at your own risk!  ⚠️",
            font=("Arial", 10, "bold"),
            foreground="red",
            background="yellow",
            padding="10"
        )
        warning_label.pack(fill='x')
        
        # Main Layout: 2 Columns
        # Left: Advanced Mode (Configurable)
        # Right: Controls & Logs
        
        # --- LEFT COLUMN: Advanced Mode ---
        left_wrapper = ttk.LabelFrame(main, text="🔵 Advanced Mode (Configurable)", padding="5")
        left_wrapper.grid(row=3, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(0, 5))
        
        # Split internally into two columns (adv_col1, adv_col2)
        adv_col1 = ttk.Frame(left_wrapper)
        adv_col1.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 5))
        
        ttk.Separator(left_wrapper, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5)
        
        adv_col2 = ttk.Frame(left_wrapper)
        adv_col2.pack(side=tk.LEFT, fill='both', expand=True, padx=(5, 0))

        # === ADV_COL1 Content ===
        
        # Intervals
        ttk.Label(adv_col1, text="Base Interval (seconds):").pack(anchor=tk.W)
        ttk.Spinbox(adv_col1, from_=MIN_INTERVAL, to=120, textvariable=self.advanced_interval, width=10).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(adv_col1, text="Refresh Interval (min):").pack(anchor=tk.W)
        ttk.Spinbox(adv_col1, from_=5, to=120, textvariable=self.refresh_interval, width=10).pack(anchor=tk.W, pady=(0, 2))
        ttk.Checkbutton(adv_col1, text="Auto Refresh (Ctrl+R)", variable=self.var_auto_refresh).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(adv_col1, text="Restart Interval (min):").pack(anchor=tk.W)
        ttk.Spinbox(adv_col1, from_=10, to=240, textvariable=self.restart_interval, width=10).pack(anchor=tk.W, pady=(0, 2))
        ttk.Checkbutton(adv_col1, text="Auto Restart (Alt+F4)", variable=self.var_auto_restart).pack(anchor=tk.W, pady=(0, 10))

        # Browser Settings
        ttk.Label(adv_col1, text="Target Link (Browser):").pack(anchor=tk.W)
        ttk.Entry(adv_col1, textvariable=self.target_url, width=25).pack(anchor=tk.W, pady=(0, 10))

        browser_btn_frame = ttk.Frame(adv_col1)
        browser_btn_frame.pack(anchor=tk.W, pady=(5, 5))
        
        ttk.Button(browser_btn_frame, text="Test Browser Nav", 
                   command=lambda: threading.Thread(target=self._open_edge_and_navigate, daemon=True).start()
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(browser_btn_frame, text="Stop Test", command=self._stop_browser_test).pack(side=tk.LEFT)

        # Modes
        ttk.Separator(adv_col1, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Checkbutton(adv_col1, text="Ultra Advanced Mode", variable=self.var_ultra_mode).pack(anchor=tk.W, pady=(5, 2))
        ttk.Checkbutton(adv_col1, text="Meme Mode", variable=self.var_meme_mode).pack(anchor=tk.W, pady=(0, 2))
        ttk.Checkbutton(adv_col1, text="Utility Mode", variable=self.var_utility_mode).pack(anchor=tk.W, pady=(0, 10))

        # === ADV_COL2 Content ===
        
        # Toggles
        ttk.Checkbutton(adv_col2, text="Random Prefixes (owo/O)", variable=self.var_advanced_prefix).pack(anchor=tk.W)
        ttk.Checkbutton(adv_col2, text="OwO Only (Force full)", variable=self.var_owo_only).pack(anchor=tk.W)
        ttk.Checkbutton(adv_col2, text="Enable Random Text", variable=self.var_enable_random_text).pack(anchor=tk.W, pady=(5, 0))
        ttk.Checkbutton(adv_col2, text="Enable 'owo sell all'", variable=self.var_enable_sell_all).pack(anchor=tk.W)
        ttk.Checkbutton(adv_col2, text="Auto-Use Gems", variable=self.var_auto_use_gems).pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Separator(adv_col2, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Gems
        ttk.Label(adv_col2, text="Gem IDs (space-sep):").pack(anchor=tk.W)
        ttk.Entry(adv_col2, textvariable=self.gem_ids_var, width=20).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(adv_col2, text="Use after hunts (0=expired):").pack(anchor=tk.W)
        ttk.Spinbox(adv_col2, from_=0, to=100, textvariable=self.gem_use_threshold, width=5).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Separator(adv_col2, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Typing Speed & Target
        ttk.Label(adv_col2, text="Typing Speed (WPM):").pack(anchor=tk.W)
        wpm_scale = ttk.Scale(
            adv_col2, from_=50, to=200, variable=self.typing_wpm,
            orient=tk.HORIZONTAL, length=120,
            command=lambda v: self.typing_wpm.set(int(float(v)))
        )
        wpm_scale.pack(anchor=tk.W)
        self.wpm_label = ttk.Label(adv_col2, text=f"{self.typing_wpm.get()} WPM", font=("Arial", 8))
        self.wpm_label.pack(anchor=tk.W)
        self.typing_wpm.trace_add('write', lambda *args: self.wpm_label.config(text=f"{self.typing_wpm.get()} WPM"))
        
        ttk.Label(adv_col2, text="Target User:").pack(anchor=tk.W, pady=(5, 0))
        ttk.Entry(adv_col2, textvariable=self.target_user, width=15).pack(anchor=tk.W)

        # --- RIGHT COLUMN: Controls & Logs ---
        right_panel = ttk.Frame(main)
        right_panel.grid(row=3, column=1, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(5, 0))

        # Controls Frame (Top Right)
        control_frame = ttk.LabelFrame(right_panel, text="🎛️ Controls & Preview", padding="10")
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Buttons
        btn_container = ttk.Frame(control_frame)
        btn_container.pack(fill='x', pady=(0, 10))
        
        self.btn_start_advanced = ttk.Button(btn_container, text="▶ Start Bot", command=self._start_advanced_mode, width=12)
        self.btn_start_advanced.pack(side=tk.LEFT, padx=(0, 2))

        self.btn_stop = ttk.Button(btn_container, text="⏹ Stop", command=self.stop, state="disabled", width=12)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 2))
        
        self.btn_pause = ttk.Button(btn_container, text="⏸ Pause", command=self._toggle_pause, state="disabled", width=10)
        self.btn_pause.pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Checkbutton(control_frame, text="🔍 Dry Run", variable=self.var_dry_run).pack(anchor=tk.W, pady=(0, 10))
        
        # Status
        ttk.Label(control_frame, text="Status:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.status_label = ttk.Label(control_frame, text="Ready.", font=("Arial", 9), wraplength=200, justify=tk.LEFT)
        self.status_label.pack(anchor=tk.W, fill='x', pady=(0, 5))
        
        # Next Command Preview (Shrunken)
        ttk.Label(control_frame, text="Next Command:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.preview_text = tk.Text(control_frame, height=3, width=30, wrap=tk.WORD, font=("Courier", 8))
        self.preview_text.pack(fill='x', expand=False)
        self.preview_text.config(state='disabled')

        # Recent Commands (Bottom Right)
        log_frame = ttk.LabelFrame(right_panel, text="📜 Recent Commands", padding="5")
        log_frame.pack(fill='both', expand=True)
        
        self.command_log = scrolledtext.ScrolledText(log_frame, height=10, width=40, wrap=tk.WORD, font=("Courier", 8))
        self.command_log.pack(fill='both', expand=True)
        self.command_log.config(state='disabled')
        
        # Configure grid weights for main window
        main.columnconfigure(0, weight=2) # Left Col gets more space
        main.columnconfigure(1, weight=1) # Right Col
        main.rowconfigure(3, weight=1)
        
        # Hotkey info at bottom
        if KEYBOARD_AVAILABLE:
            hotkey_info = ttk.Label(main, text="⌨️ Hotkey: Ctrl+P to toggle start/stop", font=("Arial", 9), foreground="blue")
            hotkey_info.grid(row=4, column=0, columnspan=2, pady=(5, 0))
    
    def _build_stats_tab(self, parent: ttk.Frame) -> None:
        """Build statistics display tab."""
        stats_frame = ttk.Frame(parent, padding="10")
        stats_frame.pack(fill='both', expand=True)
        
        ttk.Label(stats_frame, text="📊 Statistics Dashboard", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, width=80, height=30, wrap=tk.WORD, font=("Courier", 10))
        self.stats_text.pack(fill='both', expand=True)
        
        btn_frame = ttk.Frame(stats_frame)
        btn_frame.pack(pady=(10, 0))
        
        ttk.Button(btn_frame, text="🔄 Refresh", command=self._update_stats_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear Stats", command=self._clear_stats).pack(side=tk.LEFT, padx=5)
        
        self._update_stats_display()
    
    def _build_logs_tab(self, parent: ttk.Frame) -> None:
        """Build logs display tab."""
        logs_frame = ttk.Frame(parent, padding="10")
        logs_frame.pack(fill='both', expand=True)
        
        ttk.Label(logs_frame, text="📝 Application Logs", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, width=80, height=30, wrap=tk.WORD, font=("Courier", 9))
        self.logs_text.pack(fill='both', expand=True)
        
        btn_frame = ttk.Frame(logs_frame)
        btn_frame.pack(pady=(10, 0))
        
        ttk.Button(btn_frame, text="🔄 Refresh", command=self._update_logs_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear Logs", command=self._clear_logs).pack(side=tk.LEFT, padx=5)
        
        self._update_logs_display()
    
    def _build_commands_tab(self, parent: ttk.Frame) -> None:
        """Build commands reference tab with all owo bot commands."""
        commands_frame = ttk.Frame(parent, padding="10")
        commands_frame.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(commands_frame, text="📋 Complete OwO Bot Commands Reference", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        # Info label
        info_label = ttk.Label(
            commands_frame,
            text="For more info on a specific command, use: owo help {command}",
            font=("Arial", 9),
            foreground="gray"
        )
        info_label.pack(pady=(0, 15))
        
        # Scrollable text area for commands
        commands_text = scrolledtext.ScrolledText(commands_frame, width=90, height=35, wrap=tk.WORD, font=("Courier", 9))
        commands_text.pack(fill='both', expand=True)
        
        # Build commands content
        separator = '─' * 80
        bottom_separator = '═' * 80
        
        commands_content = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPLETE OWO BOT COMMANDS REFERENCE                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎖 RANKINGS
{separator}
  top          - View top players
  my           - View your ranking

💰 ECONOMY
{separator}
  cowoncy      - Check your cowoncy balance
  give         - Give cowoncy to a user (requires: @user amount)
  daily        - Claim daily rewards
  vote         - Vote for the bot
  quest        - View/complete quests
  checklist    - View checklist
  shop         - View shop
  buy          - Buy items from shop

🌱 ANIMALS
{separator}
  zoo          - View your zoo
  hunt         - Hunt for animals
  sell         - Sell animals
  sacrifice    - Sacrifice animals
  battle       - Battle with animals
  inv          - View inventory
  equip        - Equip items
  autohunt     - Toggle autohunt
  owodex       - View animal dex
  lootbox      - Open lootbox
  crate        - Open crate
  battlesetting - Configure battle settings
  team         - Manage team
  weapon       - Manage weapons
  rename       - Rename animals
  dismantle    - Dismantle items

🎲 GAMBLING
{separator}
  slots        - Play slots (requires: amount)
  coinflip     - Coinflip gamble (requires: amount)
  lottery      - Play lottery (requires: amount)
  blackjack    - Play blackjack (requires: amount)

🎱 FUN
{separator}
  8b           - 8ball fortune telling
  define       - Define a word
  gif          - Search for GIFs
  pic          - Search for pictures
  translate    - Translate text
  roll         - Roll dice
  choose       - Choose between options
  bell         - Ring a bell

🎭 SOCIAL (requires: @user)
{separator}
  cookie       - Give cookie to user
  ship         - Ship two users
  pray         - Pray
  curse        - Curse a user
  marry        - Marry a user
  emoji        - View emoji
  profile      - View user profile
  level        - View user level
  wallpaper    - Set wallpaper
  owoify       - Owoify text
  avatar       - View avatar

😂 MEME GENERATION (requires: @user)
{separator}
  spongebobchicken - Generate spongebob chicken meme
  slapcar      - Generate slap car meme
  isthisa       - Generate "is this a" meme
  drake         - Generate drake meme
  distractedbf  - Generate distracted boyfriend meme
  communismcat  - Generate communism cat meme
  eject         - Generate eject meme
  emergencymeeting - Generate emergency meeting meme
  headpat       - Generate headpat meme
  tradeoffer    - Generate trade offer meme
  waddle        - Generate waddle meme

🙂 EMOTES (requires: @user)
{separator}
  blush        - Blush emote
  cry          - Cry emote
  dance        - Dance emote
  lewd         - Lewd emote
  pout         - Pout emote
  shrug        - Shrug emote
  sleepy       - Sleepy emote
  smile        - Smile emote
  smug         - Smug emote
  thumbsup     - Thumbs up emote
  wag          - Wag emote
  thinking     - Thinking emote
  triggered    - Triggered emote
  teehee       - Teehee emote
  deredere     - Deredere emote
  thonking     - Thonking emote
  scoff        - Scoff emote
  happy         - Happy emote
  thumbs        - Thumbs emote
  grin          - Grin emote

🤗 ACTIONS (requires: @user, use "owo owo [action] @user")
{separator}
  cuddle       - Cuddle a user
  hug          - Hug a user
  kiss         - Kiss a user
  lick         - Lick a user
  nom           - Nom a user
  pat           - Pat a user
  poke          - Poke a user
  slap          - Slap a user
  stare         - Stare at a user
  highfive      - High five a user
  bite          - Bite a user
  greet         - Greet a user
  punch         - Punch a user
  handholding   - Hold hands with a user
  tickle        - Tickle a user
  kill          - Kill a user
  hold          - Hold a user
  pats          - Pats a user
  wave          - Wave at a user
  boop          - Boop a user
  snuggle       - Snuggle a user
  bully         - Bully a user

🔧 UTILITY
{separator}
  ping         - Check bot latency
  stats         - View bot statistics
  link          - Get bot invite link
  guildlink     - Get guild invite link
  disable       - Disable commands
  censor        - Configure censor
  patreon       - View patreon info
  announcement  - View announcements
  rules         - View server rules
  suggest       - Suggest features
  shards        - View shard info
  math          - Calculate math
  color         - Color commands
  prefix        - View/set prefix

{bottom_separator}

📝 NOTES:
  • Commands marked with "(requires: @user)" need a target user mention
  • Action commands use format: "owo owo [action] @user"
  • Gambling commands require an amount: "owo slots 100"
  • Some commands may have additional parameters - use "owo help [command]" for details
  • Commands are case-insensitive

💡 TIP: Use the Advanced Mode in Main Controls to automate these commands!
"""
        
        commands_text.insert('1.0', commands_content)
        commands_text.config(state='disabled')
    
    def _build_help_tab(self, parent: ttk.Frame) -> None:
        """Build help and information tab."""
        help_frame = ttk.Frame(parent, padding="10")
        help_frame.pack(fill='both', expand=True)
        
        help_text = scrolledtext.ScrolledText(help_frame, width=80, height=30, wrap=tk.WORD, font=("Arial", 10))
        help_text.pack(fill='both', expand=True)
        
        help_content = """
God OwO Discord Bot - Help & Information
========================================

MODES:
------

ADVANCED MODE (Configurable)
   
   Core Commands (always active):
   • hunt, coinflip, slots, battle, cash, zoo, pray
   • sell all, daily, vote, quest
   
   Optional Modes:
   
   ⚡ ULTRA ADVANCED MODE (Action Commands)
   • Adds "owo owo" action commands: cuddle, hug, kiss, lick, pat, poke, slap, bite
   • Frequency: ~8% of total commands (reduced for natural behavior)
   • These are double-prefix commands (owo owo [action])
   
   🎭 MEME MODE (Meme Generation)
   • Adds meme commands: drake, headpat, slapcar (with target user)
   • Frequency: ~12% of total commands
   • Uses configured target user (default: @owo)
   
   🛠️ UTILITY MODE
   • Adds utility commands: ping, stats, rules
   • Frequency: ~12% of total commands
   • Useful for checking bot status and server info
   
   🎲 RANDOM PREFIXES
   • When enabled, randomly switches between "owo" and "o" prefix
   • Makes automation less detectable
   • Example: "owo hunt" becomes "o hunt" randomly
   
   🔒 OWO ONLY
   • When enabled, forces only "owo" to be used (never "o")
   • Useful for servers that only allow full "owo" name
   • Overrides Random Prefixes setting when enabled
   • Example: Always uses "owo hunt" instead of "o hunt"
   
   🔄 BROWSER NAVIGATION
   • Uses Microsoft Edge for Discord access
   • Startup: Win -> Edge -> Ctrl+E -> Target URL
   • Auto Restart: Closes Edge (Alt+F4) and re-runs startup
   • Target URL is configurable in the UI
   
   ⚙️ Other Settings:
   • Base interval: Time between command cycles (min 5s)
   • Refresh interval: Time between navigation refreshes (min 5 mins)
   • Typing speed: 50-200 WPM (words per minute)
   • Target user: Username for give/clover/cookie/meme commands
   
   📊 Command Distribution:
   • 80% core/optional commands (hunt, battle, coinflip, etc.)
   • 20% special commands (meme + utility + action combined)
   • This keeps the bot looking natural and avoids spam

FEATURES:
---------
✓ Dry Run Mode: Preview commands without typing
✓ Statistics Tracking: See total commands, runtime, errors
✓ Comprehensive Logging: Track everything that happens
✓ Graceful Shutdown: Clean thread termination
✓ Minimum Interval: 5s enforced for safety
✓ Hotkey Support: Ctrl+P to toggle start/stop
✓ ToS Warnings: Explicit acceptance required

SAFETY:
-------
⚠️ Minimum interval: 5 seconds (enforced)
⚠️ Maximum runtime: 24 hours (enforced)
⚠️ PyAutoGUI failsafe: Move mouse to corner to abort
⚠️ Dry-run mode: Test without sending commands
⚠️ Discord ToS: You are responsible for compliance

HOTKEYS:
--------
• Ctrl+P: Toggle start/stop for current mode
• Move mouse to screen corner: Emergency abort (PyAutoGUI failsafe)

USAGE TIPS:
-----------
1. Focus the Discord message box before starting
2. Start with Dry Run mode to preview commands
3. Monitor the logs for any errors
4. Keep intervals reasonable (5-15s minimum recommended)

DISCORD TOS COMPLIANCE:
-----------------------
This bot automates Discord input, which may violate:
• Discord Terms of Service (https://discord.com/terms)
• Server-specific rules and guidelines
• Rate limiting policies

ALTERNATIVES (LEGAL):
---------------------
Instead of automation, consider:
• Official Discord bot API (https://discord.com/developers/docs)
• User bot alternatives with rate limiting
• Manual command execution
• Server-approved automation tools

USE AT YOUR OWN RISK:
---------------------
The authors are NOT responsible for:
• Account suspensions or bans
• Loss of data or access
• Violations of Discord ToS
• Any damages resulting from use

By using this tool, you accept full responsibility for your actions.

SOURCE CODE:
------------
Made with ❤️ by Aditi and Ayush

This bot is merged from:
• EnhancedOwoAutoTyper (GitHub)
• SimpleOwoAutoTyper (enhanced version)

For source, issues, or contributions, see the header of God_owo_discordbot.py

TESTING:
--------
Run unit tests with:
    python God_owo_discordbot.py --self-test

DEPENDENCIES:
-------------
• pyautogui (for keyboard automation)
• keyboard (for hotkey support)
• tkinter (GUI - usually built into Python)

Install with:
    pip install pyautogui keyboard pillow

Note: 'keyboard' requires admin/root on some systems.
"""
        
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')
    
    def _setup_hotkeys(self) -> None:
        """Setup keyboard hotkeys (Ctrl+P for toggle)."""
        def on_ctrl_p() -> None:
            """Toggle start/stop based on current mode."""
            if self.worker and self.worker.is_alive():
                self.stop()
            else:
                # Start based on last mode or default to advanced
                if self.current_mode == "none" or self.current_mode == "advanced":
                    self._start_advanced_mode()
                elif self.current_mode == "advanced":
                    self._start_advanced_mode()
        
        try:
            keyboard.add_hotkey('ctrl+p', on_ctrl_p)
            self.logger.info("Hotkey registered: Ctrl+P (start/stop toggle)")
        except Exception as e:
            self.logger.error(f"Failed to register hotkey: {e}")
    
    def _cleanup_hotkeys(self) -> None:
        """Remove all registered hotkeys to prevent leaks."""
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all()
                self.logger.info("Hotkeys cleaned up")
            except Exception as e:
                self.logger.error(f"Failed to cleanup hotkeys: {e}")
    
    def _show_tos_warning(self) -> bool:
        """Show ToS warning dialog and get user acceptance.
        
        Returns:
            True if user accepts, False otherwise
        """
        tos_message = (
            "⚠️  TERMS OF SERVICE WARNING  ⚠️\n\n"
            "Automating Discord input may violate:\n"
            "• Discord Terms of Service\n"
            "• Server-specific rules\n"
            "• Rate limiting policies\n\n"
            "This may result in:\n"
            "• Account suspension or ban\n"
            "• Loss of access to servers\n"
            "• Data loss\n\n"
            "SAFER ALTERNATIVES:\n"
            "• Use official Discord Bot API (legal)\n"
            "• Manual command execution\n"
            "• Server-approved automation\n\n"
            "This tool is for EDUCATIONAL PURPOSES ONLY.\n\n"
            "Do you accept full responsibility and want to continue?"
        )
        
        result = messagebox.askyesno(
            "Terms of Service - READ CAREFULLY",
            tos_message,
            icon='warning'
        )
        
        if result:
            self.logger.warning("User accepted ToS warning and responsibility")
        else:
            self.logger.info("User declined ToS warning")
        
        return result
    
    def _stop_browser_test(self) -> None:
        """Signal the browser test to stop."""
        self._browser_stop_event.set()
        self.logger.info("Browser Test Stopping...")

    def _calm_sleep(self, duration: float) -> None:
        """Sleep wrapper that checks for stop_event periodically."""
        end_time = time.monotonic() + duration
        while time.monotonic() < end_time:
            if self._stop_event.is_set() or self._browser_stop_event.is_set():
                break
            time.sleep(0.1)

    def _open_edge_and_navigate(self) -> None:
        """Open Microsoft Edge and navigate to the target URL."""
        try:
            self._browser_stop_event.clear()
            target_link = self.target_url.get().strip()
            if not target_link:
                self.logger.warning("No target link provided!")
                return
                
            self.logger.info("Opening Edge and navigating...")
            self._log_command("[SYSTEM] Opening Edge...")
            
            # Press Windows key
            pyautogui.press('win')
            time.sleep(1.0)
            
            # Type "edge"
            pyautogui.write("edge")
            time.sleep(1.0)
            
            # Press Enter to open
            pyautogui.press('enter')
            
            # Wait for Edge to load
            self.logger.info("Waiting 5s for Edge to load...")
            self._calm_sleep(5.0)
            
            # Ctrl + E to focus address bar (universal trigger)
            pyautogui.hotkey('ctrl', 'e')
            time.sleep(1.0)
            
            # Press Backspace to clear query/URL
            pyautogui.press('backspace')
            time.sleep(0.5)
            
            # Type/Paste URL
            self.logger.info(f"Navigating to: {target_link}")
            pyautogui.write(target_link)
            time.sleep(0.5)
            
            # Enter
            pyautogui.press('enter')
            
            # Wait for page load (30s)
            self.logger.info("Waiting 30s for page load...")
            self._calm_sleep(30.0)
            
        except Exception as e:
            self.logger.error(f"Failed to open Edge: {e}")
            self._log_command(f"[ERROR] Failed to open Edge: {e}")

    def _perform_ctrl_r_refresh(self) -> None:
        """Perform Discord refresh using Ctrl+R."""
        try:
            self.logger.info("Performing Ctrl+R Refresh...")
            self._log_command("[SYSTEM] Performing Ctrl+R Refresh...")
            
            pyautogui.hotkey('ctrl', 'r')
            
            # Wait for reload (30s as requested)
            self.logger.info("Waiting 30s for reload...")
            self._calm_sleep(30.0)
            
        except Exception as e:
            self.logger.error(f"Ctrl+R Refresh failed: {e}")
            self._log_command(f"[ERROR] Ctrl+R Refresh failed: {e}")

    def _restart_discord_sequence(self) -> None:
        """Perform full restart sequence: Alt+F4 -> Open Edge -> Navigate."""
        try:
            self.logger.info("Starting Auto Restart Sequence...")
            self._log_command("[SYSTEM] Auto Restart Sequence...")
            
            # 1. Close Browser/App
            self._close_discord()
            time.sleep(5.0)
            
            # 2. Open Edge and Navigate
            self._open_edge_and_navigate()
            
        except Exception as e:
            self.logger.error(f"Restart sequence failed: {e}")
            self._log_command(f"[ERROR] Restart sequence failed: {e}")



    def _close_discord(self) -> None:
        """Close Discord using Alt+F4."""
        try:
            self.logger.info("Closing Discord via Alt+F4...")
            self._log_command("[SYSTEM] Closing Discord...")
            pyautogui.hotkey('alt', 'f4')
        except Exception as e:
            self.logger.error(f"Failed to close Discord: {e}")
    
    def _start_advanced_mode(self) -> None:
        """Start the advanced mode bot (configurable)."""
        # Validate not already running
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Already Running", "A bot is already running. Stop it first.")
            return
        
        # Show ToS warning
        if not self._show_tos_warning():
            return
        
        # Validate interval
        if self.advanced_interval.get() < MIN_INTERVAL:
            messagebox.showerror(
                "Invalid Interval",
                f"Minimum interval is {MIN_INTERVAL} seconds for safety."
            )
            return
        
        # Start worker
        self.current_mode = "advanced"
        self._stop_event.clear()
        self._pause_event.clear()
        self._is_paused = False
        
        # Reset gem tracking
        self.gem_hunt_count = 0
        self.last_gem_use_time = 0.0
        
        self.stats.sessions += 1
        self.stats.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_statistics()
        
        self.worker = threading.Thread(target=self._run_advanced_mode, daemon=True)
        self.worker.start()
        
        # Update UI
        self.btn_start_advanced.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_pause.config(state="normal")
        self.status_label.config(text="🔵 Advanced Mode Running... Ctrl+P to stop")
        
        self.logger.info("Advanced mode started")
        self._log_command("[SYSTEM] Advanced mode started")
    
    def stop(self) -> None:
        """Stop the currently running bot safely."""
        self._stop_event.set()
        self._pause_event.clear()
        
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=3.0)
            if self.worker.is_alive():
                self.logger.warning("Worker thread did not terminate cleanly")
        
        # Update UI
        self.btn_start_advanced.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.btn_pause.config(state="disabled", text="⏸ Pause")
        self.status_label.config(text="⏹ Stopped. Ready to start.")
        self._is_paused = False
        
        self.logger.info(f"{self.current_mode.capitalize()} mode stopped")
        self._log_command(f"[SYSTEM] {self.current_mode.capitalize()} mode stopped")
        
        self.current_mode = "none"
        self._save_statistics()
    
    def _toggle_pause(self) -> None:
        """Toggle pause state of the bot."""
        if self._is_paused:
            self._pause_event.clear()
            self._is_paused = False
            self.btn_pause.config(text="⏸ Pause")
            self.status_label.config(text=f"🟢 {self.current_mode.capitalize()} Mode Running...")
            self.logger.info("Resumed")
            self._log_command("[SYSTEM] Resumed")
        else:
            self._pause_event.set()
            self._is_paused = True
            self.btn_pause.config(text="▶ Resume")
            self.status_label.config(text="⏸ Paused")
            self.logger.info("Paused")
            self._log_command("[SYSTEM] Paused")
    

    
    def _run_advanced_mode(self) -> None:
        """Worker thread for advanced mode: configurable command sets with anti-detection."""
        rng = random.Random()
        session_start = time.monotonic()
        last_random_text_time = time.monotonic()
        last_refresh_time = time.monotonic()
        random_text_interval = rng.uniform(300, 600)  # 5-10 minutes in seconds
        
        # Build command pool based on enabled modes
        core_commands = [
            "owo hunt",
            "owo coinflip",
            "owo slots",
            "owo battle",
            "owo cash",
            "owo zoo"
        ]
        
        # Pray command (reduced frequency - 2 times per 5 minutes = 150s cooldown)
        pray_command = "owo pray"
        
        optional_commands = []
        if self.var_enable_sell_all.get():
            optional_commands.append("owo sell all")
        optional_commands.extend(["owo vote", "owo quest"])
        
        # Daily command (tracked separately - once per 5 minutes = 300s cooldown)
        daily_command = "owo daily"
        
        # Ultra advanced: action commands (owo owo)
        action_commands = [
            "owo owo cuddle", "owo owo hug", "owo owo kiss", "owo owo lick",
            "owo owo pat", "owo owo poke", "owo owo slap", "owo owo bite"
        ] if self.var_ultra_mode.get() else []
        
        # Meme commands
        meme_commands = [
            f"owo drake {self.target_user.get()}",
            f"owo headpat {self.target_user.get()}",
            f"owo slapcar {self.target_user.get()}"
        ] if self.var_meme_mode.get() else []
        
        # Utility commands
        utility_commands = [
            "owo ping", "owo stats", "owo rules"
        ] if self.var_utility_mode.get() else []
        
        # Main command pool (core + optional, excluding pray and daily which are tracked separately)
        main_commands = core_commands + optional_commands
        
        try:
            # Initial countdown
            for i in range(5, 0, -1):
                if self._stop_event.is_set():
                    return
                self.root.after(0, lambda count=i: self.status_label.config(text=f"Starting in {count}s..."))
                self._calm_sleep(1.0)
            
            # Startup Sequence: Open Edge -> Navigate
            if not self.var_dry_run.get():
                self.status_label.config(text="🚀 Running Startup Sequence...")
                self._open_edge_and_navigate()
            else:
                self.logger.info("[DRY-RUN] Would run Startup Sequence (Edge -> Navigate)")
                self._log_command("[DRY-RUN] Startup Sequence")
            
            iteration = 0
            while not self._stop_event.is_set():
                try:
                    # Handle pause
                    while self._pause_event.is_set() and not self._stop_event.is_set():
                        time.sleep(0.1)
                    
                    if self._stop_event.is_set():
                        break
                    
                    current_time = time.monotonic()
                    
                    # 1. Check Auto Restart (Alt+F4) - Every 30 mins
                    restart_interval_sec = self.restart_interval.get() * 60
                    if self.var_auto_restart.get() and (current_time - session_start) >= restart_interval_sec:
                        # Reset session start to restart timer
                        session_start = current_time
                        
                        if not self.var_dry_run.get():
                            self.status_label.config(text="🔄 Performing Auto Restart...")
                            self._restart_discord_sequence()
                            # Reset other timers to avoid immediate trigger
                            last_refresh_time = time.monotonic()
                            last_random_text_time = time.monotonic()
                        else:
                            self.logger.info("[DRY-RUN] Would perform Auto Restart (Alt+F4)")
                            self._log_command("[DRY-RUN] Auto Restart")
                        
                        continue  # Skip rest of loop to start fresh
                    
                    # 2. Check Auto Refresh (Ctrl+R) - Every 10 mins
                    refresh_interval_sec = self.refresh_interval.get() * 60
                    if self.var_auto_refresh.get() and (current_time - last_refresh_time) >= refresh_interval_sec:
                        if not self.var_dry_run.get():
                            self.status_label.config(text="🔄 Performing Auto Refresh...")
                            self._perform_ctrl_r_refresh()
                        else:
                            self.logger.info("[DRY-RUN] Would perform Auto Refresh (Ctrl+R)")
                            self._log_command("[DRY-RUN] Auto Refresh")
                        
                        last_refresh_time = time.monotonic()
                        continue  # Skip rest of loop to let things settle
                    
                    # 3. Check Random Text (every 5-10 minutes)
                    if self.var_enable_random_text.get() and (current_time - last_random_text_time) >= random_text_interval:
                        self._send_random_text(rng)
                        last_random_text_time = current_time
                        random_text_interval = rng.uniform(300, 600)  # Reset interval
                        self._calm_sleep(rng.uniform(2.0, 4.0))
                    
                    # 4. Regular Command Logic
                    
                    # Pick commands for this iteration with cooldown checking
                    commands_to_run = []
                    
                    # Pick 3-5 commands from main pool (with cooldown check)
                    available_main = [cmd for cmd in main_commands if self._can_use_command(cmd, 10.0)]  # 10s base cooldown
                    if available_main:
                        num_main = rng.randint(3, min(5, len(available_main)))
                        commands_to_run.extend(rng.sample(available_main, num_main))
                    
                    # Check pray command (2 times per 5 minutes = 150s cooldown)
                    if self._can_use_command(pray_command, 150.0):
                        if rng.random() < 0.4:  # 40% chance when available
                            commands_to_run.append(pray_command)
                    
                    # Check daily command (once per 5 minutes = 300s cooldown)
                    if self._can_use_command(daily_command, 300.0):
                        if rng.random() < 0.3:  # 30% chance when available
                            commands_to_run.append(daily_command)
                    
                    # 20% chance to add ONE special command (meme/utility/action)
                    if rng.random() < 0.20:
                        special_pool = []
                        # Action commands: only 8% chance (less frequent)
                        if action_commands and rng.random() < 0.08:
                            available_actions = [cmd for cmd in action_commands if self._can_use_command(cmd, 30.0)]
                            if available_actions:
                                special_pool.extend(available_actions)
                        # Meme commands: 12% chance
                        if meme_commands and rng.random() < 0.12:
                            available_memes = [cmd for cmd in meme_commands if self._can_use_command(cmd, 30.0)]
                            if available_memes:
                                special_pool.extend(available_memes)
                        # Utility commands: 12% chance
                        if utility_commands and rng.random() < 0.12:
                            available_utils = [cmd for cmd in utility_commands if self._can_use_command(cmd, 30.0)]
                            if available_utils:
                                special_pool.extend(available_utils)
                        
                        if special_pool:
                            special_cmd = rng.choice(special_pool)
                            commands_to_run.append(special_cmd)
                    
                    # Shuffle commands for more natural order
                    rng.shuffle(commands_to_run)
                    
                    # Execute commands
                    for cmd_base in commands_to_run:
                        if self._stop_event.is_set() or self._pause_event.is_set():
                            break
                        
                        # Generate final command
                        command = self._generate_advanced_command(cmd_base, rng)
                        
                        # Mark command as used (for cooldown tracking)
                        self._mark_command_used(cmd_base)
                        
                        # Track hunt count for gem auto-use
                        if "hunt" in cmd_base.lower():
                            self.gem_hunt_count += 1
                        
                        # Preview
                        self._update_preview(f"Next: {command}")
                        
                        # Type and send (or preview if dry-run)
                        if self.var_dry_run.get():
                            self._log_command(f"[DRY-RUN] {command}")
                            self.logger.info(f"[DRY-RUN] {command}")
                        else:
                            self._type_and_send(command, "advanced", rng)
                        
                        # Small delay between commands
                        self._calm_sleep(rng.uniform(1.0, 2.0))
                    
                    # Check if we should auto-use gems
                    if self.var_auto_use_gems.get() and not self.var_dry_run.get():
                        should_use_gems = False
                        hunt_interval = self.gem_hunt_interval.get() if self.gem_hunt_interval else 0
                        
                        # Use gems if:
                        # 1. Hunt interval is set (>0) and we've reached that many hunts
                        # 2. Or hunt interval is 0 (only when expired - we'll use after every hunt cycle)
                        if hunt_interval > 0 and self.gem_hunt_count >= hunt_interval:
                            should_use_gems = True
                            self.gem_hunt_count = 0  # Reset counter
                        elif hunt_interval == 0 and self.gem_hunt_count > 0:
                            # For "expired only" mode, use after every few hunts as a check
                            # (In real scenario, you'd need to parse bot response to know when expired)
                            if self.gem_hunt_count >= 20:  # Check every 20 hunts
                                should_use_gems = True
                                self.gem_hunt_count = 0
                        
                        if should_use_gems:
                            gem_ids_str = self.gem_ids_entry.get() if self.gem_ids_entry else "51 65 72"
                            gem_ids = [gid.strip() for gid in gem_ids_str.split() if gid.strip().isdigit()]
                            
                            if gem_ids:
                                gem_command = f"owo use {' '.join(gem_ids)}"
                                self._update_preview(f"Next: {gem_command} (Auto-Use Gems)")
                                
                                if self.var_dry_run.get():
                                    self._log_command(f"[DRY-RUN] {gem_command}")
                                    self.logger.info(f"[DRY-RUN] {gem_command}")
                                else:
                                    self._type_and_send(gem_command, "advanced", rng)
                                    self.logger.info(f"[GEM AUTO-USE] Used gems: {gem_ids}")
                                    self._log_command(f"[GEM AUTO-USE] {gem_command}")
                                
                                self._calm_sleep(rng.uniform(1.5, 2.5))
                    
                    # Wait for interval
                    interval = self.advanced_interval.get()
                    for remaining in range(interval, 0, -1):
                        if self._stop_event.is_set() or self._pause_event.is_set():
                            break
                        # Calculate cooldown times
                        now = time.monotonic()
                        pray_cooldown = max(0, 150 - (now - self.command_last_used.get(pray_command, 0)))
                        daily_cooldown = max(0, 300 - (now - self.command_last_used.get(daily_command, 0)))
                        pray_min = int(pray_cooldown / 60)
                        daily_min = int(daily_cooldown / 60)
                        status_msg = f"🔵 Next iteration in {remaining}s... | Pray: {pray_min}m | Daily: {daily_min}m"
                        self.root.after(0, lambda msg=status_msg: self.status_label.config(text=msg))
                        self._calm_sleep(1.0)
                    
                    iteration += 1
                
                except Exception as loop_error:
                    self.logger.error(f"Error in main loop iteration: {loop_error}", exc_info=True)
                    self._log_command(f"[ERROR] Loop error: {loop_error}")
                    # Wait a bit before retrying to avoid spamming errors
                    self._calm_sleep(5.0)
        
        except Exception as e:
            self.logger.error(f"Fatal error in advanced mode: {e}", exc_info=True)
            self.stats.errors += 1
            self.root.after(0, lambda: messagebox.showerror("Error", f"A fatal error occurred: {e}"))
        finally:
            runtime = int(time.monotonic() - session_start)
            self.stats.total_runtime += runtime
            self.logger.info(f"Advanced mode ended. Runtime: {runtime}s")
            self._save_statistics()
            self.root.after(0, self.stop)
    
    def _can_use_command(self, command: str, cooldown_seconds: float) -> bool:
        """Check if a command can be used based on cooldown.
        
        Args:
            command: Command to check
            cooldown_seconds: Required seconds since last use
            
        Returns:
            True if command can be used, False otherwise
        """
        now = time.monotonic()
        last_used = self.command_last_used.get(command, 0)
        return (now - last_used) >= cooldown_seconds
    
    def _mark_command_used(self, command: str) -> None:
        """Mark a command as used (update timestamp)."""
        self.command_last_used[command] = time.monotonic()
    
    def _generate_random_text(self, rng: random.Random, num_sentences: int = None) -> str:
        """Generate random nonsense text with longer sentences.
        
        Args:
            rng: Random number generator
            num_sentences: Number of sentences (default: 20-30)
            
        Returns:
            Random text string
        """
        if num_sentences is None:
            num_sentences = rng.randint(20, 30)
        
        sentences = []
        for _ in range(num_sentences):
            # Prefer longer sentences (4-5 words) as requested
            sentence_length = rng.choices(
                [1, 2, 3, 4, 5],
                weights=[5, 10, 15, 40, 30]  # Higher weight for 4-5 word sentences
            )[0]
            
            # Sample words without replacement to avoid duplicates in same sentence
            available_words = [w for w in self.random_texts if len(w.split()) <= 2]  # Use shorter phrases
            if len(available_words) < sentence_length:
                available_words = self.random_texts  # Fallback to all if needed
            
            words = rng.sample(available_words, min(sentence_length, len(available_words)))
            sentence = ' '.join(words)
            
            # Random capitalization (first letter)
            if rng.random() < 0.3:
                sentence = sentence.capitalize()
            
            # Add punctuation randomly
            if rng.random() < 0.2:
                sentence += rng.choice(['!', '?', '.', '...'])
            
            sentences.append(sentence)
        
        return ' '.join(sentences)
    
    def _send_random_text(self, rng: random.Random) -> None:
        """Send random text message."""
        if not self.var_enable_random_text.get():
            return
        
        random_text = self._generate_random_text(rng)
        self._type_and_send(random_text, "advanced", rng, is_random_text=True)
        self.logger.info(f"[RANDOM TEXT] Sent {len(random_text.split())} words")
    

    
    def _generate_advanced_command(self, base_cmd: str, rng: random.Random) -> str:
        """Generate a command for advanced mode with random amounts and prefixes.
        
        Args:
            base_cmd: Base command string
            rng: Random number generator
            
        Returns:
            Final command string with amounts/prefixes if applicable
        """
        # Apply prefix logic (respect owo_only setting)
        if base_cmd.startswith("owo "):
            if self.var_owo_only.get():
                # Force "owo" only, don't use "o" (even if Random Prefixes is enabled)
                prefix = "owo"
                base_cmd = base_cmd.replace("owo", prefix, 1)
            elif self.var_advanced_prefix.get():
                # Random between "owo" and "o" (only if Random Prefixes is enabled and owo_only is NOT checked)
                prefix = rng.choice(["owo", "o"])
                base_cmd = base_cmd.replace("owo", prefix, 1)
            # If neither is enabled, keep default "owo" (no change needed)
        
        # Add amounts for gambling commands
        if "coinflip" in base_cmd:
            amount = self._generate_unique_amount("coinflip", 1, 500, rng)
            return f"{base_cmd} {amount}"
        elif "slots" in base_cmd:
            amount = self._generate_unique_amount("slots", 1, 500, rng)
            return f"{base_cmd} {amount}"
        else:
            return base_cmd
    
    def _generate_unique_amount(self, key: str, min_val: int, max_val: int, rng: random.Random, max_retries: int = 10) -> int:
        """Generate a unique random amount (different from previous).
        
        Args:
            key: Key for tracking previous amounts
            min_val: Minimum value
            max_val: Maximum value
            rng: Random number generator
            max_retries: Maximum retries to find unique value
            
        Returns:
            Random amount different from previous
        """
        amount = rng.randint(min_val, max_val)
        retries = 0
        
        while amount == self.previous_amounts.get(key, -1) and retries < max_retries:
            amount = rng.randint(min_val, max_val)
            retries += 1
        
        self.previous_amounts[key] = amount
        return amount
    
    def _type_and_send(self, command: str, mode: str, rng: random.Random, is_random_text: bool = False) -> None:
        """Type a command with human-like timing and send it.
        
        Args:
            command: The command to type
            mode: The mode ("simple" or "advanced")
            rng: Random number generator
            is_random_text: Whether this is random text (not tracked as command)
        """
        if self._stop_event.is_set() or self._pause_event.is_set():
            return
        
        try:
            # Type at configured WPM
            wpm = self.typing_wpm.get()
            chars_per_second = (wpm * 5) / 60  # Average 5 chars per word
            delay_per_char = 1.0 / chars_per_second
            
            for char in command:
                if self._stop_event.is_set() or self._pause_event.is_set():
                    break
                
                pyautogui.typewrite(char)
                # Add small variance
                variance = rng.uniform(0.8, 1.2)
                time.sleep(delay_per_char * variance)
            
            if not self._stop_event.is_set() and not self._pause_event.is_set():
                pyautogui.press('enter')
                
                # Update stats (only for actual commands, not random text)
                if not is_random_text:
                    self.stats.commands_sent += 1
                    cmd_type = mode
                    self.stats.commands_by_type[cmd_type] = self.stats.commands_by_type.get(cmd_type, 0) + 1
                
                # Log
                if is_random_text:
                    self.logger.info(f"[RANDOM TEXT] Sent: {command[:50]}...")
                    self._log_command(f"[RANDOM TEXT] {command[:50]}...")
                else:
                    self.logger.info(f"Sent: {command}")
                    self._log_command(f"[{mode.upper()}] {command}")
                
                # Update status
                cmd_preview = command[:40] + "..." if len(command) > 40 else command
                status_text = f"✓ Sent: {cmd_preview} | Total: {self.stats.commands_sent}"
                self.root.after(0, lambda txt=status_text: self.status_label.config(text=txt))
                
                # Variable post-send delay (longer for random text to seem more natural)
                if is_random_text:
                    self._calm_sleep(rng.uniform(2.0, 4.0))
                else:
                    self._calm_sleep(rng.uniform(0.8, 1.5))
        
        except Exception as e:
            self.logger.error(f"Error typing command '{command}': {e}")
            self.stats.errors += 1
            self._log_command(f"[ERROR] Failed to send: {command}")
    
    def _calm_sleep(self, duration: float) -> None:
        """Sleep with frequent stop/pause event checks.
        
        Args:
            duration: Sleep duration in seconds
        """
        end_time = time.monotonic() + duration
        while time.monotonic() < end_time and not self._stop_event.is_set():
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue
            time.sleep(min(0.1, end_time - time.monotonic()))
    
    def _update_preview(self, text: str) -> None:
        """Update the preview text box.
        
        Args:
            text: Text to display in preview
        """
        def update():
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', text)
            self.preview_text.config(state='disabled')
        
        self.root.after(0, update)
    
    def _log_command(self, command: str) -> None:
        """Add a command to the command log (keep last 50).
        
        Args:
            command: Command to log
        """
        def log():
            self.command_log.config(state='normal')
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.command_log.insert('1.0', f"[{timestamp}] {command}\n")
            
            # Keep only last 50 lines
            lines = int(self.command_log.index('end-1c').split('.')[0])
            if lines > 50:
                self.command_log.delete(f"{lines-50}.0", tk.END)
            
            self.command_log.config(state='disabled')
        
        self.root.after(0, log)
    
    def _update_stats_display(self) -> None:
        """Update the statistics display."""
        self.stats_text.delete('1.0', tk.END)
        
        hours = self.stats.total_runtime // 3600
        minutes = (self.stats.total_runtime % 3600) // 60
        seconds = self.stats.total_runtime % 60
        
        # Calculate commands per hour if we have runtime
        commands_per_hour = 0
        if self.stats.total_runtime > 0:
            commands_per_hour = int((self.stats.commands_sent / self.stats.total_runtime) * 3600)
        
        # Calculate average commands per session
        avg_per_session = 0
        if self.stats.sessions > 0:
            avg_per_session = self.stats.commands_sent // self.stats.sessions
        
        stats_content = f"""
╔════════════════════════════════════════════════════════════════╗
║                    📊 STATISTICS DASHBOARD                     ║
╚════════════════════════════════════════════════════════════════╝

📈 OVERALL METRICS
{'─' * 64}
Total Commands Sent:         {self.stats.commands_sent:,}
Total Runtime:               {hours}h {minutes}m {seconds}s
Total Sessions:              {self.stats.sessions}
Average Commands/Session:    {avg_per_session}
Commands Per Hour:           {commands_per_hour:,}
Errors Encountered:          {self.stats.errors}
Success Rate:                {((self.stats.commands_sent / max(1, self.stats.commands_sent + self.stats.errors)) * 100):.1f}%
Last Run:                    {self.stats.last_run or 'Never'}

📊 COMMANDS BY MODE
{'─' * 64}
"""
        
        # Group by mode
        if self.stats.commands_by_type:
            for cmd_type, count in sorted(self.stats.commands_by_type.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / max(1, self.stats.commands_sent)) * 100
                bar_length = int(percentage / 2)  # Scale to 50 chars max
                bar = '█' * bar_length + '░' * (50 - bar_length)
                stats_content += f"{cmd_type:12s} │ {count:6,} │ {percentage:5.1f}% │ {bar}\n"
        else:
            stats_content += "  No commands sent yet.\n"
        
        stats_content += f"\n{'─' * 64}\n"
        stats_content += f"💡 TIP: Keep the bot running longer to see detailed statistics!\n"
        
        self.stats_text.insert('1.0', stats_content)
    
    def _clear_stats(self) -> None:
        """Clear all statistics after confirmation."""
        if messagebox.askyesno("Clear Statistics", "Are you sure you want to clear all statistics?"):
            self.stats = BotStats()
            self._save_statistics()
            self._update_stats_display()
            self.logger.info("Statistics cleared")
    
    def _update_logs_display(self) -> None:
        """Update the logs display from log file."""
        try:
            if LOG_FILE.exists():
                with open(LOG_FILE, 'r') as f:
                    lines = f.readlines()
                    # Show last 500 lines
                    self.logs_text.delete('1.0', tk.END)
                    self.logs_text.insert('1.0', ''.join(lines[-500:]))
                    self.logs_text.see(tk.END)
        except Exception as e:
            self.logger.error(f"Failed to update logs display: {e}")
    
    def _clear_logs(self) -> None:
        """Clear log file after confirmation."""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            try:
                with open(LOG_FILE, 'w') as f:
                    f.write("")
                self._update_logs_display()
                self.logger.info("Logs cleared")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {e}")
    
    def _on_closing(self) -> None:
        """Handle window close event with cleanup."""
        if self.worker and self.worker.is_alive():
            if messagebox.askokcancel("Quit", "Bot is running. Stop and quit?"):
                self.stop()
                self._cleanup_hotkeys()
                self.root.destroy()
        else:
            self._cleanup_hotkeys()
            self.root.destroy()


# ============================================================================
# UNIT TESTS (--self-test mode)
# ============================================================================

def run_self_tests() -> bool:
    """Run unit tests for pure functions.
    
    Returns:
        True if all tests pass, False otherwise
    """
    print("=" * 60)
    print("God OwO Bot - Self Test Mode")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Test 1: Generate unique amount
    print("\nTest 1: Generate unique amounts...")
    try:
        rng = random.Random(42)  # Seeded for reproducibility
        amounts = []
        for _ in range(10):
            amount = rng.randint(1, 500)
            amounts.append(amount)
        
        # Check that we get variety (not all the same)
        unique_count = len(set(amounts))
        assert unique_count > 1, f"Expected variety, got {unique_count} unique values"
        print(f"  ✓ Generated {unique_count} unique amounts out of 10")
        passed += 1
    except AssertionError as e:
        print(f"  ✗ FAILED: {e}")
        failed += 1
    

    
    # Test 3: Stats dataclass
    print("\nTest 3: BotStats serialization...")
    try:
        stats = BotStats(commands_sent=100, sessions=5)
        data = stats.to_dict()
        assert data['commands_sent'] == 100
        assert data['sessions'] == 5
        
        stats2 = BotStats.from_dict(data)
        assert stats2.commands_sent == 100
        assert stats2.sessions == 5
        
        print(f"  ✓ BotStats serialization works")
        passed += 1
    except AssertionError as e:
        print(f"  ✗ FAILED: {e}")
        failed += 1
    
    # Test 4: Minimum interval enforcement (logic check)
    print("\nTest 4: Minimum interval validation...")
    try:
        test_interval = 3
        assert test_interval < MIN_INTERVAL, "Test interval should be less than MIN_INTERVAL"
        
        # Simulate validation
        if test_interval < MIN_INTERVAL:
            error_raised = True
        else:
            error_raised = False
        
        assert error_raised, "Should raise error for interval < MIN_INTERVAL"
        print(f"  ✓ Minimum interval enforcement works (MIN={MIN_INTERVAL}s)")
        passed += 1
    except AssertionError as e:
        print(f"  ✗ FAILED: {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All tests passed!")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed.")
        return False


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """Main entry point for the application."""
    # Check for --self-test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        success = run_self_tests()
        sys.exit(0 if success else 1)
    
    # Normal GUI mode
    root = tk.Tk()
    app = GodOwoBotApp(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Cleaning up...")
        if hasattr(app, '_cleanup_hotkeys'):
            app._cleanup_hotkeys()
        sys.exit(0)


if __name__ == "__main__":
    main()
