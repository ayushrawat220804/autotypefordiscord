"""
Simple Owo Auto Typer
- Hardcoded 5 commands that run every 15 seconds
- Fixed 800x600 UI resolution
- Simple start/stop functionality
- No complex configuration

Commands:
1. owo hunt
2. owo coinflip 100
3. owo slots 50
4. owo battle
5. owo cash

Notes / warnings:
- Automating Discord input may violate server rules or Discord Terms of Service.
- Use responsibly; I added deliberate warnings and minimum intervals.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import pyautogui
import keyboard


class SimpleOwoAutoTyper:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Simple OwO Auto Typer")
        self.root.geometry("900x700")
        self.root.resizable(True, True)  # Flexible size

        # State
        self._stop_event = threading.Event()
        self.worker: threading.Thread | None = None

        # Hardcoded commands with random amounts
        self.commands = [
            "owo hunt",
            "owo coinflip",  # Will be filled with random amount
            "owo slots",     # Will be filled with random amount  
            "owo battle",
            "owo choose",    # Will be filled with head/tail
            "owo lottery",   # Will be filled with random amount
            "owo bet",       # Will be filled with random amount
            "owo lootbox",
            "owo crate"
        ]
        
        # Optional commands that run randomly
        self.optional_commands = [
            "owo sell all",  # Sells all pets for cash (3x more frequent)
            "owo sell all",  # Sells all pets for cash (3x more frequent)
            "owo sell all",  # Sells all pets for cash (3x more frequent)
            "owo sc all",    # Sacrifice all for essence
            "owo cash",      # Check cash
            "owo zoo",       # Zoo command
            "owo team",      # Team command
            "owo owo cash",  # Double owo cash
            "owo owo hunt",  # Double owo hunt
            "owo owo battle", # Double owo battle
            "owo owo b",     # Double owo b
            "owo owo hug",   # Double owo hug
            "owo owo pray",  # Double owo pray
            "owo curse @owo",  # Curse command
            "owo marry",     # Marry command
            "owo roll",      # Roll dice (1-6)
            "owo bell",      # Bell command
            "owo pray"       # Single pray command
        ]
        
        # Utility commands
        self.utility_commands = [
            "owo ping",      # Ping command
            "owo stats",     # Stats command
            "owo rules",     # Rules command
            "owo shards",    # Shards command
            "owo color",     # Random color command
            "owo prefix"     # Prefix command
        ]
        
        # Ultra advanced action commands
        self.action_commands = [
            "owo owo cuddle", "owo owo hug", "owo owo kiss", "owo owo lick", "owo owo nom",
            "owo owo pat", "owo owo poke", "owo owo slap", "owo owo stare", "owo owo highfive",
            "owo owo bite", "owo owo greet", "owo owo punch", "owo owo handholding", "owo owo tickle",
            "owo owo kill", "owo owo hold", "owo owo pats", "owo owo wave", "owo owo boop",
            "owo owo snuggle", "owo owo bully"
        ]
        
        # Meme generation commands
        self.meme_commands = [
            "owo spongebobchicken @owo", "owo slapcar @owo", "owo isthisa @owo", "owo drake @owo",
            "owo distracteddbf @owo", "owo communismcat @owo", "owo eject @owo", "owo emergencymeeting @owo",
            "owo headpat @owo", "owo tradeoffer @owo", "owo waddle @owo"
        ]
        
        # Track previous amounts to ensure different values
        self.previous_amounts = {"coinflip": 0, "slots": 0, "lottery": 0, "bet": 0, "give": 0}
        
        # Advanced mode for random prefixes
        self.var_advanced_mode = tk.BooleanVar(value=False)
        
        # Ultra advanced mode for all action commands
        self.var_ultra_advanced_mode = tk.BooleanVar(value=False)
        
        # Meme generation mode
        self.var_meme_mode = tk.BooleanVar(value=False)
        
        # Utility mode
        self.var_utility_mode = tk.BooleanVar(value=False)
        
        # Special timer tracking
        self.last_pray_time = 0
        self.pray_interval = 360  # 6 minutes in seconds
        
        self.last_clover_time = 0
        self.clover_interval = 600  # 10 minutes in seconds
        
        self.last_cookie_time = 0
        self.cookie_interval = 600  # 10 minutes in seconds

        # Ultra special timers (every 10 minutes)
        self.last_daily_time = 0
        self.daily_interval = 600
        self.last_vote_time = 0
        self.vote_interval = 600
        self.last_quest_time = 0
        self.quest_interval = 600
        self.last_checklist_time = 0
        self.checklist_interval = 600
        self.last_shop_time = 0
        self.shop_interval = 600
        self.last_buy_time = 0
        self.buy_interval = 600
        
        # Ranking commands (every 3 minutes)
        self.last_top_time = 0
        self.top_interval = 180  # 3 minutes in seconds
        self.last_my_time = 0
        self.my_interval = 180  # 3 minutes in seconds
        
        # Economy commands (every 10 minutes)
        self.last_cash_time = 0
        self.cash_interval = 600
        self.last_give_time = 0
        self.give_interval = 600

        self._build_ui()
        self._setup_hotkeys()
        self._refresh_preview()

    def _build_ui(self) -> None:
        # Main frame with padding
        main = ttk.Frame(self.root, padding="20")
        main.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Title
        title_label = ttk.Label(main, text="Simple OwO Auto Typer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Commands display
        commands_frame = ttk.LabelFrame(main, text="Hardcoded Commands (Every 5 seconds)", padding="10")
        commands_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))

        for i, cmd in enumerate(self.commands):
            if cmd in ["owo coinflip", "owo slots"]:
                cmd_label = ttk.Label(commands_frame, text=f"{i+1}. {cmd} [1-500]", font=("Courier", 10))
            elif cmd in ["owo lottery", "owo bet"]:
                cmd_label = ttk.Label(commands_frame, text=f"{i+1}. {cmd} [1-400]", font=("Courier", 10))
            elif cmd == "owo choose":
                cmd_label = ttk.Label(commands_frame, text=f"{i+1}. {cmd} [head/tail]", font=("Courier", 10))
            else:
                cmd_label = ttk.Label(commands_frame, text=f"{i+1}. {cmd}", font=("Courier", 10))
            cmd_label.grid(row=i, column=0, sticky=tk.W, pady=2)
            
        # Add optional commands info
        optional_label = ttk.Label(commands_frame, text="Optional (random): sell all, sc all, cash, zoo, team, owo cash, owo hunt, owo battle, owo b, owo hug, owo pray, cookie, clover, curse, marry, roll, bell", 
                                 font=("Courier", 9), foreground="blue")
        optional_label.grid(row=len(self.commands), column=0, sticky=tk.W, pady=(10, 2))

        # Advanced mode checkbox
        advanced_frame = ttk.LabelFrame(main, text="Advanced Modes", padding="10")
        advanced_frame.grid(row=1, column=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 20))
        
        ttk.Checkbutton(advanced_frame, text="Random prefixes (owo/o)", 
                       variable=self.var_advanced_mode, command=self._refresh_preview).grid(row=0, column=0, sticky=tk.W)
        
        ttk.Checkbutton(advanced_frame, text="Ultra Advanced (22 action commands - 5% chance)", 
                       variable=self.var_ultra_advanced_mode, command=self._refresh_preview).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Checkbutton(advanced_frame, text="Meme Generation (11 meme commands)", 
                       variable=self.var_meme_mode, command=self._refresh_preview).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        ttk.Checkbutton(advanced_frame, text="Utility Commands (6 utility commands)", 
                       variable=self.var_utility_mode, command=self._refresh_preview).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        advanced_info = ttk.Label(advanced_frame, text="Advanced: Mix 'owo' and 'o' prefixes\nUltra: Add 22 action commands (15% chance each)\nMeme: Add 11 meme generation commands (15% chance each)\nUtility: Add 6 utility commands (ping, stats, rules, etc.)", 
                                 font=("Arial", 8), justify=tk.LEFT)
        advanced_info.grid(row=4, column=0, sticky=tk.W, pady=(5, 0))

        # Status frame
        status_frame = ttk.LabelFrame(main, text="Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        self.status_label = ttk.Label(status_frame, text="Ready. Focus Discord before starting.", 
                                    font=("Arial", 12))
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        # Controls frame
        controls_frame = ttk.LabelFrame(main, text="Controls", padding="10")
        controls_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        # Buttons
        self.btn_start = ttk.Button(controls_frame, text="Start Auto Typer", 
                                  command=self.start, style="Accent.TButton")
        self.btn_start.grid(row=0, column=0, padx=(0, 10), pady=10)

        self.btn_stop = ttk.Button(controls_frame, text="Stop Auto Typer", 
                                 command=self.stop, state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=(0, 10), pady=10)

        # Info frame
        info_frame = ttk.LabelFrame(main, text="How it works", padding="10")
        info_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

        info_text = """• The bot will run 9 core commands every 5 seconds
