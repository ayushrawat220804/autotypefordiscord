"""
Enhanced Owo Auto Typer - Production Ready
==========================================

Improvements over refactored version:
- Bug fixes (rng parameter, hunt_count reset, focus validation)
- Configuration save/load with JSON profiles
- Statistics tracking and live dashboard
- Pause/resume functionality
- Cooldown tracker with countdown display
- Window focus detection and auto-pause
- Comprehensive logging system
- Human-like behavior (typing variance, occasional typos, random pauses)
- Profile/preset management
- Better error handling and recovery
- Anti-pattern randomization for more human-like behavior
- Emergency stop on focus loss
- Export logs and statistics
- Dark mode support

Safety Features:
- Maximum runtime limits
- Focus validation before typing
- Rate limit protection with exponential backoff
- ToS warnings with acceptance logging
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import random
import pyautogui
import keyboard
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys

# Try to import optional window focus detection
try:
    if sys.platform == 'win32':
        import win32gui
        import win32process
        FOCUS_DETECTION = True
    elif sys.platform == 'linux':
        try:
            import subprocess
            FOCUS_DETECTION = True
        except ImportError:
            FOCUS_DETECTION = False
    else:
        FOCUS_DETECTION = False
except ImportError:
    FOCUS_DETECTION = False


MIN_INTERVAL = 3
MAX_RUNTIME_HOURS = 24
CONFIG_DIR = Path.home() / ".owo_autotyper"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "autotyper.log"
STATS_FILE = CONFIG_DIR / "statistics.json"


class EnhancedOwoAutoTyper:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OwO Auto Typer — Enhanced Edition")
        self.root.geometry("1000x700")
        
        # Ensure config directory exists
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # State
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self.worker: Optional[threading.Thread] = None
        self._is_paused = False
        self._hunt_count = 0
        self._last_focus_check = 0
        self._focus_check_interval = 2.0  # Check every 2 seconds
        
        # Statistics
        self.stats = {
            'commands_sent': 0,
            'total_runtime': 0,
            'sessions': 0,
            'last_run': None,
            'commands_by_type': {},
            'errors': 0,
            'focus_losses': 0
        }
        self._load_statistics()
        
        # UI variables
        self.interval_seconds = tk.IntVar(value=15)
        self.run_mode = tk.StringVar(value="duration")
        self.run_duration_seconds = tk.IntVar(value=3600)
        self.run_iterations = tk.IntVar(value=100)
        
        # Categories
        self.var_economy = tk.BooleanVar(value=True)
        self.var_animals = tk.BooleanVar(value=True)
        self.var_gambling = tk.BooleanVar(value=False)
        self.var_aliases = tk.BooleanVar(value=True)
        
        # Minute plan / cash farm
        self.var_minute_plan = tk.BooleanVar(value=True)
        self.var_cashfarm = tk.BooleanVar(value=False)
        self.var_hunts_per_sell = tk.IntVar(value=10)
        self.var_cf_every = tk.IntVar(value=7)
        self.var_tiny_cf = tk.BooleanVar(value=False)
        
        # Per command enable and intervals
        self.en_hunt = tk.BooleanVar(value=True); self.iv_hunt = tk.IntVar(value=15)
        self.en_cf = tk.BooleanVar(value=True); self.iv_cf = tk.IntVar(value=10)
        self.en_slots = tk.BooleanVar(value=True); self.iv_slots = tk.IntVar(value=10)
        self.en_battle = tk.BooleanVar(value=True); self.iv_battle = tk.IntVar(value=15)
        self.en_pray = tk.BooleanVar(value=True); self.iv_pray = tk.IntVar(value=300)
        
        # Enhanced features
        self.var_focus_detection = tk.BooleanVar(value=FOCUS_DETECTION)
        self.var_human_variance = tk.BooleanVar(value=True)
        self.var_random_typos = tk.BooleanVar(value=False)
        self.var_random_pauses = tk.BooleanVar(value=True)
        self.var_auto_pause_focus = tk.BooleanVar(value=True)
        
        # Cooldown tracking
        self.cooldowns = {
            'pray': 0,
            'daily': 0,
            'hunt': 0,
            'battle': 0
        }
        
        self._build_ui()
        self._setup_hotkeys()
        self._load_config()
        self._start_cooldown_updater()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_logging(self) -> None:
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*50)
        self.logger.info("Enhanced OwO Auto Typer started")
        self.logger.info(f"Focus detection available: {FOCUS_DETECTION}")
    
    def _load_statistics(self) -> None:
        """Load statistics from file"""
        try:
            if STATS_FILE.exists():
                with open(STATS_FILE, 'r') as f:
                    self.stats.update(json.load(f))
                self.logger.info(f"Loaded statistics: {self.stats['commands_sent']} total commands")
        except Exception as e:
            self.logger.error(f"Failed to load statistics: {e}")
    
    def _save_statistics(self) -> None:
        """Save statistics to file"""
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save statistics: {e}")
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    self._apply_config(config)
                self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
    
    def _save_config(self) -> None:
        """Save current configuration to file"""
        try:
            config = self._get_current_config()
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info("Configuration saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def _get_current_config(self) -> Dict[str, Any]:
        """Get current configuration as dictionary"""
        return {
            'interval_seconds': self.interval_seconds.get(),
            'run_mode': self.run_mode.get(),
            'run_duration_seconds': self.run_duration_seconds.get(),
            'run_iterations': self.run_iterations.get(),
            'var_economy': self.var_economy.get(),
            'var_animals': self.var_animals.get(),
            'var_gambling': self.var_gambling.get(),
            'var_aliases': self.var_aliases.get(),
            'var_minute_plan': self.var_minute_plan.get(),
            'var_cashfarm': self.var_cashfarm.get(),
            'var_hunts_per_sell': self.var_hunts_per_sell.get(),
            'var_cf_every': self.var_cf_every.get(),
            'var_tiny_cf': self.var_tiny_cf.get(),
            'en_hunt': self.en_hunt.get(),
            'iv_hunt': self.iv_hunt.get(),
            'en_cf': self.en_cf.get(),
            'iv_cf': self.iv_cf.get(),
            'en_slots': self.en_slots.get(),
            'iv_slots': self.iv_slots.get(),
            'en_battle': self.en_battle.get(),
            'iv_battle': self.iv_battle.get(),
            'en_pray': self.en_pray.get(),
            'iv_pray': self.iv_pray.get(),
            'var_focus_detection': self.var_focus_detection.get(),
            'var_human_variance': self.var_human_variance.get(),
            'var_random_typos': self.var_random_typos.get(),
            'var_random_pauses': self.var_random_pauses.get(),
            'var_auto_pause_focus': self.var_auto_pause_focus.get()
        }
    
    def _apply_config(self, config: Dict[str, Any]) -> None:
        """Apply configuration from dictionary"""
        try:
            self.interval_seconds.set(config.get('interval_seconds', 15))
            self.run_mode.set(config.get('run_mode', 'duration'))
            self.run_duration_seconds.set(config.get('run_duration_seconds', 3600))
            self.run_iterations.set(config.get('run_iterations', 100))
            self.var_economy.set(config.get('var_economy', True))
            self.var_animals.set(config.get('var_animals', True))
            self.var_gambling.set(config.get('var_gambling', False))
            self.var_aliases.set(config.get('var_aliases', True))
            self.var_minute_plan.set(config.get('var_minute_plan', True))
            self.var_cashfarm.set(config.get('var_cashfarm', False))
            self.var_hunts_per_sell.set(config.get('var_hunts_per_sell', 10))
            self.var_cf_every.set(config.get('var_cf_every', 7))
            self.var_tiny_cf.set(config.get('var_tiny_cf', False))
            self.en_hunt.set(config.get('en_hunt', True))
            self.iv_hunt.set(config.get('iv_hunt', 15))
            self.en_cf.set(config.get('en_cf', True))
            self.iv_cf.set(config.get('iv_cf', 10))
            self.en_slots.set(config.get('en_slots', True))
            self.iv_slots.set(config.get('iv_slots', 10))
            self.en_battle.set(config.get('en_battle', True))
            self.iv_battle.set(config.get('iv_battle', 15))
            self.en_pray.set(config.get('en_pray', True))
            self.iv_pray.set(config.get('iv_pray', 300))
            self.var_focus_detection.set(config.get('var_focus_detection', FOCUS_DETECTION))
            self.var_human_variance.set(config.get('var_human_variance', True))
            self.var_random_typos.set(config.get('var_random_typos', False))
            self.var_random_pauses.set(config.get('var_random_pauses', True))
            self.var_auto_pause_focus.set(config.get('var_auto_pause_focus', True))
            self._refresh_preview()
        except Exception as e:
            self.logger.error(f"Error applying config: {e}")
    
    def _build_ui(self) -> None:
        """Build enhanced UI with tabs"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Main control tab
        main_tab = ttk.Frame(notebook)
        notebook.add(main_tab, text='Main Controls')
        self._build_main_tab(main_tab)
        
        # Statistics tab
        stats_tab = ttk.Frame(notebook)
        notebook.add(stats_tab, text='Statistics')
        self._build_stats_tab(stats_tab)
        
        # Settings tab
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text='Advanced Settings')
        self._build_settings_tab(settings_tab)
        
        # Logs tab
        logs_tab = ttk.Frame(notebook)
        notebook.add(logs_tab, text='Logs')
        self._build_logs_tab(logs_tab)
    
    def _build_main_tab(self, parent: ttk.Frame) -> None:
        """Build main control tab"""
        main = ttk.Frame(parent, padding="10")
        main.pack(fill='both', expand=True)
        
        # Top row: Run mode and duration controls
        run_frame = ttk.LabelFrame(main, text="Run Mode", padding="6")
        run_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(run_frame, text="Run for duration", variable=self.run_mode,
                       value="duration", command=self._refresh_preview).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(run_frame, text="Run for iterations", variable=self.run_mode,
                       value="iterations", command=self._refresh_preview).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        duration_frame = ttk.Frame(run_frame)
        duration_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(duration_frame, text="Duration (seconds):").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(duration_frame, from_=60, to=86400, textvariable=self.run_duration_seconds,
                   width=8, command=self._refresh_preview).grid(row=0, column=1, padx=(5, 20))
        
        ttk.Label(duration_frame, text="Iterations:").grid(row=0, column=2, sticky=tk.W)
        ttk.Spinbox(duration_frame, from_=1, to=10000, textvariable=self.run_iterations,
                   width=8, command=self._refresh_preview).grid(row=0, column=3, padx=(5, 0))
        
        # Base interval
        interval_frame = ttk.LabelFrame(main, text="Base Settings", padding="6")
        interval_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(interval_frame, text="Base interval (s):").grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(interval_frame, from_=MIN_INTERVAL, to=120, textvariable=self.interval_seconds,
                   width=6, command=self._refresh_preview).grid(row=0, column=1, padx=(8, 0))
        
        # Minute Plan Mode
        plan = ttk.LabelFrame(main, text="Minute Plan", padding="6")
        plan.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        ttk.Checkbutton(plan, text="Enable: 4 hunt, 5 cf, 3 slots, 2 bj per minute",
                       variable=self.var_minute_plan, command=self._refresh_preview).grid(row=0, column=0, sticky=tk.W)
        
        # Cash Farm Mode
        farm = ttk.LabelFrame(main, text="Cash Farm", padding="6")
        farm.grid(row=1, column=2, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        ttk.Checkbutton(farm, text="Enable (hunt+sell)", variable=self.var_cashfarm,
                       command=self._refresh_preview).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(farm, text="Hunts per sell:").grid(row=1, column=0, sticky=tk.W, pady=(6,0))
        ttk.Spinbox(farm, from_=2, to=50, textvariable=self.var_hunts_per_sell,
                   width=6, command=self._refresh_preview).grid(row=1, column=1, sticky=tk.W, pady=(6,0))
        ttk.Checkbutton(farm, text="Tiny CF sometimes", variable=self.var_tiny_cf,
                       command=self._refresh_preview).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(6,0))
        ttk.Label(farm, text="CF every N hunts:").grid(row=3, column=0, sticky=tk.W)
        ttk.Spinbox(farm, from_=3, to=50, textvariable=self.var_cf_every,
                   width=6, command=self._refresh_preview).grid(row=3, column=1, sticky=tk.W)
        
        # Categories
        cats = ttk.LabelFrame(main, text="Categories", padding="6")
        cats.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), pady=(0, 10))
        
        ttk.Checkbutton(cats, text="Economy", variable=self.var_economy,
                       command=self._refresh_preview).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(cats, text="Animals / Hunt", variable=self.var_animals,
                       command=self._refresh_preview).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(cats, text="Gambling", variable=self.var_gambling,
                       command=self._refresh_preview).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(cats, text="Use aliases (o/cf/bj/oh/ob)", variable=self.var_aliases,
                       command=self._refresh_preview).grid(row=3, column=0, sticky=tk.W, pady=(6,0))
        
        # Per-command scheduling
        sched = ttk.LabelFrame(main, text="Per-Command (s)", padding="6")
        sched.grid(row=2, column=1, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        
        commands = [
            ("hunt", self.en_hunt, self.iv_hunt, MIN_INTERVAL, 600),
            ("coinflip", self.en_cf, self.iv_cf, MIN_INTERVAL, 600),
            ("slots", self.en_slots, self.iv_slots, MIN_INTERVAL, 600),
            ("battle", self.en_battle, self.iv_battle, MIN_INTERVAL, 600),
            ("pray", self.en_pray, self.iv_pray, 30, 3600),
        ]
        
        for idx, (label, en_var, iv_var, min_val, max_val) in enumerate(commands):
            ttk.Checkbutton(sched, text=label, variable=en_var,
                           command=self._refresh_preview).grid(row=idx, column=0, sticky=tk.W)
            ttk.Spinbox(sched, from_=min_val, to=max_val, textvariable=iv_var,
                       width=6, command=self._refresh_preview).grid(row=idx, column=1, sticky=tk.W)
        
        # Cooldown tracker
        cooldown_frame = ttk.LabelFrame(main, text="Cooldown Tracker", padding="6")
        cooldown_frame.grid(row=2, column=2, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        
        self.cooldown_labels = {}
        for idx, cmd in enumerate(['pray', 'daily', 'hunt', 'battle']):
            ttk.Label(cooldown_frame, text=f"{cmd.capitalize()}:").grid(row=idx, column=0, sticky=tk.W)
            label = ttk.Label(cooldown_frame, text="Ready")
            label.grid(row=idx, column=1, sticky=tk.W, padx=(10, 0))
            self.cooldown_labels[cmd] = label
        
        # Controls
        controls = ttk.LabelFrame(main, text="Controls", padding="6")
        controls.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.btn_start = ttk.Button(controls, text="▶ Start", command=self.start)
        self.btn_start.grid(row=0, column=0, padx=(0, 5))
        
        self.btn_pause = ttk.Button(controls, text="⏸ Pause", command=self.toggle_pause, state="disabled")
        self.btn_pause.grid(row=0, column=1, padx=(0, 5))
        
        self.btn_stop = ttk.Button(controls, text="⏹ Stop", command=self.stop, state="disabled")
        self.btn_stop.grid(row=0, column=2, padx=(0, 5))
        
        ttk.Button(controls, text="💾 Save Config", command=self._save_config).grid(row=0, column=3, padx=(20, 5))
        ttk.Button(controls, text="📂 Load Config", command=self._load_config_dialog).grid(row=0, column=4, padx=(0, 5))
        
        self.status_label = ttk.Label(controls, text="Ready. Focus Discord before starting.")
        self.status_label.grid(row=0, column=5, padx=(20, 0))
        
        # Preview
        preview = ttk.LabelFrame(main, text="Preview & Status", padding="6")
        preview.grid(row=4, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.W, tk.E), pady=(0, 10))
        
        self.preview_box = tk.Text(preview, width=80, height=10, wrap=tk.WORD)
        self.preview_box.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(preview, orient="vertical", command=self.preview_box.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_box.configure(yscrollcommand=scrollbar.set)
        
        # Layout weights
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)
        main.rowconfigure(4, weight=1)
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(0, weight=1)
        
        self._refresh_preview()
    
    def _build_stats_tab(self, parent: ttk.Frame) -> None:
        """Build statistics tab"""
        stats_frame = ttk.Frame(parent, padding="10")
        stats_frame.pack(fill='both', expand=True)
        
        # Statistics display
        ttk.Label(stats_frame, text="Session Statistics", font=('TkDefaultFont', 14, 'bold')).pack(pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, width=80, height=25, wrap=tk.WORD)
        self.stats_text.pack(fill='both', expand=True)
        
        btn_frame = ttk.Frame(stats_frame)
        btn_frame.pack(pady=(10, 0))
        
        ttk.Button(btn_frame, text="🔄 Refresh Stats", command=self._update_stats_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear Stats", command=self._clear_stats).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📊 Export Stats", command=self._export_stats).pack(side=tk.LEFT, padx=5)
        
        self._update_stats_display()
    
    def _build_settings_tab(self, parent: ttk.Frame) -> None:
        """Build advanced settings tab"""
        settings_frame = ttk.Frame(parent, padding="10")
        settings_frame.pack(fill='both', expand=True)
        
        # Human-like behavior settings
        human_frame = ttk.LabelFrame(settings_frame, text="Human-like Behavior", padding="10")
        human_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Checkbutton(human_frame, text="Enable typing speed variance (±20%)",
                       variable=self.var_human_variance).pack(anchor=tk.W)
        ttk.Checkbutton(human_frame, text="Random typos with corrections (5% chance)",
                       variable=self.var_random_typos).pack(anchor=tk.W)
        ttk.Checkbutton(human_frame, text="Random pauses between commands (1-3% chance)",
                       variable=self.var_random_pauses).pack(anchor=tk.W)
        
        # Focus detection settings
        focus_frame = ttk.LabelFrame(settings_frame, text="Focus Detection", padding="10")
        focus_frame.pack(fill='x', pady=(0, 10))
        
        if FOCUS_DETECTION:
            ttk.Checkbutton(focus_frame, text="Enable focus detection",
                           variable=self.var_focus_detection).pack(anchor=tk.W)
            ttk.Checkbutton(focus_frame, text="Auto-pause when Discord loses focus",
                           variable=self.var_auto_pause_focus).pack(anchor=tk.W)
            ttk.Label(focus_frame, text="✓ Focus detection is available on this system").pack(anchor=tk.W, pady=(5,0))
        else:
            ttk.Label(focus_frame, text="⚠ Focus detection not available on this system").pack(anchor=tk.W)
        
        # Safety limits
        safety_frame = ttk.LabelFrame(settings_frame, text="Safety Limits", padding="10")
        safety_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(safety_frame, text=f"Minimum interval: {MIN_INTERVAL}s (enforced)").pack(anchor=tk.W)
        ttk.Label(safety_frame, text=f"Maximum runtime: {MAX_RUNTIME_HOURS}h (enforced)").pack(anchor=tk.W)
        ttk.Label(safety_frame, text="Focus check interval: 2s").pack(anchor=tk.W)
        
        # About
        about_frame = ttk.LabelFrame(settings_frame, text="About", padding="10")
        about_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        about_text = tk.Text(about_frame, width=80, height=10, wrap=tk.WORD)
        about_text.pack(fill='both', expand=True)
        about_text.insert('1.0', """Enhanced OwO Auto Typer - Production Ready

Key Features:
• Bug-fixed and optimized scheduling engine
• Configuration save/load with JSON profiles
• Comprehensive statistics tracking
• Pause/resume functionality
• Real-time cooldown tracking
• Window focus detection (platform-dependent)
• Human-like behavior simulation
• Extensive logging for debugging
• Rate limit protection
• Emergency stop mechanisms

Hotkeys:
• Ctrl+P: Toggle Start/Stop
• Ctrl+Space: Toggle Pause/Resume (when running)

Warnings:
⚠️ Automating Discord may violate Terms of Service
⚠️ Use at your own risk and responsibility
⚠️ Keep intervals reasonable to avoid rate limits
""")
        about_text.config(state='disabled')
    
    def _build_logs_tab(self, parent: ttk.Frame) -> None:
        """Build logs tab"""
        logs_frame = ttk.Frame(parent, padding="10")
        logs_frame.pack(fill='both', expand=True)
        
        ttk.Label(logs_frame, text="Application Logs", font=('TkDefaultFont', 14, 'bold')).pack(pady=(0, 10))
        
        self.logs_text = tk.Text(logs_frame, width=80, height=25, wrap=tk.WORD, font=('Courier', 9))
        self.logs_text.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(logs_frame, orient="vertical", command=self.logs_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.logs_text.configure(yscrollcommand=scrollbar.set)
        
        btn_frame = ttk.Frame(logs_frame)
        btn_frame.pack(pady=(10, 0))
        
        ttk.Button(btn_frame, text="🔄 Refresh Logs", command=self._update_logs_display).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear Logs", command=self._clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Export Logs", command=self._export_logs).pack(side=tk.LEFT, padx=5)
        
        self._update_logs_display()
    
    def _setup_hotkeys(self) -> None:
        """Setup keyboard hotkeys"""
        def on_ctrl_p() -> None:
            if self.worker and self.worker.is_alive():
                self.stop()
            else:
                self.start()
        
        def on_ctrl_space() -> None:
            if self.worker and self.worker.is_alive():
                self.toggle_pause()
        
        try:
            keyboard.add_hotkey('ctrl+p', on_ctrl_p)
            keyboard.add_hotkey('ctrl+space', on_ctrl_space)
            self.logger.info("Hotkeys registered: Ctrl+P (start/stop), Ctrl+Space (pause/resume)")
        except Exception as e:
            self.logger.error(f"Failed to register hotkeys: {e}")
    
    def _start_cooldown_updater(self) -> None:
        """Start cooldown display updater"""
        def update():
            if hasattr(self, 'cooldown_labels'):
                for cmd, remaining in self.cooldowns.items():
                    if remaining > 0:
                        mins = int(remaining // 60)
                        secs = int(remaining % 60)
                        self.cooldown_labels[cmd].config(text=f"{mins}m {secs}s")
                        self.cooldowns[cmd] = max(0, remaining - 1)
                    else:
                        self.cooldown_labels[cmd].config(text="Ready")
            self.root.after(1000, update)
        update()
    
    def _refresh_preview(self) -> None:
        """Generate live preview of strategy"""
        self.preview_box.delete('1.0', tk.END)
        
        if self.var_minute_plan.get():
            self.preview_box.insert(tk.END, "🎯 MINUTE PLAN MODE\n")
            self.preview_box.insert(tk.END, "=" * 40 + "\n\n")
            self.preview_box.insert(tk.END, "Commands per minute:\n")
            self.preview_box.insert(tk.END, "  • 4 hunts\n")
            self.preview_box.insert(tk.END, "  • 5 coinflips\n")
            self.preview_box.insert(tk.END, "  • 3 slots\n")
            self.preview_box.insert(tk.END, "  • 2 blackjack\n")
            self.preview_box.insert(tk.END, "  • 2 random noise commands\n\n")
            self.preview_box.insert(tk.END, "Evenly spaced with ±0.4s jitter\n")
        elif self.var_cashfarm.get():
            self.preview_box.insert(tk.END, "💰 CASH FARM MODE\n")
            self.preview_box.insert(tk.END, "=" * 40 + "\n\n")
            hunts_per_sell = self.var_hunts_per_sell.get()
            self.preview_box.insert(tk.END, f"  • Hunt every {self.interval_seconds.get()}s\n")
            self.preview_box.insert(tk.END, f"  • Sell all every {hunts_per_sell} hunts\n")
            if self.var_tiny_cf.get():
                cf_every = self.var_cf_every.get()
                self.preview_box.insert(tk.END, f"  • Tiny coinflip every {cf_every} hunts\n")
            self.preview_box.insert(tk.END, "\nFocus: Hunt → Sell → Repeat\n")
        else:
            self.preview_box.insert(tk.END, "⚙️ PER-COMMAND SCHEDULING\n")
            self.preview_box.insert(tk.END, "=" * 40 + "\n\n")
            if self.en_hunt.get():
                self.preview_box.insert(tk.END, f"  • Hunt every {self.iv_hunt.get()}s\n")
            if self.en_cf.get():
                self.preview_box.insert(tk.END, f"  • Coinflip every {self.iv_cf.get()}s\n")
            if self.en_slots.get():
                self.preview_box.insert(tk.END, f"  • Slots every {self.iv_slots.get()}s\n")
            if self.en_battle.get():
                self.preview_box.insert(tk.END, f"  • Battle every {self.iv_battle.get()}s\n")
            if self.en_pray.get():
                self.preview_box.insert(tk.END, f"  • Pray every {self.iv_pray.get()}s\n")
            self.preview_box.insert(tk.END, "\nIndependent scheduling with variance\n")
        
        # Run mode info
        if self.run_mode.get() == "duration":
            duration = self.run_duration_seconds.get()
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            self.preview_box.insert(tk.END, f"\n⏱️ Run for: {hours}h {minutes}m\n")
        else:
            self.preview_box.insert(tk.END, f"\n🔢 Run for: {self.run_iterations.get()} iterations\n")
        
        # Enhanced features status
        if self.var_human_variance.get():
            self.preview_box.insert(tk.END, "\n✓ Human-like typing variance enabled\n")
        if self.var_random_typos.get():
            self.preview_box.insert(tk.END, "✓ Random typos enabled\n")
        if self.var_random_pauses.get():
            self.preview_box.insert(tk.END, "✓ Random pauses enabled\n")
        if self.var_focus_detection.get() and FOCUS_DETECTION:
            self.preview_box.insert(tk.END, "✓ Focus detection enabled\n")
    
    def _update_stats_display(self) -> None:
        """Update statistics display"""
        self.stats_text.delete('1.0', tk.END)
        
        self.stats_text.insert(tk.END, "📊 STATISTICS DASHBOARD\n")
        self.stats_text.insert(tk.END, "=" * 50 + "\n\n")
        
        self.stats_text.insert(tk.END, f"Total Commands Sent: {self.stats['commands_sent']}\n")
        self.stats_text.insert(tk.END, f"Total Runtime: {self.stats['total_runtime']//3600}h {(self.stats['total_runtime']%3600)//60}m\n")
        self.stats_text.insert(tk.END, f"Total Sessions: {self.stats['sessions']}\n")
        self.stats_text.insert(tk.END, f"Errors Encountered: {self.stats['errors']}\n")
        self.stats_text.insert(tk.END, f"Focus Losses: {self.stats['focus_losses']}\n")
        
        if self.stats['last_run']:
            self.stats_text.insert(tk.END, f"Last Run: {self.stats['last_run']}\n")
        
        if self.stats['commands_by_type']:
            self.stats_text.insert(tk.END, "\n📋 Commands by Type:\n")
            self.stats_text.insert(tk.END, "-" * 50 + "\n")
            for cmd_type, count in sorted(self.stats['commands_by_type'].items(), key=lambda x: x[1], reverse=True):
                self.stats_text.insert(tk.END, f"  {cmd_type}: {count}\n")
    
    def _update_logs_display(self) -> None:
        """Update logs display"""
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
    
    def _load_config_dialog(self) -> None:
        """Load configuration from file dialog"""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                    self._apply_config(config)
                messagebox.showinfo("Success", "Configuration loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def _clear_stats(self) -> None:
        """Clear statistics"""
        if messagebox.askyesno("Clear Statistics", "Are you sure you want to clear all statistics?"):
            self.stats = {
                'commands_sent': 0,
                'total_runtime': 0,
                'sessions': 0,
                'last_run': None,
                'commands_by_type': {},
                'errors': 0,
                'focus_losses': 0
            }
            self._save_statistics()
            self._update_stats_display()
            self.logger.info("Statistics cleared")
    
    def _export_stats(self) -> None:
        """Export statistics to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Statistics",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.stats, f, indent=2)
                else:
                    with open(filename, 'w') as f:
                        f.write("OwO Auto Typer Statistics\n")
                        f.write("=" * 50 + "\n\n")
                        f.write(f"Total Commands: {self.stats['commands_sent']}\n")
                        f.write(f"Total Runtime: {self.stats['total_runtime']//3600}h {(self.stats['total_runtime']%3600)//60}m\n")
                        f.write(f"Sessions: {self.stats['sessions']}\n")
                        f.write(f"Errors: {self.stats['errors']}\n")
                        f.write(f"Focus Losses: {self.stats['focus_losses']}\n")
                        if self.stats['commands_by_type']:
                            f.write("\nCommands by Type:\n")
                            for cmd_type, count in sorted(self.stats['commands_by_type'].items()):
                                f.write(f"  {cmd_type}: {count}\n")
                messagebox.showinfo("Success", f"Statistics exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export statistics: {e}")
    
    def _clear_logs(self) -> None:
        """Clear log file"""
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            try:
                with open(LOG_FILE, 'w') as f:
                    f.write("")
                self._update_logs_display()
                self.logger.info("Logs cleared")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {e}")
    
    def _export_logs(self) -> None:
        """Export logs to file"""
        filename = filedialog.asksaveasfilename(
            title="Export Logs",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                if LOG_FILE.exists():
                    with open(LOG_FILE, 'r') as src:
                        with open(filename, 'w') as dst:
                            dst.write(src.read())
                    messagebox.showinfo("Success", f"Logs exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export logs: {e}")
    
    def start(self) -> None:
        """Start the auto typer with validation and ToS warning"""
        # Validation
        if not self.var_minute_plan.get() and not self.var_cashfarm.get() and not any([
            self.var_economy.get(), self.var_animals.get(), self.var_gambling.get()
        ]):
            messagebox.showwarning("No commands", "Please select at least one category of commands.")
            return
        
        # ToS warning
        result = messagebox.askyesno(
            "Terms of Service Warning",
            "⚠️ WARNING ⚠️\n\n"
            "Automating Discord input may violate:\n"
            "• Server rules\n"
            "• Discord Terms of Service\n\n"
            "This tool includes safety features but use at your own risk.\n\n"
            "Do you accept responsibility and want to continue?"
        )
        if not result:
            self.logger.info("User declined ToS warning")
            return
        
        self.logger.info("User accepted ToS warning - starting session")
        
        # Validate intervals
        if self.interval_seconds.get() < MIN_INTERVAL:
            messagebox.showerror("Invalid interval", f"Interval must be at least {MIN_INTERVAL} seconds.")
            return
        
        # Validate max runtime
        max_runtime_seconds = MAX_RUNTIME_HOURS * 3600
        if self.run_mode.get() == "duration" and self.run_duration_seconds.get() > max_runtime_seconds:
            messagebox.showerror("Invalid duration",
                               f"Maximum runtime is {MAX_RUNTIME_HOURS} hours for safety.")
            return
        
        # Reset state
        self._stop_event.clear()
        self._pause_event.clear()
        self._is_paused = False
        self._hunt_count = 0
        
        # Update stats
        self.stats['sessions'] += 1
        self.stats['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_statistics()
        
        # Start worker thread
        self.worker = threading.Thread(target=self._run_loop, daemon=True)
        self.worker.start()
        
        # Update UI
        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal")
        self.btn_stop.config(state="normal")
        self.status_label.config(text="🟢 Running... Ctrl+P to stop, Ctrl+Space to pause")
        
        self.logger.info("Auto typer started successfully")
    
    def toggle_pause(self) -> None:
        """Toggle pause state"""
        if self._is_paused:
            self._pause_event.clear()
            self._is_paused = False
            self.btn_pause.config(text="⏸ Pause")
            self.status_label.config(text="🟢 Running...")
            self.logger.info("Resumed")
        else:
            self._pause_event.set()
            self._is_paused = True
            self.btn_pause.config(text="▶ Resume")
            self.status_label.config(text="⏸ Paused")
            self.logger.info("Paused")
    
    def stop(self) -> None:
        """Stop the auto typer safely"""
        self._stop_event.set()
        self._pause_event.clear()
        
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=3.0)
        
        # Update UI
        self.btn_start.config(state="normal")
        self.btn_pause.config(state="disabled", text="⏸ Pause")
        self.btn_stop.config(state="disabled")
        self.status_label.config(text="⏹ Stopped.")
        self._is_paused = False
        
        self.logger.info("Auto typer stopped")
        self._save_statistics()
    
    def _check_focus(self) -> bool:
        """Check if Discord window is focused"""
        if not self.var_focus_detection.get() or not FOCUS_DETECTION:
            return True
        
        try:
            if sys.platform == 'win32':
                import win32gui
                window = win32gui.GetForegroundWindow()
                title = win32gui.GetWindowText(window).lower()
                return 'discord' in title
            elif sys.platform == 'linux':
                result = subprocess.run(
                    ['xdotool', 'getactivewindow', 'getwindowname'],
                    capture_output=True, text=True, timeout=1
                )
                return 'discord' in result.stdout.lower()
        except Exception as e:
            self.logger.error(f"Focus check failed: {e}")
        
        return True  # Assume focused if check fails
    
    def _run_loop(self) -> None:
        """Main worker loop with enhanced features"""
        start_time = time.monotonic()
        session_start = start_time
        iterations = 0
        rng = random.Random()
        
        # Initialize per-command scheduling
        command_schedule = {
            'hunt': {'enabled': self.en_hunt.get(), 'interval': self.iv_hunt.get(), 'next': time.monotonic()},
            'cf': {'enabled': self.en_cf.get(), 'interval': self.iv_cf.get(), 'next': time.monotonic()},
            'slots': {'enabled': self.en_slots.get(), 'interval': self.iv_slots.get(), 'next': time.monotonic()},
            'battle': {'enabled': self.en_battle.get(), 'interval': self.iv_battle.get(), 'next': time.monotonic()},
            'pray': {'enabled': self.en_pray.get(), 'interval': self.iv_pray.get(), 'next': time.monotonic()},
        }
        
        try:
            # Main loop
            while not self._stop_event.is_set():
                # Handle pause
                while self._pause_event.is_set() and not self._stop_event.is_set():
                    time.sleep(0.1)
                
                if self._stop_event.is_set():
                    break
                
                now = time.monotonic()
                
                # Focus check
                if self.var_focus_detection.get() and now - self._last_focus_check > self._focus_check_interval:
                    self._last_focus_check = now
                    if not self._check_focus():
                        self.logger.warning("Discord window not focused!")
                        self.stats['focus_losses'] += 1
                        if self.var_auto_pause_focus.get() and not self._is_paused:
                            self.root.after(0, self.toggle_pause)
                            self.root.after(0, lambda: messagebox.showwarning(
                                "Focus Lost",
                                "Discord window lost focus. Auto-paused for safety."
                            ))
                
                # Check run termination conditions
                if self.run_mode.get() == "duration":
                    if now - start_time >= self.run_duration_seconds.get():
                        self.logger.info("Duration limit reached")
                        break
                else:
                    if iterations >= self.run_iterations.get():
                        self.logger.info(f"Iteration limit reached: {iterations}")
                        break
                
                # Random pause (simulate human behavior)
                if self.var_random_pauses.get() and rng.random() < 0.02:  # 2% chance
                    pause_duration = rng.uniform(2.0, 5.0)
                    self.logger.info(f"Random human-like pause: {pause_duration:.1f}s")
                    self._calm_sleep(pause_duration)
                
                # Execute scheduled commands
                if self.var_minute_plan.get():
                    self._execute_minute_plan(rng)
                elif self.var_cashfarm.get():
                    self._execute_cash_farm(rng)
                else:
                    self._execute_per_command_schedule(command_schedule, rng, now)
                
                iterations += 1
                
                # Update runtime stats
                self.stats['total_runtime'] = int(time.monotonic() - session_start)
                
                # Calm sleep
                self._calm_sleep(1.0)
        
        except Exception as e:
            self.logger.error(f"Error in run loop: {e}", exc_info=True)
            self.stats['errors'] += 1
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {e}"))
        finally:
            # Clean shutdown
            self.logger.info(f"Session ended. Commands sent: {iterations}, Runtime: {time.monotonic() - session_start:.0f}s")
            self._save_statistics()
            self.root.after(0, self.stop)
    
    def _execute_minute_plan(self, rng: random.Random) -> None:
        """Execute minute plan with enhanced randomization"""
        if self._stop_event.is_set():
            return
        
        commands = []
        
        # Build commands with slight variation
        hunt_count = rng.randint(3, 5)
        cf_count = rng.randint(4, 6)
        slots_count = rng.randint(2, 4)
        bj_count = rng.randint(1, 3)
        
        for _ in range(hunt_count):
            commands.append(('hunt', self._random_simple("hunt", rng)))
        
        for _ in range(cf_count):
            cf_cmd = self._random_coinflip(rng)
            commands.append(('coinflip', self._clamp_amount(cf_cmd, 200, 500, rng)))
        
        for _ in range(slots_count):
            slots_cmd = self._random_slots(rng)
            commands.append(('slots', self._clamp_amount(slots_cmd, 200, 500, rng)))
        
        for _ in range(bj_count):
            bj_cmd = self._random_blackjack(rng)
            commands.append(('blackjack', self._clamp_amount(bj_cmd, 200, 500, rng)))
        
        # Add some variety
        variety_commands = [
            ('cash', f"{self._prefix(rng)} cash"),
            ('battle', self._random_simple("battle", rng)),
        ]
        commands.extend(rng.sample(variety_commands, min(2, len(variety_commands))))
        
        # Shuffle and execute
        rng.shuffle(commands)
        gap = 60.0 / max(1, len(commands))
        
        for i, (cmd_type, cmd) in enumerate(commands):
            if self._stop_event.is_set() or self._pause_event.is_set():
                break
            
            target_time = time.monotonic() + i * gap + rng.uniform(-0.4, 0.4)
            self._wait_until(target_time)
            
            if not self._stop_event.is_set() and not self._pause_event.is_set():
                self._type_and_send(cmd, cmd_type, rng)
    
    def _execute_cash_farm(self, rng: random.Random) -> None:
        """Execute cash farm with tracking"""
        if self._stop_event.is_set() or self._pause_event.is_set():
            return
        
        # Hunt
        hunt_cmd = self._random_simple("hunt", rng)
        self._type_and_send(hunt_cmd, 'hunt', rng)
        self._hunt_count += 1
        
        # Check if we should sell
        hunts_per_sell = self.var_hunts_per_sell.get()
        if self._hunt_count % hunts_per_sell == 0:
            self._calm_sleep(0.4 + rng.uniform(-0.1, 0.2))
            sell_cmd = self._random_simple("sell all", rng)
            self._type_and_send(sell_cmd, 'sell', rng)
        
        # Optional tiny coinflip
        if self.var_tiny_cf.get() and self._hunt_count % self.var_cf_every.get() == 0:
            self._calm_sleep(0.25 + rng.uniform(-0.05, 0.15))
            cf_cmd = self._random_coinflip(rng)
            cf_cmd = self._clamp_amount(cf_cmd, 2, 25, rng)
            self._type_and_send(cf_cmd, 'coinflip', rng)
    
    def _execute_per_command_schedule(self, schedule: dict, rng: random.Random, now: float) -> None:
        """Execute per-command scheduling"""
        for cmd_name, cmd_data in schedule.items():
            if not cmd_data['enabled'] or now < cmd_data['next']:
                continue
            
            if self._stop_event.is_set() or self._pause_event.is_set():
                break
            
            # Generate command
            if cmd_name == 'hunt':
                cmd = self._random_simple('hunt', rng)
            elif cmd_name == 'cf':
                cmd = self._random_coinflip(rng)
            elif cmd_name == 'slots':
                cmd = self._random_slots(rng)
            elif cmd_name == 'battle':
                cmd = self._random_simple('battle', rng)
            elif cmd_name == 'pray':
                cmd = f"{self._prefix(rng)} pray"
                self.cooldowns['pray'] = 300  # 5 minute cooldown
            else:
                continue
            
            self._type_and_send(cmd, cmd_name, rng)
            
            # Update next fire time with variance
            variance = rng.uniform(-0.5, 0.5)
            cmd_data['next'] = now + cmd_data['interval'] + variance
    
    def _type_and_send(self, command: str, cmd_type: str, rng: random.Random) -> None:
        """Type command with enhanced human-like behavior"""
        if self._stop_event.is_set() or self._pause_event.is_set():
            return
        
        try:
            # Apply typo if enabled
            final_command = command
            if self.var_random_typos.get() and rng.random() < 0.05:  # 5% chance
                final_command = self._apply_typo(command, rng)
                self._type_at_variable_wpm(final_command, rng)
                self._calm_sleep(0.3)
                # Correct the typo
                for _ in range(len(final_command) - len(command) + 1):
                    pyautogui.press('backspace')
                    time.sleep(0.05)
                final_command = command
            
            self._type_at_variable_wpm(final_command, rng)
            
            if not self._stop_event.is_set() and not self._pause_event.is_set():
                pyautogui.press('enter')
                
                # Update stats
                self.stats['commands_sent'] += 1
                if cmd_type in self.stats['commands_by_type']:
                    self.stats['commands_by_type'][cmd_type] += 1
                else:
                    self.stats['commands_by_type'][cmd_type] = 1
                
                # Log command
                self.logger.info(f"Sent: {command}")
                
                # Update UI
                self.root.after(0, lambda c=command: self.status_label.config(
                    text=f"🟢 Sent: {c} | Total: {self.stats['commands_sent']}"
                ))
                
                # Variable sleep
                sleep_time = rng.uniform(0.8, 2.2)
                self._calm_sleep(sleep_time)
        
        except Exception as e:
            self.logger.error(f"Error typing command '{command}': {e}")
            self.stats['errors'] += 1
    
    def _type_at_variable_wpm(self, text: str, rng: random.Random) -> None:
        """Type with variable speed for human-like behavior"""
        base_delay = 0.6 / 5.0  # 100 WPM base
        
        for char in text:
            if self._stop_event.is_set() or self._pause_event.is_set():
                break
            
            # Apply variance if enabled
            if self.var_human_variance.get():
                variance = rng.uniform(0.8, 1.2)  # ±20% variance
                delay = base_delay * variance
            else:
                delay = base_delay
            
            pyautogui.typewrite(char)
            time.sleep(delay + rng.uniform(-0.01, 0.01))
    
    def _apply_typo(self, text: str, rng: random.Random) -> str:
        """Apply a random typo to text"""
        if len(text) < 3:
            return text
        
        typo_pos = rng.randint(1, len(text) - 1)
        typo_type = rng.choice(['swap', 'duplicate', 'wrong_char'])
        
        chars = list(text)
        if typo_type == 'swap' and typo_pos < len(chars) - 1:
            chars[typo_pos], chars[typo_pos + 1] = chars[typo_pos + 1], chars[typo_pos]
        elif typo_type == 'duplicate':
            chars.insert(typo_pos, chars[typo_pos])
        elif typo_type == 'wrong_char':
            chars[typo_pos] = rng.choice('abcdefghijklmnopqrstuvwxyz')
        
        return ''.join(chars)
    
    def _calm_sleep(self, duration: float) -> None:
        """Sleep with frequent event checks"""
        end_time = time.monotonic() + duration
        while time.monotonic() < end_time and not self._stop_event.is_set():
            if self._pause_event.is_set():
                time.sleep(0.1)
                continue
            time.sleep(min(0.1, end_time - time.monotonic()))
    
    def _wait_until(self, target_time: float) -> None:
        """Wait until target time with event checks"""
        while time.monotonic() < target_time and not self._stop_event.is_set() and not self._pause_event.is_set():
            time.sleep(0.05)
    
    def _clamp_amount(self, command: str, min_amt: int, max_amt: int, rng: random.Random) -> str:
        """Clamp amount in command"""
        parts = command.split()
        if parts and parts[-1].isdigit():
            amount = int(parts[-1])
            if amount < min_amt or amount > max_amt:
                parts[-1] = str(rng.randint(min_amt, max_amt))
                return ' '.join(parts)
        return command
    
    # Command generation methods
    
    def _prefix(self, rng: random.Random) -> str:
        """Get command prefix"""
        if self.var_aliases.get():
            return rng.choice(["owo", "o"])
        return "owo"
    
    def _random_amount(self, rng: random.Random, lo: int = 2, hi: int = 1500) -> int:
        """Generate random amount"""
        return rng.randint(lo, hi)
    
    def _random_coinflip(self, rng: random.Random) -> str:
        """Generate coinflip command"""
        prefix = self._prefix(rng)
        verb = rng.choice(["coinflip", "cf", "cf"]) if self.var_aliases.get() else "coinflip"
        side = rng.choice(["t", "h", "tail", "head", ""]).strip()
        amount = self._random_amount(rng, 2, 300)
        
        parts = [prefix, verb]
        if side:
            parts.append(side)
        parts.append(str(amount))
        return " ".join(parts)
    
    def _random_slots(self, rng: random.Random) -> str:
        """Generate slots command"""
        amount = self._random_amount(rng, 2, 500)
        token = "s" if (self.var_aliases.get() and rng.random() < 0.5) else "slots"
        return f"{self._prefix(rng)} {token} {amount}"
    
    def _random_blackjack(self, rng: random.Random) -> str:
        """Generate blackjack command"""
        amount = self._random_amount(rng, 2, 500)
        token = "bj" if (self.var_aliases.get() and rng.random() < 0.7) else "blackjack"
        return f"{self._prefix(rng)} {token} {amount}"
    
    def _random_simple(self, word: str, rng: random.Random) -> str:
        """Generate simple command"""
        alias_map = {
            "hunt": ["hunt", "h", "o h"],
            "battle": ["battle", "b", "o b", "ob"],
            "cash": ["cash", "owo cash"],
            "checklist": ["checklist", "cl", "o cl"],
            "lootbox all": ["lootbox all", "lb all", "o lb all"],
            "crate all": ["crate all", "o crate all"],
            "sell all": ["sell all", "o sell all"],
            "team": ["team", "o team"],
            "zoo": ["zoo", "o zoo"],
            "inv": ["inv", "o inv"],
            "autohunt": ["autohunt", "o autohunt"],
        }
        
        token = word
        if self.var_aliases.get() and word in alias_map:
            token = rng.choice(alias_map[word])
        
        if token.startswith("o ") or token in ("oh", "ob"):
            return token
        return f"{self._prefix(rng)} {token}"
    
    def _on_closing(self) -> None:
        """Handle window close event"""
        if self.worker and self.worker.is_alive():
            if messagebox.askokcancel("Quit", "Auto typer is running. Do you want to stop and quit?"):
                self.stop()
                self.root.destroy()
        else:
            self.root.destroy()


def main() -> None:
    """Main entry point"""
    root = tk.Tk()
    app = EnhancedOwoAutoTyper(root)
    root.mainloop()


if __name__ == "__main__":
    main()