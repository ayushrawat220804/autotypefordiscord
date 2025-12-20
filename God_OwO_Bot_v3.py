#!/usr/bin/env python3
"""
God OwO Discord Bot v3 - Enhanced Auto Typer
=============================================

Features:
- Pause/Resume with 5-second countdown before resuming
- Hardcoded @owo target
- 3 custom command input fields with placeholders
- Updated default settings (all modes ON, sell all OFF)
- Fixed gem usage threshold at 30+ hunts

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
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json

# Optional imports with graceful fallback
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.01
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


# Constants
MIN_INTERVAL = 5
MAX_RUNTIME_HOURS = 24
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
        return cls(**data)


class GodOwoBotV3:
    """Main application class for God OwO Discord Bot v3."""
    
    # Hardcoded target user
    TARGET_USER = "@owo"
    
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("✨ God OwO Discord Bot v3 ✨ - Made with ❤️ by Aditi and Ayush")
        
        # Maximize window on startup
        try:
            self.root.state('zoomed')
        except:
            try:
                self.root.attributes('-zoomed', True)
            except:
                self.root.geometry("1200x900")
        
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
        self._resume_countdown_active = False
        self.worker: Optional[threading.Thread] = None
        self.current_mode: str = "none"
        self._browser_stop_event = threading.Event()
        
        # Statistics
        self.stats = BotStats()
        self._load_statistics()
        
        # UI Variables - Advanced Mode with UPDATED DEFAULTS
        self.advanced_interval = tk.IntVar(value=10)
        self.refresh_interval = tk.IntVar(value=10)
        self.restart_interval = tk.IntVar(value=30)
        self.var_auto_refresh = tk.BooleanVar(value=True)
        self.var_auto_restart = tk.BooleanVar(value=True)
        self.var_dry_run = tk.BooleanVar(value=False)
        self.target_url = tk.StringVar(value="https://discord.com/channels/1432319524606054422/1434581841037492377")
        
        # UPDATED DEFAULTS - All modes ON except sell all
        self.var_ultra_mode = tk.BooleanVar(value=True)       # TICKED
        self.var_meme_mode = tk.BooleanVar(value=True)        # TICKED
        self.var_utility_mode = tk.BooleanVar(value=True)     # TICKED
        self.var_advanced_prefix = tk.BooleanVar(value=True)  # TICKED (Random owo/o)
        self.var_owo_only = tk.BooleanVar(value=False)
        self.var_enable_sell_all = tk.BooleanVar(value=False) # UNTICKED
        self.var_enable_random_text = tk.BooleanVar(value=True)  # TICKED
        self.typing_wpm = tk.IntVar(value=120)
        
        # Command tracking
        self.previous_amounts: Dict[str, int] = {}
        self.command_last_used: Dict[str, float] = {}
        
        # Gem usage tracking - UPDATED DEFAULT
        self.var_auto_use_gems = tk.BooleanVar(value=False)  # UNTICKED
        self.gem_hunt_count = 0
        self.gems_to_use = []
        self.last_gem_use_time = 0.0
        self.gem_ids_var = tk.StringVar(value="51 65 72")
        self.gem_hunt_interval = tk.IntVar(value=0)
        self.gem_use_threshold = tk.IntVar(value=30)  # At least 30 hunts
        
        # Custom command inputs
        self.custom_cmd_1 = tk.StringVar(value="")
        self.custom_cmd_2 = tk.StringVar(value="")
        self.custom_cmd_3 = tk.StringVar(value="")
        
        # === NEW SAFETY FEATURES ===
        # Anti-Detection Delays
        self.var_anti_detection = tk.BooleanVar(value=True)  # ON by default
        self.delay_min = tk.DoubleVar(value=1.5)  # Minimum delay between commands
        self.delay_max = tk.DoubleVar(value=4.0)  # Maximum delay between commands
        
        # Activity Randomizer (simulate AFK/typing patterns)
        self.var_activity_randomizer = tk.BooleanVar(value=True)  # ON by default
        self.afk_chance = tk.IntVar(value=10)  # % chance to go AFK briefly
        self.afk_duration_min = tk.IntVar(value=5)  # Min AFK seconds
        self.afk_duration_max = tk.IntVar(value=30)  # Max AFK seconds
        
        # Max Runtime Limit
        self.var_max_runtime = tk.BooleanVar(value=True)  # ON by default
        self.max_runtime_hours = tk.DoubleVar(value=4.0)  # Auto-stop after X hours
        
        # Random text sentences pool
        self.random_texts = [
            "lol", "haha", "nice", "cool", "yeah", "ok", "sure", "maybe", "idk", "lmao",
            "xd", "wtf", "bruh", "fr", "ngl", "tbh", "same", "mood", "facts", "true",
            "yep", "nope", "nah", "okay", "lol i", "kux bi hora h",
            "that's funny", "makes sense", "got it", "sounds good", "fair enough",
            "nice one", "good stuff", "no way", "for real", "wait what",
            "lol i don't know", "xd that's so funny", "wtf is going on",
            "bruh that's crazy", "fr that makes sense", "ngl that's pretty cool",
            "tbh i think so", "same here bro", "mood right now",
        ]
        
        # Build UI
        self._build_ui()
        
        # Setup hotkeys
        if KEYBOARD_AVAILABLE:
            self._setup_hotkeys()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.logger.info("God OwO Bot v3 initialized successfully")
    
    def _setup_logging(self) -> None:
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
        self.logger.info("God OwO Discord Bot v3 - Session Started")
    
    def _check_dependencies(self) -> bool:
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
                f"pip install {' '.join(missing)}"
            )
            messagebox.showerror("Missing Dependencies", msg)
            self.root.quit()
            return False
        return True
    
    def _load_statistics(self) -> None:
        try:
            if STATS_FILE.exists():
                with open(STATS_FILE, 'r') as f:
                    data = json.load(f)
                    self.stats = BotStats.from_dict(data)
        except Exception as e:
            self.logger.error(f"Failed to load statistics: {e}")
    
    def _save_statistics(self) -> None:
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save statistics: {e}")
    
    def _build_ui(self) -> None:
        """Build the main user interface."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text='🎮 Main Controls')
        self._build_main_tab(main_tab)
        
        stats_tab = ttk.Frame(notebook)
        notebook.add(stats_tab, text='📊 Statistics')
        self._build_stats_tab(stats_tab)
        
        logs_tab = ttk.Frame(notebook)
        notebook.add(logs_tab, text='📝 Logs')
        self._build_logs_tab(logs_tab)
        
        commands_tab = ttk.Frame(notebook)
        notebook.add(commands_tab, text='📋 Commands')
        self._build_commands_tab(commands_tab)
        
        help_tab = ttk.Frame(notebook)
        notebook.add(help_tab, text='❓ Help')
        self._build_help_tab(help_tab)
    
    def _build_main_tab(self, parent: ttk.Frame) -> None:
        """Build main controls tab."""
        main = ttk.Frame(parent, padding="10")
        main.pack(fill='both', expand=True)
        
        # Title
        title = ttk.Label(main, text="✨ God OwO Discord Bot v3 ✨", font=("Arial", 18, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=(0, 0))
        
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
        
        # LEFT COLUMN: Advanced Mode
        left_wrapper = ttk.LabelFrame(main, text="🔵 Advanced Mode (Configurable)", padding="5")
        left_wrapper.grid(row=3, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(0, 5))
        
        adv_col1 = ttk.Frame(left_wrapper)
        adv_col1.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 5))
        
        ttk.Separator(left_wrapper, orient='vertical').pack(side=tk.LEFT, fill='y', padx=5)
        
        adv_col2 = ttk.Frame(left_wrapper)
        adv_col2.pack(side=tk.LEFT, fill='both', expand=True, padx=(5, 0))

        # === ADV_COL1 Content ===
        ttk.Label(adv_col1, text="Base Interval (seconds):").pack(anchor=tk.W)
        ttk.Spinbox(adv_col1, from_=MIN_INTERVAL, to=120, textvariable=self.advanced_interval, width=10).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(adv_col1, text="Refresh Interval (min):").pack(anchor=tk.W)
        ttk.Spinbox(adv_col1, from_=5, to=120, textvariable=self.refresh_interval, width=10).pack(anchor=tk.W, pady=(0, 2))
        ttk.Checkbutton(adv_col1, text="Auto Refresh (Ctrl+R)", variable=self.var_auto_refresh).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(adv_col1, text="Restart Interval (min):").pack(anchor=tk.W)
        ttk.Spinbox(adv_col1, from_=10, to=240, textvariable=self.restart_interval, width=10).pack(anchor=tk.W, pady=(0, 2))
        ttk.Checkbutton(adv_col1, text="Auto Restart (Alt+F4)", variable=self.var_auto_restart).pack(anchor=tk.W, pady=(0, 10))

        ttk.Label(adv_col1, text="Target Link (Browser):").pack(anchor=tk.W)
        ttk.Entry(adv_col1, textvariable=self.target_url, width=25).pack(anchor=tk.W, pady=(0, 10))

        browser_btn_frame = ttk.Frame(adv_col1)
        browser_btn_frame.pack(anchor=tk.W, pady=(5, 5))
        
        ttk.Button(browser_btn_frame, text="Test Browser Nav", 
                   command=lambda: threading.Thread(target=self._open_edge_and_navigate, daemon=True).start()
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(browser_btn_frame, text="Stop Test", command=self._stop_browser_test).pack(side=tk.LEFT)

        # Modes - All TICKED by default
        ttk.Separator(adv_col1, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Checkbutton(adv_col1, text="Ultra Advanced Mode", variable=self.var_ultra_mode).pack(anchor=tk.W, pady=(5, 2))
        ttk.Checkbutton(adv_col1, text="Meme Mode", variable=self.var_meme_mode).pack(anchor=tk.W, pady=(0, 2))
        ttk.Checkbutton(adv_col1, text="Utility Mode", variable=self.var_utility_mode).pack(anchor=tk.W, pady=(0, 10))

        # === ADV_COL2 Content ===
        ttk.Checkbutton(adv_col2, text="Random Prefixes (owo/O)", variable=self.var_advanced_prefix).pack(anchor=tk.W)
        ttk.Checkbutton(adv_col2, text="OwO Only (Force full)", variable=self.var_owo_only).pack(anchor=tk.W)
        ttk.Checkbutton(adv_col2, text="Enable Random Text", variable=self.var_enable_random_text).pack(anchor=tk.W, pady=(5, 0))
        ttk.Checkbutton(adv_col2, text="Enable 'owo sell all'", variable=self.var_enable_sell_all).pack(anchor=tk.W)
        ttk.Checkbutton(adv_col2, text="Use Gem ID", variable=self.var_auto_use_gems).pack(anchor=tk.W, pady=(5, 0))
        
        ttk.Separator(adv_col2, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Gems - UPDATED threshold default to 30
        ttk.Label(adv_col2, text="Gem IDs (space-sep):").pack(anchor=tk.W)
        ttk.Entry(adv_col2, textvariable=self.gem_ids_var, width=20).pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(adv_col2, text="Use after hunts (0=expired):").pack(anchor=tk.W)
        ttk.Spinbox(adv_col2, from_=0, to=100, textvariable=self.gem_use_threshold, width=5).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Separator(adv_col2, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Typing Speed
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
        
        # Target User - HARDCODED, shown as label
        ttk.Label(adv_col2, text="Target User:").pack(anchor=tk.W, pady=(5, 0))
        ttk.Label(adv_col2, text=self.TARGET_USER, font=("Arial", 10, "bold"), foreground="blue").pack(anchor=tk.W)
        
        ttk.Separator(adv_col2, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # CUSTOM COMMAND INPUTS with placeholders
        ttk.Label(adv_col2, text="Custom Commands:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.custom_entry_1 = ttk.Entry(adv_col2, textvariable=self.custom_cmd_1, width=20)
        self.custom_entry_1.pack(anchor=tk.W, pady=(5, 2))
        self.custom_entry_1.insert(0, "e.g. owo daily")
        self.custom_entry_1.bind("<FocusIn>", lambda e: self._clear_placeholder(self.custom_entry_1, "e.g. owo daily"))
        self.custom_entry_1.bind("<FocusOut>", lambda e: self._restore_placeholder(self.custom_entry_1, "e.g. owo daily"))
        
        self.custom_entry_2 = ttk.Entry(adv_col2, textvariable=self.custom_cmd_2, width=20)
        self.custom_entry_2.pack(anchor=tk.W, pady=(0, 2))
        self.custom_entry_2.insert(0, "e.g. owo quest")
        self.custom_entry_2.bind("<FocusIn>", lambda e: self._clear_placeholder(self.custom_entry_2, "e.g. owo quest"))
        self.custom_entry_2.bind("<FocusOut>", lambda e: self._restore_placeholder(self.custom_entry_2, "e.g. owo quest"))
        
        self.custom_entry_3 = ttk.Entry(adv_col2, textvariable=self.custom_cmd_3, width=20)
        self.custom_entry_3.pack(anchor=tk.W, pady=(0, 5))
        self.custom_entry_3.insert(0, "e.g. owo vote")
        self.custom_entry_3.bind("<FocusIn>", lambda e: self._clear_placeholder(self.custom_entry_3, "e.g. owo vote"))
        self.custom_entry_3.bind("<FocusOut>", lambda e: self._restore_placeholder(self.custom_entry_3, "e.g. owo vote"))

        # === SAFETY FEATURES SECTION ===
        safety_frame = ttk.LabelFrame(main, text="🛡️ Safety Features", padding="5")
        safety_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=(10, 0))
        
        safety_col1 = ttk.Frame(safety_frame)
        safety_col1.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 10))
        
        safety_col2 = ttk.Frame(safety_frame)
        safety_col2.pack(side=tk.LEFT, fill='both', expand=True)
        
        # Anti-Detection Delays
        ttk.Checkbutton(safety_col1, text="🕵️ Anti-Detection Delays", variable=self.var_anti_detection).pack(anchor=tk.W)
        delay_frame = ttk.Frame(safety_col1)
        delay_frame.pack(anchor=tk.W, pady=(2, 5))
        ttk.Label(delay_frame, text="Delay:", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(delay_frame, from_=0.5, to=10, textvariable=self.delay_min, width=4, increment=0.5).pack(side=tk.LEFT, padx=2)
        ttk.Label(delay_frame, text="-", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(delay_frame, from_=1, to=20, textvariable=self.delay_max, width=4, increment=0.5).pack(side=tk.LEFT, padx=2)
        ttk.Label(delay_frame, text="sec", font=("Arial", 8)).pack(side=tk.LEFT)
        
        # Activity Randomizer
        ttk.Checkbutton(safety_col1, text="💤 Activity Randomizer (AFK)", variable=self.var_activity_randomizer).pack(anchor=tk.W, pady=(5, 0))
        afk_frame = ttk.Frame(safety_col1)
        afk_frame.pack(anchor=tk.W, pady=(2, 5))
        ttk.Label(afk_frame, text="AFK:", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(afk_frame, from_=1, to=50, textvariable=self.afk_chance, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Label(afk_frame, text="% for", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(afk_frame, from_=5, to=60, textvariable=self.afk_duration_min, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Label(afk_frame, text="-", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(afk_frame, from_=10, to=120, textvariable=self.afk_duration_max, width=3).pack(side=tk.LEFT, padx=2)
        ttk.Label(afk_frame, text="sec", font=("Arial", 8)).pack(side=tk.LEFT)
        
        # Max Runtime Limit
        ttk.Checkbutton(safety_col2, text="⏰ Max Runtime Limit", variable=self.var_max_runtime).pack(anchor=tk.W)
        runtime_frame = ttk.Frame(safety_col2)
        runtime_frame.pack(anchor=tk.W, pady=(2, 5))
        ttk.Label(runtime_frame, text="Stop after:", font=("Arial", 8)).pack(side=tk.LEFT)
        ttk.Spinbox(runtime_frame, from_=0.5, to=24, textvariable=self.max_runtime_hours, width=4, increment=0.5).pack(side=tk.LEFT, padx=2)
        ttk.Label(runtime_frame, text="hours", font=("Arial", 8)).pack(side=tk.LEFT)
        
        # Emergency Stop Info
        emergency_frame = ttk.Frame(safety_col2)
        emergency_frame.pack(anchor=tk.W, pady=(10, 0))
        ttk.Label(emergency_frame, text="🚨 Emergency Stop:", font=("Arial", 9, "bold"), foreground="red").pack(anchor=tk.W)
        ttk.Label(emergency_frame, text="Ctrl+Shift+Q", font=("Arial", 10, "bold"), foreground="darkred").pack(anchor=tk.W)

        # RIGHT COLUMN: Controls & Logs
        right_panel = ttk.Frame(main)
        right_panel.grid(row=3, column=1, rowspan=2, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(5, 0))

        control_frame = ttk.LabelFrame(right_panel, text="🎛️ Controls & Preview", padding="10")
        control_frame.pack(fill='x', pady=(0, 10))
        
        btn_container = ttk.Frame(control_frame)
        btn_container.pack(fill='x', pady=(0, 10))
        
        self.btn_start = ttk.Button(btn_container, text="▶ Start Bot", command=self._start_advanced_mode, width=12)
        self.btn_start.pack(side=tk.LEFT, padx=(0, 2))

        self.btn_stop = ttk.Button(btn_container, text="⏹ Stop", command=self.stop, state="disabled", width=12)
        self.btn_stop.pack(side=tk.LEFT, padx=(0, 2))
        
        self.btn_pause = ttk.Button(btn_container, text="⏸ Pause", command=self._toggle_pause, state="disabled", width=10)
        self.btn_pause.pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Checkbutton(control_frame, text="🔍 Dry Run", variable=self.var_dry_run).pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(control_frame, text="Status:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.status_label = ttk.Label(control_frame, text="Ready.", font=("Arial", 9), wraplength=200, justify=tk.LEFT)
        self.status_label.pack(anchor=tk.W, fill='x', pady=(0, 5))
        
        # Runtime display
        ttk.Label(control_frame, text="Runtime:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.runtime_label = ttk.Label(control_frame, text="0h 0m 0s", font=("Arial", 9))
        self.runtime_label.pack(anchor=tk.W, fill='x', pady=(0, 5))
        
        ttk.Label(control_frame, text="Next Command:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        self.preview_text = tk.Text(control_frame, height=3, width=30, wrap=tk.WORD, font=("Courier", 8))
        self.preview_text.pack(fill='x', expand=False)
        self.preview_text.config(state='disabled')

        log_frame = ttk.LabelFrame(right_panel, text="📜 Recent Commands", padding="5")
        log_frame.pack(fill='both', expand=True)
        
        self.command_log = scrolledtext.ScrolledText(log_frame, height=10, width=40, wrap=tk.WORD, font=("Courier", 8))
        self.command_log.pack(fill='both', expand=True)
        self.command_log.config(state='disabled')
        
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(3, weight=1)
        
        if KEYBOARD_AVAILABLE:
            hotkey_info = ttk.Label(main, text="⌨️ Hotkeys: Ctrl+P (toggle) | Ctrl+Shift+Q (emergency stop)", font=("Arial", 9), foreground="blue")
            hotkey_info.grid(row=5, column=0, columnspan=2, pady=(5, 0))
    
    def _clear_placeholder(self, entry: ttk.Entry, placeholder: str) -> None:
        """Clear placeholder text on focus."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
    
    def _restore_placeholder(self, entry: ttk.Entry, placeholder: str) -> None:
        """Restore placeholder text if empty."""
        if entry.get() == "":
            entry.insert(0, placeholder)
    
    def _build_stats_tab(self, parent: ttk.Frame) -> None:
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
        commands_frame = ttk.Frame(parent, padding="10")
        commands_frame.pack(fill='both', expand=True)
        
        title = ttk.Label(commands_frame, text="📋 Complete OwO Bot Commands Reference", font=("Arial", 16, "bold"))
        title.pack(pady=(0, 10))
        
        commands_text = scrolledtext.ScrolledText(commands_frame, width=90, height=35, wrap=tk.WORD, font=("Courier", 9))
        commands_text.pack(fill='both', expand=True)
        
        commands_content = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    COMPLETE OWO BOT COMMANDS REFERENCE                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎖 RANKINGS: top, my
💰 ECONOMY: cowoncy, give, daily, vote, quest, checklist, shop, buy
🌱 ANIMALS: zoo, hunt, sell, sacrifice, battle, inv, equip, autohunt, lootbox, crate, team
🎲 GAMBLING: slots, coinflip, lottery, blackjack
🎱 FUN: 8b, define, gif, pic, translate, roll, choose, bell
🎭 SOCIAL: cookie, ship, pray, curse, marry, emoji, profile, level
😂 MEME GENERATION: spongebobchicken, slapcar, isthisa, drake, distractedbf, communismcat, 
   eject, emergencymeeting, headpat, tradeoffer, waddle
🤗 ACTIONS: cuddle, hug, kiss, lick, nom, pat, poke, slap, stare, highfive, bite, greet,
   punch, handholding, tickle, kill, hold, pats, wave, boop, snuggle, bully
🔧 UTILITY: ping, stats, link, guildlink, disable, censor, rules, shards, math, color, prefix

NOTE: Action commands use format "owo owo [action] @user"
      Target user is hardcoded to @owo in this version
"""
        
        commands_text.insert('1.0', commands_content)
        commands_text.config(state='disabled')
    
    def _build_help_tab(self, parent: ttk.Frame) -> None:
        help_frame = ttk.Frame(parent, padding="10")
        help_frame.pack(fill='both', expand=True)
        
        help_text = scrolledtext.ScrolledText(help_frame, width=80, height=30, wrap=tk.WORD, font=("Arial", 10))
        help_text.pack(fill='both', expand=True)
        
        help_content = """
God OwO Discord Bot v3 - Help & Information
============================================

v3 NEW FEATURES:
----------------
✓ Pause/Resume with 5-second countdown before resuming
✓ Hardcoded @owo target (more consistent)
✓ 3 custom command input fields with placeholders
✓ Updated defaults: All modes ON, sell all OFF
✓ Gem usage after 30+ hunts by default

DEFAULT SETTINGS (v3):
----------------------
✓ Ultra Advanced Mode: ON
✓ Meme Mode: ON
✓ Utility Mode: ON
✓ Random Prefixes: ON
✓ Random Text: ON
✓ Anti-Detection Delays: ON (1.5-4s)
✓ Activity Randomizer: ON (10% AFK)
✓ Max Runtime Limit: ON (4 hours)
✗ Enable 'owo sell all': OFF
✗ Use Gem ID: OFF
• Use after hunts: 30

SAFETY FEATURES:
----------------
🕵️ Anti-Detection Delays: Random delays between commands
💤 Activity Randomizer: Simulates AFK/idle behavior
⏰ Max Runtime Limit: Auto-stops after configurable hours
🚨 Emergency Stop: Ctrl+Shift+Q to instantly stop

PAUSE/RESUME:
-------------
When you pause and resume, the bot will show a 5-second countdown before
continuing from where it left off. This gives you time to focus Discord.

CUSTOM COMMANDS:
----------------
Enter up to 3 custom commands that will be run alongside the built-in commands.
Clear the placeholder text and enter your command (e.g., "owo daily").

SAFETY:
-------
⚠️ Minimum interval: 5 seconds (enforced)
⚠️ Maximum runtime: 24 hours (configurable)
⚠️ PyAutoGUI failsafe: Move mouse to corner to abort
⚠️ Discord ToS: You are responsible for compliance

HOTKEYS:
--------
• Ctrl+P: Toggle start/stop
• Ctrl+Shift+Q: Emergency stop (instant)

Made with ❤️ by Aditi and Ayush
"""
        
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')
    
    def _setup_hotkeys(self) -> None:
        def on_ctrl_p() -> None:
            if self.worker and self.worker.is_alive():
                self.stop()
            else:
                self._start_advanced_mode()
        
        def on_emergency_stop() -> None:
            """Emergency stop - Ctrl+Shift+Q - instantly stops everything."""
            self.logger.warning("EMERGENCY STOP triggered via Ctrl+Shift+Q!")
            self._log_command("[EMERGENCY] Bot stopped via Ctrl+Shift+Q!")
            self.stop()
        
        try:
            keyboard.add_hotkey('ctrl+p', on_ctrl_p)
            keyboard.add_hotkey('ctrl+shift+q', on_emergency_stop)
            self.logger.info("Hotkeys registered: Ctrl+P (toggle), Ctrl+Shift+Q (emergency stop)")
        except Exception as e:
            self.logger.error(f"Failed to register hotkeys: {e}")
    
    def _cleanup_hotkeys(self) -> None:
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all()
            except Exception as e:
                self.logger.error(f"Failed to cleanup hotkeys: {e}")
    
    def _show_tos_warning(self) -> bool:
        result = messagebox.askyesno(
            "Terms of Service - READ CAREFULLY",
            "⚠️  TERMS OF SERVICE WARNING  ⚠️\n\n"
            "Automating Discord input may violate:\n"
            "• Discord Terms of Service\n"
            "• Server-specific rules\n\n"
            "This may result in account suspension or ban.\n\n"
            "Do you accept full responsibility and want to continue?",
            icon='warning'
        )
        return result
    
    def _stop_browser_test(self) -> None:
        self._browser_stop_event.set()
    
    def _calm_sleep(self, duration: float) -> None:
        end_time = time.monotonic() + duration
        while time.monotonic() < end_time:
            if self._stop_event.is_set() or self._browser_stop_event.is_set():
                break
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue
            time.sleep(0.1)
    
    def _open_edge_and_navigate(self) -> None:
        try:
            self._browser_stop_event.clear()
            target_link = self.target_url.get().strip()
            if not target_link:
                return
            
            self.logger.info("Opening Edge and navigating...")
            self._log_command("[SYSTEM] Opening Edge...")
            
            pyautogui.press('win')
            time.sleep(1.0)
            pyautogui.write("edge")
            time.sleep(1.0)
            pyautogui.press('enter')
            
            self._calm_sleep(5.0)
            
            pyautogui.hotkey('ctrl', 'e')
            time.sleep(1.0)
            pyautogui.press('backspace')
            time.sleep(0.5)
            pyautogui.write(target_link)
            time.sleep(0.5)
            pyautogui.press('enter')
            
            self._calm_sleep(30.0)
            
        except Exception as e:
            self.logger.error(f"Failed to open Edge: {e}")
    
    def _perform_ctrl_r_refresh(self) -> None:
        try:
            pyautogui.hotkey('ctrl', 'r')
            self._calm_sleep(30.0)
        except Exception as e:
            self.logger.error(f"Ctrl+R Refresh failed: {e}")
    
    def _restart_discord_sequence(self) -> None:
        try:
            pyautogui.hotkey('alt', 'f4')
            time.sleep(5.0)
            self._open_edge_and_navigate()
        except Exception as e:
            self.logger.error(f"Restart sequence failed: {e}")
    
    def _start_advanced_mode(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showwarning("Already Running", "Bot is already running. Stop it first.")
            return
        
        if not self._show_tos_warning():
            return
        
        if self.advanced_interval.get() < MIN_INTERVAL:
            messagebox.showerror("Invalid Interval", f"Minimum interval is {MIN_INTERVAL} seconds.")
            return
        
        self.current_mode = "advanced"
        self._stop_event.clear()
        self._pause_event.clear()
        self._is_paused = False
        
        self.gem_hunt_count = 0
        
        self.stats.sessions += 1
        self.stats.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_statistics()
        
        self.worker = threading.Thread(target=self._run_advanced_mode, daemon=True)
        self.worker.start()
        
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.btn_pause.config(state="normal")
        self.status_label.config(text="🔵 Advanced Mode Running... Ctrl+P to stop")
        
        self.logger.info("Advanced mode started")
        self._log_command("[SYSTEM] Advanced mode started")
    
    def stop(self) -> None:
        self._stop_event.set()
        self._pause_event.clear()
        
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=3.0)
        
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.btn_pause.config(state="disabled", text="⏸ Pause")
        self.status_label.config(text="⏹ Stopped. Ready to start.")
        self._is_paused = False
        
        self.logger.info("Bot stopped")
        self._log_command("[SYSTEM] Bot stopped")
        
        self.current_mode = "none"
        self._save_statistics()
    
    def _toggle_pause(self) -> None:
        """Toggle pause with 5-second countdown on resume."""
        if self._is_paused:
            # Resume with 5-second countdown
            self._start_resume_countdown()
        else:
            # Pause immediately
            self._pause_event.set()
            self._is_paused = True
            self.btn_pause.config(text="▶ Resume")
            self.status_label.config(text="⏸ Paused - Click Resume to continue")
            self.logger.info("Paused")
            self._log_command("[SYSTEM] Paused")
    
    def _start_resume_countdown(self) -> None:
        """Start 5-second countdown before resuming."""
        if self._resume_countdown_active:
            return
        
        self._resume_countdown_active = True
        
        def countdown():
            for i in range(5, 0, -1):
                if self._stop_event.is_set():
                    self._resume_countdown_active = False
                    return
                self.root.after(0, lambda c=i: self.status_label.config(text=f"⏳ Resuming in {c} seconds... Focus Discord!"))
                time.sleep(1.0)
            
            self._pause_event.clear()
            self._is_paused = False
            self._resume_countdown_active = False
            self.root.after(0, lambda: self.btn_pause.config(text="⏸ Pause"))
            self.root.after(0, lambda: self.status_label.config(text="🟢 Resumed - Running..."))
            self.logger.info("Resumed after countdown")
            self._log_command("[SYSTEM] Resumed")
        
        threading.Thread(target=countdown, daemon=True).start()
    
    def _run_advanced_mode(self) -> None:
        """Worker thread for advanced mode."""
        rng = random.Random()
        session_start = time.monotonic()
        last_random_text_time = time.monotonic()
        last_refresh_time = time.monotonic()
        random_text_interval = rng.uniform(300, 600)
        
        # Build command pool
        core_commands = [
            "owo hunt",
            "owo coinflip",
            "owo slots",
            "owo battle",
            "owo cash",
            "owo zoo"
        ]
        
        pray_command = "owo pray"
        daily_command = "owo daily"
        
        optional_commands = []
        if self.var_enable_sell_all.get():
            optional_commands.append("owo sell all")
        optional_commands.extend(["owo vote", "owo quest"])
        
        # Get custom commands
        custom_commands = []
        for cmd_var in [self.custom_cmd_1.get(), self.custom_cmd_2.get(), self.custom_cmd_3.get()]:
            if cmd_var and not cmd_var.startswith("e.g."):
                custom_commands.append(cmd_var)
        
        action_commands = [
            "owo owo cuddle", "owo owo hug", "owo owo kiss", "owo owo lick",
            "owo owo pat", "owo owo poke", "owo owo slap", "owo owo bite"
        ] if self.var_ultra_mode.get() else []
        
        meme_commands = [
            f"owo drake {self.TARGET_USER}",
            f"owo headpat {self.TARGET_USER}",
            f"owo slapcar {self.TARGET_USER}"
        ] if self.var_meme_mode.get() else []
        
        utility_commands = [
            "owo ping", "owo stats", "owo rules"
        ] if self.var_utility_mode.get() else []
        
        main_commands = core_commands + optional_commands + custom_commands
        
        try:
            # Initial countdown
            for i in range(5, 0, -1):
                if self._stop_event.is_set():
                    return
                self.root.after(0, lambda count=i: self.status_label.config(text=f"Starting in {count}s..."))
                self._calm_sleep(1.0)
            
            # Startup sequence
            if not self.var_dry_run.get():
                self.status_label.config(text="🚀 Running Startup Sequence...")
                self._open_edge_and_navigate()
            
            iteration = 0
            while not self._stop_event.is_set():
                try:
                    # Handle pause
                    while self._pause_event.is_set() and not self._stop_event.is_set():
                        time.sleep(0.1)
                    
                    if self._stop_event.is_set():
                        break
                    
                    current_time = time.monotonic()
                    elapsed_time = current_time - session_start
                    
                    # Update runtime display
                    hours = int(elapsed_time // 3600)
                    minutes = int((elapsed_time % 3600) // 60)
                    seconds = int(elapsed_time % 60)
                    self.root.after(0, lambda h=hours, m=minutes, s=seconds: 
                        self.runtime_label.config(text=f"{h}h {m}m {s}s"))
                    
                    # === MAX RUNTIME CHECK ===
                    if self.var_max_runtime.get():
                        max_runtime_sec = self.max_runtime_hours.get() * 3600
                        if elapsed_time >= max_runtime_sec:
                            self.logger.warning(f"Max runtime limit reached ({self.max_runtime_hours.get()}h). Auto-stopping.")
                            self._log_command(f"[SAFETY] Max runtime reached - auto-stopping")
                            self.root.after(0, lambda: messagebox.showinfo(
                                "Max Runtime", 
                                f"Bot auto-stopped after {self.max_runtime_hours.get()} hours."
                            ))
                            break
                    
                    # === ACTIVITY RANDOMIZER (AFK Simulation) ===
                    if self.var_activity_randomizer.get():
                        if rng.randint(1, 100) <= self.afk_chance.get():
                            afk_duration = rng.uniform(
                                self.afk_duration_min.get(), 
                                self.afk_duration_max.get()
                            )
                            self.logger.info(f"[AFK] Simulating idle for {afk_duration:.1f}s")
                            self._log_command(f"[AFK] Going idle for {afk_duration:.0f}s...")
                            self.root.after(0, lambda d=afk_duration: 
                                self.status_label.config(text=f"💤 Simulating AFK ({d:.0f}s)..."))
                            self._calm_sleep(afk_duration)
                            continue
                    
                    # Check Auto Restart
                    restart_interval_sec = self.restart_interval.get() * 60
                    if self.var_auto_restart.get() and elapsed_time >= restart_interval_sec:
                        session_start = current_time
                        if not self.var_dry_run.get():
                            self.status_label.config(text="🔄 Performing Auto Restart...")
                            self._restart_discord_sequence()
                            last_refresh_time = time.monotonic()
                            last_random_text_time = time.monotonic()
                        continue
                    
                    # Check Auto Refresh
                    refresh_interval_sec = self.refresh_interval.get() * 60
                    if self.var_auto_refresh.get() and (current_time - last_refresh_time) >= refresh_interval_sec:
                        if not self.var_dry_run.get():
                            self.status_label.config(text="🔄 Performing Auto Refresh...")
                            self._perform_ctrl_r_refresh()
                        last_refresh_time = time.monotonic()
                        continue
                    
                    # Random text
                    if self.var_enable_random_text.get() and (current_time - last_random_text_time) >= random_text_interval:
                        self._send_random_text(rng)
                        last_random_text_time = current_time
                        random_text_interval = rng.uniform(300, 600)
                        self._calm_sleep(rng.uniform(2.0, 4.0))
                    
                    # Pick commands
                    commands_to_run = []
                    
                    available_main = [cmd for cmd in main_commands if self._can_use_command(cmd, 10.0)]
                    if available_main:
                        num_main = rng.randint(3, min(5, len(available_main)))
                        commands_to_run.extend(rng.sample(available_main, num_main))
                    
                    if self._can_use_command(pray_command, 150.0):
                        if rng.random() < 0.4:
                            commands_to_run.append(pray_command)
                    
                    if self._can_use_command(daily_command, 300.0):
                        if rng.random() < 0.3:
                            commands_to_run.append(daily_command)
                    
                    # Special commands
                    if rng.random() < 0.20:
                        special_pool = []
                        if action_commands and rng.random() < 0.08:
                            available_actions = [cmd for cmd in action_commands if self._can_use_command(cmd, 30.0)]
                            if available_actions:
                                special_pool.extend(available_actions)
                        if meme_commands and rng.random() < 0.12:
                            available_memes = [cmd for cmd in meme_commands if self._can_use_command(cmd, 30.0)]
                            if available_memes:
                                special_pool.extend(available_memes)
                        if utility_commands and rng.random() < 0.12:
                            available_utils = [cmd for cmd in utility_commands if self._can_use_command(cmd, 30.0)]
                            if available_utils:
                                special_pool.extend(available_utils)
                        
                        if special_pool:
                            commands_to_run.append(rng.choice(special_pool))
                    
                    rng.shuffle(commands_to_run)
                    
                    for cmd_base in commands_to_run:
                        if self._stop_event.is_set() or self._pause_event.is_set():
                            break
                        
                        command = self._generate_advanced_command(cmd_base, rng)
                        self._mark_command_used(cmd_base)
                        
                        if "hunt" in cmd_base.lower():
                            self.gem_hunt_count += 1
                        
                        self._update_preview(f"Next: {command}")
                        
                        if self.var_dry_run.get():
                            self._log_command(f"[DRY-RUN] {command}")
                        else:
                            self._type_and_send(command, "advanced", rng)
                        
                        # === ANTI-DETECTION DELAYS ===
                        if self.var_anti_detection.get():
                            delay = rng.uniform(self.delay_min.get(), self.delay_max.get())
                        else:
                            delay = rng.uniform(1.0, 2.0)
                        self._calm_sleep(delay)
                    
                    # Auto-use gems
                    if self.var_auto_use_gems.get() and not self.var_dry_run.get():
                        threshold = self.gem_use_threshold.get()
                        if threshold > 0 and self.gem_hunt_count >= threshold:
                            gem_ids_str = self.gem_ids_var.get()
                            gem_ids = [gid.strip() for gid in gem_ids_str.split() if gid.strip().isdigit()]
                            
                            if gem_ids:
                                gem_command = f"owo use {' '.join(gem_ids)}"
                                self._type_and_send(gem_command, "advanced", rng)
                                self._log_command(f"[GEM AUTO-USE] {gem_command}")
                                self.gem_hunt_count = 0
                                self._calm_sleep(rng.uniform(1.5, 2.5))
                    
                    # Wait for interval
                    interval = self.advanced_interval.get()
                    for remaining in range(interval, 0, -1):
                        if self._stop_event.is_set() or self._pause_event.is_set():
                            break
                        status_msg = f"🔵 Next iteration in {remaining}s..."
                        self.root.after(0, lambda msg=status_msg: self.status_label.config(text=msg))
                        self._calm_sleep(1.0)
                    
                    iteration += 1
                
                except Exception as loop_error:
                    self.logger.error(f"Error in main loop: {loop_error}")
                    self._calm_sleep(5.0)
        
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            self.stats.errors += 1
        finally:
            runtime = int(time.monotonic() - session_start)
            self.stats.total_runtime += runtime
            self._save_statistics()
            self.root.after(0, self.stop)
    
    def _can_use_command(self, command: str, cooldown_seconds: float) -> bool:
        now = time.monotonic()
        last_used = self.command_last_used.get(command, 0)
        return (now - last_used) >= cooldown_seconds
    
    def _mark_command_used(self, command: str) -> None:
        self.command_last_used[command] = time.monotonic()
    
    def _generate_random_text(self, rng: random.Random) -> str:
        num_sentences = rng.randint(20, 30)
        sentences = rng.sample(self.random_texts, min(num_sentences, len(self.random_texts)))
        return ' '.join(sentences)
    
    def _send_random_text(self, rng: random.Random) -> None:
        random_text = self._generate_random_text(rng)
        self._type_and_send(random_text, "advanced", rng, is_random_text=True)
    
    def _generate_advanced_command(self, base_cmd: str, rng: random.Random) -> str:
        # Handle prefix replacement
        if base_cmd.startswith("owo "):
            if self.var_owo_only.get():
                pass  # Keep "owo" as-is
            elif self.var_advanced_prefix.get():
                new_prefix = rng.choice(["owo", "o"])
                base_cmd = new_prefix + base_cmd[3:]  # Replace "owo" with new prefix
        
        if "coinflip" in base_cmd:
            amount = self._generate_unique_amount("coinflip", 1, 500, rng)
            return f"{base_cmd} {amount}"
        elif "slots" in base_cmd:
            amount = self._generate_unique_amount("slots", 1, 500, rng)
            return f"{base_cmd} {amount}"
        else:
            return base_cmd
    
    def _generate_unique_amount(self, key: str, min_val: int, max_val: int, rng: random.Random) -> int:
        amount = rng.randint(min_val, max_val)
        retries = 0
        while amount == self.previous_amounts.get(key, -1) and retries < 10:
            amount = rng.randint(min_val, max_val)
            retries += 1
        self.previous_amounts[key] = amount
        return amount
    
    def _type_and_send(self, command: str, mode: str, rng: random.Random, is_random_text: bool = False) -> None:
        if self._stop_event.is_set() or self._pause_event.is_set():
            return
        
        try:
            wpm = self.typing_wpm.get()
            chars_per_second = (wpm * 5) / 60
            delay_per_char = 1.0 / chars_per_second
            
            for char in command:
                if self._stop_event.is_set() or self._pause_event.is_set():
                    break
                # Use write() for alphanumeric, press() for special chars
                if char.isalnum() or char in ' .,!?-_':
                    pyautogui.write(char, interval=0)
                else:
                    pyautogui.press(char) if len(char) == 1 else None
                variance = rng.uniform(0.8, 1.2)
                time.sleep(delay_per_char * variance)
            
            if not self._stop_event.is_set() and not self._pause_event.is_set():
                pyautogui.press('enter')
                
                if not is_random_text:
                    self.stats.commands_sent += 1
                    cmd_type = mode
                    self.stats.commands_by_type[cmd_type] = self.stats.commands_by_type.get(cmd_type, 0) + 1
                
                cmd_preview = command[:40] + "..." if len(command) > 40 else command
                self.root.after(0, lambda: self.status_label.config(text=f"✓ Sent: {cmd_preview}"))
                self._log_command(f"[{mode.upper()}] {command}" if not is_random_text else f"[RANDOM] {command[:30]}...")
                
                self._calm_sleep(rng.uniform(0.8, 1.5))
        
        except Exception as e:
            self.logger.error(f"Error typing command: {e}")
            self.stats.errors += 1
    
    def _update_preview(self, text: str) -> None:
        def update():
            self.preview_text.config(state='normal')
            self.preview_text.delete('1.0', tk.END)
            self.preview_text.insert('1.0', text)
            self.preview_text.config(state='disabled')
        self.root.after(0, update)
    
    def _log_command(self, command: str) -> None:
        def log():
            self.command_log.config(state='normal')
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.command_log.insert('1.0', f"[{timestamp}] {command}\n")
            lines = int(self.command_log.index('end-1c').split('.')[0])
            if lines > 50:
                self.command_log.delete(f"{lines-50}.0", tk.END)
            self.command_log.config(state='disabled')
        self.root.after(0, log)
    
    def _update_stats_display(self) -> None:
        self.stats_text.delete('1.0', tk.END)
        
        hours = self.stats.total_runtime // 3600
        minutes = (self.stats.total_runtime % 3600) // 60
        seconds = self.stats.total_runtime % 60
        
        commands_per_hour = 0
        if self.stats.total_runtime > 0:
            commands_per_hour = int((self.stats.commands_sent / self.stats.total_runtime) * 3600)
        
        avg_per_session = 0
        if self.stats.sessions > 0:
            avg_per_session = self.stats.commands_sent // self.stats.sessions
        
        stats_content = f"""
╔════════════════════════════════════════════════════════════════╗
║                    📊 STATISTICS DASHBOARD                     ║
╚════════════════════════════════════════════════════════════════╝

📈 OVERALL METRICS
────────────────────────────────────────────────────────────────
Total Commands Sent:         {self.stats.commands_sent:,}
Total Runtime:               {hours}h {minutes}m {seconds}s
Total Sessions:              {self.stats.sessions}
Average Commands/Session:    {avg_per_session}
Commands Per Hour:           {commands_per_hour:,}
Errors Encountered:          {self.stats.errors}
Last Run:                    {self.stats.last_run or 'Never'}
"""
        self.stats_text.insert('1.0', stats_content)
    
    def _clear_stats(self) -> None:
        if messagebox.askyesno("Clear Statistics", "Clear all statistics?"):
            self.stats = BotStats()
            self._save_statistics()
            self._update_stats_display()
    
    def _update_logs_display(self) -> None:
        try:
            if LOG_FILE.exists():
                with open(LOG_FILE, 'r') as f:
                    lines = f.readlines()
                    self.logs_text.delete('1.0', tk.END)
                    self.logs_text.insert('1.0', ''.join(lines[-500:]))
                    self.logs_text.see(tk.END)
        except Exception as e:
            self.logger.error(f"Failed to update logs: {e}")
    
    def _clear_logs(self) -> None:
        if messagebox.askyesno("Clear Logs", "Clear all logs?"):
            try:
                with open(LOG_FILE, 'w') as f:
                    f.write("")
                self._update_logs_display()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")
    
    def _on_closing(self) -> None:
        if self.worker and self.worker.is_alive():
            if messagebox.askokcancel("Quit", "Bot is running. Stop and quit?"):
                self.stop()
                self._cleanup_hotkeys()
                self.root.destroy()
        else:
            self._cleanup_hotkeys()
            self.root.destroy()


def run_self_tests() -> bool:
    """Run unit tests."""
    print("=" * 60)
    print("God OwO Bot v3 - Self Test Mode")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Test 1: BotStats
    print("\nTest 1: BotStats serialization...")
    try:
        stats = BotStats(commands_sent=100, sessions=5)
        data = stats.to_dict()
        stats2 = BotStats.from_dict(data)
        assert stats2.commands_sent == 100
        print("  ✓ BotStats works")
        passed += 1
    except AssertionError as e:
        print(f"  ✗ FAILED: {e}")
        failed += 1
    
    # Test 2: Defaults
    print("\nTest 2: Default values...")
    try:
        assert GodOwoBotV3.TARGET_USER == "@owo"
        print("  ✓ Target user hardcoded correctly")
        passed += 1
    except AssertionError as e:
        print(f"  ✗ FAILED: {e}")
        failed += 1
    
    print("\n" + "=" * 60)
    print(f"Tests Passed: {passed}")
    print(f"Tests Failed: {failed}")
    print("=" * 60)
    
    return failed == 0


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        success = run_self_tests()
        sys.exit(0 if success else 1)
    
    root = tk.Tk()
    app = GodOwoBotV3(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        if hasattr(app, '_cleanup_hotkeys'):
            app._cleanup_hotkeys()
        sys.exit(0)


if __name__ == "__main__":
    main()