• Core: hunt, coinflip (1-500), slots (1-500), battle, choose (head/tail), lottery (1-400), bet (1-400), lootbox, crate
• Optional (20% chance): sell all (3x more frequent), sc all, cash, zoo, team, owo cash, owo hunt, owo battle, owo b, owo hug, owo pray, curse, marry, roll, bell
• Ultra Advanced (10% chance): 22 action commands (cuddle, hug, kiss, lick, nom, pat, poke, slap, stare, highfive, bite, greet, punch, handholding, tickle, kill, hold, pats, wave, boop, snuggle, bully)
• Meme Generation (10% chance): 11 meme commands (spongebobchicken, slapcar, isthisa, drake, distracteddbf, communismcat, eject, emergencymeeting, headpat, tradeoffer, waddle)
• Utility Commands: ping, stats, rules, shards, color, prefix
• Ultra Special Timers: owo pray (every 6 minutes), owo clover @owo (every 10 minutes), owo cookie @owo (every 10 minutes)
• Ranking Commands (every 3 minutes): owo top, owo my
• Economy Commands (every 10 minutes): owo cash, owo give [500-20k] @aditimaheshwari4 (shop, buy exist but optional)
• Random amounts for gambling commands (1-500 for coinflip/slots, 1-400 for lottery/bet)
• Advanced mode: Random prefixes (owo/o) + aliases (cf, h, b, s, z, lb) for stealth
• Typing speed: 150 WPM for faster execution
• Make sure Discord is focused before starting
• Press Ctrl+P to start/stop quickly
• Use responsibly and follow server rules"""

        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 9))
        info_label.grid(row=0, column=0, sticky=tk.W)

        # Warning frame
        warning_frame = ttk.LabelFrame(main, text="⚠️ Warning", padding="10")
        warning_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))

        warning_text = """Automating Discord may violate server rules or Discord ToS.
