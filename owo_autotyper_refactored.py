"""
Refactored Owo Auto Typer
- Cleaner scheduling (per-command intervals, minute-plan, cash-farm)
- Run-by-duration or run-by-iterations support
- Stop event for safe shutdown
- Fewer busy-waits and calmer sleeping
- Better UI: validation, run controls, preview

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


MIN_INTERVAL = 3  # absolute minimum between typed characters for safety


class OwoAutoTyper:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OwO Auto Typer — Refactor")
        self.root.geometry("760x520")

        # State
        self._stop_event = threading.Event()
        self.worker: threading.Thread | None = None

        # UI variables
        self.interval_seconds = tk.IntVar(value=15)
        self.run_mode = tk.StringVar(value="duration")  # 'duration' or 'iterations'
        self.run_duration_seconds = tk.IntVar(value=3600)  # 1 hour
        self.run_iterations = tk.IntVar(value=100)

        # categories
        self.var_economy = tk.BooleanVar(value=True)
        self.var_animals = tk.BooleanVar(value=True)
        self.var_gambling = tk.BooleanVar(value=False)
        self.var_aliases = tk.BooleanVar(value=True)

        # minute plan / cash farm
        self.var_minute_plan = tk.BooleanVar(value=True)
        self.var_cashfarm = tk.BooleanVar(value=False)
        self.var_hunts_per_sell = tk.IntVar(value=10)
        self.var_cf_every = tk.IntVar(value=7)
        self.var_tiny_cf = tk.BooleanVar(value=False)

        # Per command enable and intervals
        self.en_hunt = tk.BooleanVar(value=True); self.iv_hunt = tk.IntVar(value=15)
        self.en_cf   = tk.BooleanVar(value=True); self.iv_cf   = tk.IntVar(value=10)
        self.en_slots= tk.BooleanVar(value=True); self.iv_slots= tk.IntVar(value=10)
        self.en_battle = tk.BooleanVar(value=True); self.iv_battle = tk.IntVar(value=15)
        self.en_pray = tk.BooleanVar(value=True); self.iv_pray = tk.IntVar(value=300)

        self._build_ui()
        self._setup_hotkeys()

    # ---------------- UI ----------------

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding="10")
        main.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Top row: Run mode and duration controls
        run_frame = ttk.LabelFrame(main, text="Run Mode", padding="6")
        run_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Run mode selection
        ttk.Radiobutton(run_frame, text="Run for duration", variable=self.run_mode, 
                       value="duration", command=self._refresh_preview).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(run_frame, text="Run for iterations", variable=self.run_mode, 
                       value="iterations", command=self._refresh_preview).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))

        # Duration/iterations controls
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

        # Hunt
        ttk.Checkbutton(sched, text="hunt", variable=self.en_hunt, 
                       command=self._refresh_preview).grid(row=0, column=0, sticky=tk.W)
        ttk.Spinbox(sched, from_=MIN_INTERVAL, to=600, textvariable=self.iv_hunt, 
                   width=6, command=self._refresh_preview).grid(row=0, column=1, sticky=tk.W)

        # Coinflip
        ttk.Checkbutton(sched, text="coinflip", variable=self.en_cf, 
                       command=self._refresh_preview).grid(row=1, column=0, sticky=tk.W)
        ttk.Spinbox(sched, from_=MIN_INTERVAL, to=600, textvariable=self.iv_cf, 
                   width=6, command=self._refresh_preview).grid(row=1, column=1, sticky=tk.W)

        # Slots
        ttk.Checkbutton(sched, text="slots", variable=self.en_slots, 
                       command=self._refresh_preview).grid(row=2, column=0, sticky=tk.W)
        ttk.Spinbox(sched, from_=MIN_INTERVAL, to=600, textvariable=self.iv_slots, 
                   width=6, command=self._refresh_preview).grid(row=2, column=1, sticky=tk.W)

        # Pray
        ttk.Checkbutton(sched, text="pray", variable=self.en_pray, 
                       command=self._refresh_preview).grid(row=3, column=0, sticky=tk.W)
        ttk.Spinbox(sched, from_=30, to=3600, textvariable=self.iv_pray, 
                   width=6, command=self._refresh_preview).grid(row=3, column=1, sticky=tk.W)

        # Battle
        ttk.Checkbutton(sched, text="battle", variable=self.en_battle, 
                       command=self._refresh_preview).grid(row=4, column=0, sticky=tk.W)
        ttk.Spinbox(sched, from_=MIN_INTERVAL, to=600, textvariable=self.iv_battle, 
                   width=6, command=self._refresh_preview).grid(row=4, column=1, sticky=tk.W)

        # Controls
        controls = ttk.LabelFrame(main, text="Controls", padding="6")
        controls.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.btn_start = ttk.Button(controls, text="Start", command=self.start)
        self.btn_start.grid(row=0, column=0, padx=(0, 10))

        self.btn_stop = ttk.Button(controls, text="Stop", command=self.stop, state="disabled")
        self.btn_stop.grid(row=0, column=1)

        self.status_label = ttk.Label(controls, text="Ready. Focus Discord before starting.")
        self.status_label.grid(row=0, column=2, padx=(16, 0))

        # Preview
        preview = ttk.LabelFrame(main, text="Preview", padding="6")
        preview.grid(row=2, column=2, rowspan=2, sticky=(tk.N, tk.S, tk.W, tk.E), 
                    padx=(10, 0), pady=(0, 10))
        self.preview_box = tk.Text(preview, width=40, height=12, wrap=tk.WORD)
        self.preview_box.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))
        
        # Scrollbar for preview
        scrollbar = ttk.Scrollbar(preview, orient="vertical", command=self.preview_box.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.preview_box.configure(yscrollcommand=scrollbar.set)

        # Layout weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=1)
        preview.columnconfigure(0, weight=1)
        preview.rowconfigure(0, weight=1)

        self._refresh_preview()

    def _setup_hotkeys(self) -> None:
        def on_ctrl_p() -> None:
            if self.worker and self.worker.is_alive():
                self.stop()
            else:
                self.start()
        keyboard.add_hotkey('ctrl+p', on_ctrl_p)

    def _refresh_preview(self) -> None:
        """Generate live preview of strategy"""
        self.preview_box.delete('1.0', tk.END)
        
        if self.var_minute_plan.get():
            self.preview_box.insert(tk.END, "MINUTE PLAN MODE\n")
            self.preview_box.insert(tk.END, "=" * 20 + "\n\n")
            self.preview_box.insert(tk.END, "Commands per minute:\n")
            self.preview_box.insert(tk.END, "• 4 hunts\n")
            self.preview_box.insert(tk.END, "• 5 coinflips\n")
            self.preview_box.insert(tk.END, "• 3 slots\n")
            self.preview_box.insert(tk.END, "• 2 blackjack\n")
            self.preview_box.insert(tk.END, "• 2 random noise commands\n\n")
            self.preview_box.insert(tk.END, "Evenly spaced with ±0.4s jitter\n")
            
        elif self.var_cashfarm.get():
            self.preview_box.insert(tk.END, "CASH FARM MODE\n")
            self.preview_box.insert(tk.END, "=" * 20 + "\n\n")
            hunts_per_sell = self.var_hunts_per_sell.get()
            self.preview_box.insert(tk.END, f"• Hunt every {self.interval_seconds.get()}s\n")
            self.preview_box.insert(tk.END, f"• Sell all every {hunts_per_sell} hunts\n")
            if self.var_tiny_cf.get():
                cf_every = self.var_cf_every.get()
                self.preview_box.insert(tk.END, f"• Tiny coinflip every {cf_every} hunts\n")
            self.preview_box.insert(tk.END, "\nFocus: Hunt → Sell → Repeat\n")
            
        else:
            self.preview_box.insert(tk.END, "PER-COMMAND SCHEDULING\n")
            self.preview_box.insert(tk.END, "=" * 25 + "\n\n")
            if self.en_hunt.get():
                self.preview_box.insert(tk.END, f"• Hunt every {self.iv_hunt.get()}s\n")
            if self.en_cf.get():
                self.preview_box.insert(tk.END, f"• Coinflip every {self.iv_cf.get()}s\n")
            if self.en_slots.get():
                self.preview_box.insert(tk.END, f"• Slots every {self.iv_slots.get()}s\n")
            if self.en_battle.get():
                self.preview_box.insert(tk.END, f"• Battle every {self.iv_battle.get()}s\n")
            if self.en_pray.get():
                self.preview_box.insert(tk.END, f"• Pray every {self.iv_pray.get()}s\n")
            self.preview_box.insert(tk.END, "\nIndependent scheduling\n")

        # Run mode info
        if self.run_mode.get() == "duration":
            duration = self.run_duration_seconds.get()
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            self.preview_box.insert(tk.END, f"\nRun for: {hours}h {minutes}m\n")
        else:
            self.preview_box.insert(tk.END, f"\nRun for: {self.run_iterations.get()} iterations\n")

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
            "Use responsibly and at your own risk.\n\n"
            "Do you want to continue?"
        )
        if not result:
            return

        # Validate intervals
        if self.interval_seconds.get() < MIN_INTERVAL:
            messagebox.showerror("Invalid interval", f"Interval must be at least {MIN_INTERVAL} seconds for safety.")
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
        """Main worker loop with improved scheduling"""
        start_time = time.monotonic()
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

        # Main loop
        while not self._stop_event.is_set():
            now = time.monotonic()
            
            # Check run termination conditions
            if self.run_mode.get() == "duration":
                if now - start_time >= self.run_duration_seconds.get():
                    break
            else:  # iterations mode
                if iterations >= self.run_iterations.get():
                    break

            # Execute scheduled commands
            if self.var_minute_plan.get():
                self._execute_minute_plan(rng)
            elif self.var_cashfarm.get():
                self._execute_cash_farm(rng)
            else:
                self._execute_per_command_schedule(command_schedule, rng, now)

            iterations += 1

            # Calm sleep - check stop event frequently
            self._calm_sleep(1.0)

        # Clean shutdown
        self.root.after(0, self.stop)

    def _execute_minute_plan(self, rng: random.Random) -> None:
        """Execute minute plan: 4 hunts, 5 cf, 3 slots, 2 bj per minute"""
        if self._stop_event.is_set():
            return

        # Build command list for this minute
        commands = []
        
        # 4 hunts
        for _ in range(4):
            commands.append(self._random_simple("hunt", rng))
        
        # 5 coinflips (clamped amounts)
        for _ in range(5):
            cf_cmd = self._random_coinflip(rng)
            commands.append(self._clamp_amount(cf_cmd, 200, 500, rng))
        
        # 3 slots (clamped amounts)
        for _ in range(3):
            slots_cmd = self._random_slots(rng)
            commands.append(self._clamp_amount(slots_cmd, 200, 500, rng))
        
        # 2 blackjack (clamped amounts)
        for _ in range(2):
            bj_cmd = self._random_blackjack(rng)
            commands.append(self._clamp_amount(bj_cmd, 200, 500, rng))
        
        # 2 noise commands
        noise_commands = [
            f"{self._prefix(rng)} cash",
            self._random_simple("battle", rng),
            self._random_simple("hunt", rng)
        ]
        commands.extend(rng.sample(noise_commands, 2))
        
        # Shuffle and execute with even spacing
        rng.shuffle(commands)
        gap = 60.0 / max(1, len(commands))
        
        for i, cmd in enumerate(commands):
            if self._stop_event.is_set():
                break
                
            target_time = time.monotonic() + i * gap + rng.uniform(-0.4, 0.4)
            self._wait_until(target_time)
            
            if not self._stop_event.is_set():
                self._type_and_send(cmd)

    def _execute_cash_farm(self, rng: random.Random) -> None:
        """Execute cash farm: hunt -> sell all -> repeat"""
        if self._stop_event.is_set():
            return

        # Hunt
        hunt_cmd = self._random_simple("hunt", rng)
        self._type_and_send(hunt_cmd)
        
        # Check if we should sell
        hunts_per_sell = self.var_hunts_per_sell.get()
        if hasattr(self, '_hunt_count'):
            self._hunt_count += 1
        else:
            self._hunt_count = 1
            
        if self._hunt_count % hunts_per_sell == 0:
            self._calm_sleep(0.4)
            sell_cmd = self._random_simple("sell all", rng)
            self._type_and_send(sell_cmd)
        
        # Optional tiny coinflip
        if self.var_tiny_cf.get() and self._hunt_count % self.var_cf_every.get() == 0:
            self._calm_sleep(0.25)
            cf_cmd = self._random_coinflip(rng)
            # Force small amounts
            cf_cmd = self._clamp_amount(cf_cmd, 2, 25, rng)
            self._type_and_send(cf_cmd)

    def _execute_per_command_schedule(self, schedule: dict, rng: random.Random, now: float) -> None:
        """Execute per-command scheduling"""
        for cmd_name, cmd_data in schedule.items():
            if not cmd_data['enabled'] or now < cmd_data['next']:
                continue
                
            if self._stop_event.is_set():
                break
                
            # Generate and send command
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
            else:
                continue
                
            self._type_and_send(cmd)
            cmd_data['next'] = now + cmd_data['interval'] + rng.uniform(-0.5, 0.5)

    def _type_and_send(self, command: str) -> None:
        """Type command with human-like timing and send"""
        if self._stop_event.is_set():
            return
            
        self._type_at_100_wpm(command)
        if not self._stop_event.is_set():
            pyautogui.press('enter')
            self._calm_sleep(rng.uniform(1.0, 2.0))
            
        # Update status on main thread
        self.root.after(0, lambda c=command: self.status_label.config(text=f"Sent: {c}"))

    def _type_at_100_wpm(self, text: str) -> None:
        """Type text at ~100 WPM with character-by-character delays"""
        delay_per_char = 0.6 / 5.0  # 100 WPM = 0.6s per word, ~5 chars per word
        
        for char in text:
            if self._stop_event.is_set():
                break
            pyautogui.typewrite(char)
            time.sleep(delay_per_char + random.uniform(-0.02, 0.02))

    def _calm_sleep(self, duration: float) -> None:
        """Sleep with frequent stop event checks"""
        end_time = time.monotonic() + duration
        while time.monotonic() < end_time and not self._stop_event.is_set():
            time.sleep(min(0.1, end_time - time.monotonic()))

    def _wait_until(self, target_time: float) -> None:
        """Wait until target time with stop event checks"""
        while time.monotonic() < target_time and not self._stop_event.is_set():
            time.sleep(0.05)

    def _clamp_amount(self, command: str, min_amt: int, max_amt: int, rng: random.Random) -> str:
        """Clamp the amount in a command to specified range"""
        parts = command.split()
        if parts and parts[-1].isdigit():
            amount = int(parts[-1])
            if amount < min_amt or amount > max_amt:
                parts[-1] = str(rng.randint(min_amt, max_amt))
                return ' '.join(parts)
        return command

    # ---------------- Command generation ----------------

    def _prefix(self, rng: random.Random | None = None) -> str:
        """Get command prefix with alias support"""
        if self.var_aliases.get():
            return (rng or random).choice(["owo", "o"])
        return "owo"

    def _random_amount(self, rng: random.Random | None = None, lo: int = 2, hi: int = 1500) -> int:
        """Generate random amount within range"""
        return (rng or random).randint(lo, hi)

    def _random_coinflip(self, rng: random.Random | None = None) -> str:
        """Generate random coinflip command"""
        r = rng or random
        prefix = self._prefix(r)
        verb = r.choice(["coinflip", "cf", "cf"]) if self.var_aliases.get() else "coinflip"
        side = r.choice(["t", "h", "tail", "head", ""]).strip()
        amount = self._random_amount(r, 2, 300)
        
        parts = [prefix, verb]
        if side:
            parts.append(side)
        parts.append(str(amount))
        return " ".join(parts)

    def _random_slots(self, rng: random.Random | None = None) -> str:
        """Generate random slots command"""
        r = rng or random
        amount = self._random_amount(r, 2, 500)
        token = "s" if (self.var_aliases.get() and r.random() < 0.5) else "slots"
        return f"{self._prefix(r)} {token} {amount}"

    def _random_blackjack(self, rng: random.Random | None = None) -> str:
        """Generate random blackjack command"""
        r = rng or random
        amount = self._random_amount(r, 2, 500)
        token = "bj" if (self.var_aliases.get() and r.random() < 0.7) else "blackjack"
        return f"{self._prefix(r)} {token} {amount}"

    def _random_simple(self, word: str, rng: random.Random | None = None) -> str:
        """Generate simple command with alias support"""
        r = rng or random
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
            token = r.choice(alias_map[word])
            
        if token.startswith("o ") or token in ("oh", "ob"):
            return token
        return f"{self._prefix(r)} {token}"


def main() -> None:
    root = tk.Tk()
    app = OwoAutoTyper(root)
    root.mainloop()


if __name__ == "__main__":
    main()