Use at your own risk and follow all applicable rules."""

        warning_label = ttk.Label(warning_frame, text=warning_text, justify=tk.LEFT, 
                                font=("Arial", 9), foreground="red")
        warning_label.grid(row=0, column=0, sticky=tk.W)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)

    def _setup_hotkeys(self) -> None:
        def on_ctrl_p() -> None:
            if self.worker and self.worker.is_alive():
                self.stop()
            else:
                self.start()
        keyboard.add_hotkey('ctrl+p', on_ctrl_p)

    def _refresh_preview(self) -> None:
        """Generate live preview of strategy"""
        # This method will be called when advanced mode is toggled
        pass

    def start(self) -> None:
        """Start the auto typer with validation and ToS warning"""
        # ToS warning
        result = messagebox.askyesno(
            "Terms of Service Warning",
            "⚠️ WARNING ⚠️\n\n"
            "Automating Discord input may violate:\n"
            "• Server rules\n"
            "• Discord Terms of Service\n\n"
            "Use responsibly and at your own risk.\n\n"
            "Do you want to continue?"
        )
        if not result:
            return

        # Start worker thread
        self._stop_event.clear()
        self.worker = threading.Thread(target=self._run_loop, daemon=True)
        self.worker.start()

        # Update UI
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.status_label.config(text="Running... Press Ctrl+P to stop.")

    def stop(self) -> None:
        """Stop the auto typer safely"""
        self._stop_event.set()
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=2.0)  # Wait up to 2 seconds for clean shutdown

        # Update UI
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status_label.config(text="Stopped.")

    def _run_loop(self) -> None:
        """Main worker loop - runs all 5 commands every 15 seconds"""
        rng = random.Random()
        
        # 5-second countdown before starting
        for i in range(5, 0, -1):
            if self._stop_event.is_set():
                return
            self.root.after(0, lambda count=i: self.status_label.config(text=f"Starting in {count} seconds..."))
            self._calm_sleep(1.0)
        
        if self._stop_event.is_set():
            return
            
        self.root.after(0, lambda: self.status_label.config(text="Running commands..."))
        
        while not self._stop_event.is_set():
            # Run all core commands with small delays between them
            for i, command in enumerate(self.commands):
                if self._stop_event.is_set():
                    break
                
                # Generate random amounts for gambling commands
                final_command = self._generate_command_with_amount(command, rng)
                    
                # Type and send command
                self._type_and_send(final_command)
                
                # Small delay between commands (except for the last one)
                if i < len(self.commands) - 1:
                    self._calm_sleep(1.0)  # 1 second between commands
            
            # Randomly add optional commands (20% chance each)
            for optional_cmd in self.optional_commands:
                if self._stop_event.is_set():
                    break
                    
                if rng.random() < 0.20:  # 20% chance to run each optional command
                    final_command = self._generate_command_with_amount(optional_cmd, rng)
                    self._type_and_send(final_command)
                    self._calm_sleep(1.0)  # 1 second delay
            
            # Ultra Advanced Mode: Randomly add action commands (10% chance each)
            if self.var_ultra_advanced_mode.get():
                for action_cmd in self.action_commands:
                    if self._stop_event.is_set():
                        break
                        
                    if rng.random() < 0.10:  # 10% chance to run each action command
                        final_command = self._generate_command_with_amount(action_cmd, rng)
                        self._type_and_send(final_command)
                        self._calm_sleep(1.0)  # 1 second delay
            
            # Meme Generation Mode: Randomly add meme commands (10% chance each)
            if self.var_meme_mode.get():
                for meme_cmd in self.meme_commands:
                    if self._stop_event.is_set():
                        break
                        
                    if rng.random() < 0.10:  # 10% chance to run each meme command
                        final_command = self._generate_command_with_amount(meme_cmd, rng)
                        self._type_and_send(final_command)
                        self._calm_sleep(1.0)  # 1 second delay
            
            # Utility Commands Mode: Randomly add utility commands (10% chance each)
            if self.var_utility_mode.get():
                for utility_cmd in self.utility_commands:
                    if self._stop_event.is_set():
                        break
                        
                    if rng.random() < 0.10:  # 10% chance to run each utility command
                        final_command = self._generate_command_with_amount(utility_cmd, rng)
                        self._type_and_send(final_command)
                        self._calm_sleep(1.0)  # 1 second delay
            
            # Special Timers: Check if enough time has passed for special commands
            current_time = time.monotonic()
            
            # Pray Timer: Every 6 minutes
            if current_time - self.last_pray_time >= self.pray_interval:
                if not self._stop_event.is_set():
                    pray_command = self._generate_command_with_amount("owo pray", rng)
                    self._type_and_send(pray_command)
                    self.last_pray_time = current_time
                    self._calm_sleep(1.0)  # 1 second delay
            
            # Clover Timer: Every 10 minutes
            if current_time - self.last_clover_time >= self.clover_interval:
                if not self._stop_event.is_set():
                    clover_command = self._generate_command_with_amount("owo clover @owo", rng)
                    self._type_and_send(clover_command)
                    self.last_clover_time = current_time
                    self._calm_sleep(1.0)  # 1 second delay
            
            # Cookie Timer: Every 10 minutes
            if current_time - self.last_cookie_time >= self.cookie_interval:
                if not self._stop_event.is_set():
                    cookie_command = self._generate_command_with_amount("owo cookie @owo", rng)
                    self._type_and_send(cookie_command)
                    self.last_cookie_time = current_time
                    self._calm_sleep(1.0)  # 1 second delay

            # Ultra Special timers (every 10 minutes)
            if current_time - self.last_daily_time >= self.daily_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo daily", rng))
                    self.last_daily_time = current_time
                    self._calm_sleep(1.0)

            if current_time - self.last_vote_time >= self.vote_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo vote", rng))
                    self.last_vote_time = current_time
                    self._calm_sleep(1.0)

            if current_time - self.last_quest_time >= self.quest_interval:
                if not self._stop_event.is_set():
                    # Randomize between quest aliases
                    self._type_and_send(self._generate_command_with_amount("owo quest", rng))
                    self.last_quest_time = current_time
                    self._calm_sleep(1.0)

            if current_time - self.last_checklist_time >= self.checklist_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo checklist", rng))
                    self.last_checklist_time = current_time
                    self._calm_sleep(1.0)

            if current_time - self.last_shop_time >= self.shop_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo shop", rng))
                    self.last_shop_time = current_time
                    self._calm_sleep(1.0)

            if current_time - self.last_buy_time >= self.buy_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo buy", rng))
                    self.last_buy_time = current_time
                    self._calm_sleep(1.0)
            
            # Ranking commands (every 3 minutes)
            if current_time - self.last_top_time >= self.top_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo top", rng))
                    self.last_top_time = current_time
                    self._calm_sleep(1.0)
            
            if current_time - self.last_my_time >= self.my_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo my", rng))
                    self.last_my_time = current_time
                    self._calm_sleep(1.0)
            
            # Economy commands (every 10 minutes)
            if current_time - self.last_cash_time >= self.cash_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo cash", rng))
                    self.last_cash_time = current_time
                    self._calm_sleep(1.0)
            
            if current_time - self.last_give_time >= self.give_interval:
                if not self._stop_event.is_set():
                    self._type_and_send(self._generate_command_with_amount("owo give", rng))
                    self.last_give_time = current_time
                    self._calm_sleep(1.0)
            
            # Wait 5 seconds before next cycle (faster cycling)
            if not self._stop_event.is_set():
                self._calm_sleep(5.0)

        # Clean shutdown
        self.root.after(0, self.stop)

    def _type_and_send(self, command: str) -> None:
        """Type command with human-like timing and send"""
        if self._stop_event.is_set():
            return
            
        # Type at human-like speed
        self._type_at_human_speed(command)
        
        if not self._stop_event.is_set():
            pyautogui.press('enter')
            self._calm_sleep(random.uniform(1.0, 2.0))
            
        # Update status on main thread
        self.root.after(0, lambda c=command: self.status_label.config(text=f"Sent: {c}"))

    def _type_at_human_speed(self, text: str) -> None:
        """Type text at 150 WPM speed with character-by-character delays"""
        delay_per_char = 0.04  # ~150 WPM typing speed (0.4s per word, ~5 chars per word)
        
        for char in text:
            if self._stop_event.is_set():
                break
            pyautogui.typewrite(char)
            time.sleep(delay_per_char + random.uniform(-0.005, 0.005))

    def _calm_sleep(self, duration: float) -> None:
        """Sleep with frequent stop event checks"""
        end_time = time.monotonic() + duration
        while time.monotonic() < end_time and not self._stop_event.is_set():
            time.sleep(min(0.1, end_time - time.monotonic()))

    def _generate_command_with_amount(self, command: str, rng: random.Random) -> str:
        """Generate command with random amount, prefixes, and aliases for maximum stealth"""
        # Choose random prefix if advanced mode is enabled
        if self.var_advanced_mode.get():
            prefix = rng.choice(["owo", "o"])
        else:
            prefix = "owo"
        
        if command == "owo coinflip":
            # Generate different amount from previous
            amount = rng.randint(1, 500)
            while amount == self.previous_amounts["coinflip"]:
                amount = rng.randint(1, 500)
            self.previous_amounts["coinflip"] = amount
            
            # Random coinflip variations
            if self.var_advanced_mode.get():
                # Choose random coinflip command variation
                cf_variations = [
                    f"{prefix} coinflip {amount}",
                    f"{prefix} cf {amount}",
                    f"{prefix} coinflip h {amount}",
                    f"{prefix} coinflip t {amount}",
                    f"{prefix} cf h {amount}",
                    f"{prefix} cf t {amount}"
                ]
                return rng.choice(cf_variations)
            else:
                return f"{prefix} coinflip {amount}"
                
        elif command == "owo slots":
            # Generate different amount from previous
            amount = rng.randint(1, 500)
            while amount == self.previous_amounts["slots"]:
                amount = rng.randint(1, 500)
            self.previous_amounts["slots"] = amount
            
            # Random slots variations
            if self.var_advanced_mode.get():
                slots_variations = [
                    f"{prefix} slots {amount}",
                    f"{prefix} s {amount}"
                ]
                return rng.choice(slots_variations)
            else:
                return f"{prefix} slots {amount}"
                
        elif command == "owo hunt":
            if self.var_advanced_mode.get():
                hunt_variations = [
                    f"{prefix} hunt",
                    f"{prefix} h"
                ]
                return rng.choice(hunt_variations)
            else:
                return f"{prefix} hunt"
                
        elif command == "owo battle":
            if self.var_advanced_mode.get():
                battle_variations = [
                    f"{prefix} battle",
                    f"{prefix} b"
                ]
                return rng.choice(battle_variations)
            else:
                return f"{prefix} battle"
                
        elif command == "owo choose":
            if self.var_advanced_mode.get():
                choose_variations = [
                    f"{prefix} choose head, tail",
                    f"{prefix} choose h, t",
                    f"{prefix} choose head, t",
                    f"{prefix} choose h, tail"
                ]
                return rng.choice(choose_variations)
            else:
                return f"{prefix} choose {rng.choice(['head, tail', 'h, t', 'head, t', 'h, tail'])}"
                
        elif command == "owo lottery":
            # Generate different amount from previous (1-400)
            amount = rng.randint(1, 400)
            while amount == self.previous_amounts["lottery"]:
                amount = rng.randint(1, 400)
            self.previous_amounts["lottery"] = amount
            return f"{prefix} lottery {amount}"
            
        elif command == "owo bet":
            # Generate different amount from previous (1-400)
            amount = rng.randint(1, 400)
            while amount == self.previous_amounts["bet"]:
                amount = rng.randint(1, 400)
            self.previous_amounts["bet"] = amount
            return f"{prefix} bet {amount}"
            
        elif command == "owo sell all":
            return f"{prefix} sell all"
            
        elif command == "owo sc all":
            return f"{prefix} sc all"
            
        elif command == "owo owo cash":
            return f"{prefix} owo cash"
            
        elif command == "owo owo hunt":
            return f"{prefix} owo hunt"
            
        elif command == "owo owo battle":
            return f"{prefix} owo battle"
            
        elif command == "owo owo b":
            return f"{prefix} owo b"
            
        elif command == "owo owo hug":
            return f"{prefix} owo hug"
            
        elif command == "owo owo pray":
            return f"{prefix} owo pray"
            
        # New optional commands
        elif command == "owo zoo":
            if self.var_advanced_mode.get():
                zoo_variations = [
                    f"{prefix} zoo",
                    f"{prefix} z"
                ]
                return rng.choice(zoo_variations)
            else:
                return f"{prefix} zoo"
                
        elif command == "owo team":
            return f"{prefix} team"
            
        elif command == "owo cookie @owo":
            return f"{prefix} cookie @owo"
            
        elif command == "owo clover @owo":
            return f"{prefix} clover @owo"
            
        elif command == "owo curse @owo":
            return f"{prefix} curse @owo"
            
        elif command == "owo marry":
            return f"{prefix} marry"
            
        elif command == "owo roll":
            return f"{prefix} roll"
            
        elif command == "owo bell":
            return f"{prefix} bell"

        # Ultra special commands (10-minute timers) and aliases
        elif command == "owo daily":
            return f"{prefix} daily"
        elif command == "owo vote":
            return f"{prefix} vote"
        elif command == "owo quest":
            # Support alias 'q'
            if self.var_advanced_mode.get():
                return f"{prefix} {rng.choice(['quest', 'q'])}"
            return f"{prefix} quest"
        elif command == "owo checklist":
            # Support alias 'cl'
            if self.var_advanced_mode.get():
                return f"{prefix} {rng.choice(['checklist', 'cl'])}"
            return f"{prefix} checklist"
        elif command == "owo shop":
            return f"{prefix} shop"
        elif command == "owo buy":
            return f"{prefix} buy"
            
        # Ranking commands (every 3 minutes)
        elif command == "owo top":
            return f"{prefix} top"
        elif command == "owo my":
            return f"{prefix} my"
            
        # Economy commands (every 10 minutes)
        elif command == "owo cash":
            return f"{prefix} cash"
        elif command == "owo give":
            # Generate random amount between 500-20000, different from previous
            amount = rng.randint(500, 20000)
            while amount == self.previous_amounts["give"]:
                amount = rng.randint(500, 20000)
            self.previous_amounts["give"] = amount
            return f"{prefix} give {amount} @aditimaheshwari4"
            
        # Utility commands
        elif command == "owo ping":
            return f"{prefix} ping"
            
        elif command == "owo stats":
            return f"{prefix} stats"
            
        elif command == "owo rules":
            return f"{prefix} rules"
            
        elif command == "owo shards":
            return f"{prefix} shards"
            
        elif command == "owo color":
            return f"{prefix} color"
            
        elif command == "owo prefix":
            return f"{prefix} prefix"
            
        # Action commands (Ultra Advanced Mode) - Only use "owo owo" format
        elif command in ["owo owo cuddle", "owo owo hug", "owo owo kiss", "owo owo lick", "owo owo nom",
                        "owo owo pat", "owo owo poke", "owo owo slap", "owo owo stare", "owo owo highfive",
                        "owo owo bite", "owo owo greet", "owo owo punch", "owo owo handholding", "owo owo tickle",
                        "owo owo kill", "owo owo hold", "owo owo pats", "owo owo wave", "owo owo boop",
                        "owo owo snuggle", "owo owo bully"]:
            return command  # Keep as "owo owo [action]" - no prefix changes
            
        # Meme generation commands
        elif command in ["owo spongebobchicken @owo", "owo slapcar @owo", "owo isthisa @owo", "owo drake @owo",
                        "owo distracteddbf @owo", "owo communismcat @owo", "owo eject @owo", "owo emergencymeeting @owo",
                        "owo headpat @owo", "owo tradeoffer @owo", "owo waddle @owo"]:
            return command  # Keep as "owo [meme] @owo" - no prefix changes
                
        elif command == "owo zoo":
            if self.var_advanced_mode.get():
                zoo_variations = [
                    f"{prefix} zoo",
                    f"{prefix} z"
                ]
                return rng.choice(zoo_variations)
            else:
                return f"{prefix} zoo"
                
        elif command == "owo team":
            return f"{prefix} team"
            
        elif command == "owo lootbox":
            if self.var_advanced_mode.get():
                lootbox_variations = [
                    f"{prefix} lootbox",
                    f"{prefix} lb",
                    f"{prefix} lootbox all",
                    f"{prefix} lb all"
                ]
                return rng.choice(lootbox_variations)
            else:
                return f"{prefix} lootbox"
                
        elif command == "owo crate":
            if self.var_advanced_mode.get():
                crate_variations = [
                    f"{prefix} crate",
                    f"{prefix} crate all"
                ]
                return rng.choice(crate_variations)
            else:
                return f"{prefix} crate"
                
        elif command == "owo cash":
            return f"{prefix} cash"
        else:
            return command


def main() -> None:
    root = tk.Tk()
    app = SimpleOwoAutoTyper(root)
    root.mainloop()


if __name__ == "__main__":
    main()
