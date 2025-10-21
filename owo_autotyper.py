import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import random
import pyautogui
import keyboard


class OwoAutoTyper:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("OwO Auto Typer")
        self.root.geometry("560x400")

        # State
        self.is_running = False
        self.interval_seconds = tk.StringVar(value="15")

        # Base command names (expanded via generators and aliases)
        self.commands_economy = [
            "daily", "vote", "quest", "checklist", "shop", "buy", "cash", "top", "my",
            "inv", "team", "zoo", "autohunt", "sell all", "lootbox all", "crate all",
        ]

        self.commands_animals = [
            "hunt", "battle", "zoo", "inv", "sell all", "autohunt",
        ]

        self.commands_gambling = [
            "coinflip", "slots", "blackjack", "lottery", "bet",
        ]

        # UI
        self._build_ui()
        self._setup_hotkeys()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding="10")
        main.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        # Interval
        interval_frame = ttk.LabelFrame(main, text="Tick", padding="6")
        interval_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        ttk.Label(interval_frame, text="Base interval (s):").grid(row=0, column=0, sticky=tk.W)
        interval_entry = ttk.Spinbox(interval_frame, from_=5, to=120, textvariable=self.interval_seconds, width=6)
        interval_entry.grid(row=0, column=1, padx=(8, 0))

        # Minute Plan Mode
        plan = ttk.LabelFrame(main, text="Minute Plan", padding="6")
        plan.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.var_minute_plan = tk.BooleanVar(value=True)
        ttk.Checkbutton(plan, text="Enable: 4 hunt, 5 cf, 3 slots, 2 bj per minute", variable=self.var_minute_plan, command=self._refresh_preview).grid(row=0, column=0, sticky=tk.W)

        # Cash Farm Mode
        farm = ttk.LabelFrame(main, text="Cash Farm", padding="6")
        farm.grid(row=0, column=2, sticky=(tk.N, tk.S, tk.W, tk.E))
        self.var_cashfarm = tk.BooleanVar(value=True)
        ttk.Checkbutton(farm, text="Enable (hunt+sell)", variable=self.var_cashfarm, command=self._refresh_preview).grid(row=0, column=0, columnspan=2, sticky=tk.W)
        ttk.Label(farm, text="Hunts per sell:").grid(row=1, column=0, sticky=tk.W, pady=(6,0))
        self.var_hunts_per_sell = tk.StringVar(value="10")
        ttk.Spinbox(farm, from_=2, to=50, textvariable=self.var_hunts_per_sell, width=6).grid(row=1, column=1, sticky=tk.W, pady=(6,0))
        self.var_tiny_cf = tk.BooleanVar(value=False)
        ttk.Checkbutton(farm, text="Tiny CF sometimes", variable=self.var_tiny_cf, command=self._refresh_preview).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(6,0))
        ttk.Label(farm, text="CF every N hunts:").grid(row=3, column=0, sticky=tk.W)
        self.var_cf_every = tk.StringVar(value="7")
        ttk.Spinbox(farm, from_=3, to=50, textvariable=self.var_cf_every, width=6).grid(row=3, column=1, sticky=tk.W)

        # Categories
        cats = ttk.LabelFrame(main, text="Categories", padding="6")
        cats.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.W, tk.E), pady=(10, 0))

        self.var_economy = tk.BooleanVar(value=True)
        self.var_animals = tk.BooleanVar(value=True)
        self.var_gambling = tk.BooleanVar(value=False)

        ttk.Checkbutton(cats, text="Economy", variable=self.var_economy, command=self._refresh_preview).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(cats, text="Animals / Hunt", variable=self.var_animals, command=self._refresh_preview).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(cats, text="Gambling", variable=self.var_gambling, command=self._refresh_preview).grid(row=2, column=0, sticky=tk.W)

        # Alias toggle
        self.var_aliases = tk.BooleanVar(value=True)
        ttk.Checkbutton(cats, text="Use aliases (o/cf/bj/oh/ob)", variable=self.var_aliases, command=self._refresh_preview).grid(row=3, column=0, sticky=tk.W, pady=(6,0))

        # Per-command scheduling
        sched = ttk.LabelFrame(main, text="Per-Command (s)", padding="6")
        sched.grid(row=1, column=1, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(10, 0))

        # Hunt
        self.en_hunt = tk.BooleanVar(value=True)
        ttk.Checkbutton(sched, text="hunt", variable=self.en_hunt).grid(row=0, column=0, sticky=tk.W)
        self.iv_hunt = tk.StringVar(value="15")
        ttk.Spinbox(sched, from_=5, to=600, textvariable=self.iv_hunt, width=6).grid(row=0, column=1, sticky=tk.W)

        # Coinflip
        self.en_cf = tk.BooleanVar(value=True)
        ttk.Checkbutton(sched, text="coinflip", variable=self.en_cf).grid(row=1, column=0, sticky=tk.W)
        self.iv_cf = tk.StringVar(value="10")
        ttk.Spinbox(sched, from_=5, to=600, textvariable=self.iv_cf, width=6).grid(row=1, column=1, sticky=tk.W)

        # Slots
        self.en_slots = tk.BooleanVar(value=True)
        ttk.Checkbutton(sched, text="slots", variable=self.en_slots).grid(row=2, column=0, sticky=tk.W)
        self.iv_slots = tk.StringVar(value="10")
        ttk.Spinbox(sched, from_=5, to=600, textvariable=self.iv_slots, width=6).grid(row=2, column=1, sticky=tk.W)

        # Pray
        self.en_pray = tk.BooleanVar(value=True)
        ttk.Checkbutton(sched, text="pray", variable=self.en_pray).grid(row=3, column=0, sticky=tk.W)
        self.iv_pray = tk.StringVar(value="300")
        ttk.Spinbox(sched, from_=30, to=3600, textvariable=self.iv_pray, width=6).grid(row=3, column=1, sticky=tk.W)

        # Battle
        self.en_battle = tk.BooleanVar(value=True)
        ttk.Checkbutton(sched, text="battle", variable=self.en_battle).grid(row=4, column=0, sticky=tk.W)
        self.iv_battle = tk.StringVar(value="15")
        ttk.Spinbox(sched, from_=5, to=600, textvariable=self.iv_battle, width=6).grid(row=4, column=1, sticky=tk.W)

        # Controls
        controls = ttk.LabelFrame(main, text="Controls", padding="6")
        controls.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.btn_start = ttk.Button(controls, text="Start", command=self.toggle)
        self.btn_start.grid(row=0, column=0, padx=(0, 10))

        self.btn_stop = ttk.Button(controls, text="Stop", command=self.stop, state="disabled")
        self.btn_stop.grid(row=0, column=1)

        self.status_label = ttk.Label(controls, text="Ready. Focus Discord before starting.")
        self.status_label.grid(row=0, column=2, padx=(16, 0))

        # Example list
        preview = ttk.LabelFrame(main, text="Preview", padding="6")
        preview.grid(row=2, column=1, sticky=(tk.N, tk.S, tk.W, tk.E), padx=(10, 0))
        self.preview_box = tk.Text(preview, width=36, height=8)
        self.preview_box.grid(row=0, column=0)
        self._refresh_preview()

        # Layout weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

    def _setup_hotkeys(self) -> None:
        def on_ctrl_p() -> None:
            if self.is_running:
                self.stop()
        keyboard.add_hotkey('ctrl+p', on_ctrl_p)

    def _collect_selected_commands(self) -> list[str]:
        selected: list[str] = []
        if self.var_economy.get():
            selected.extend(self.commands_economy)
        if self.var_animals.get():
            selected.extend(self.commands_animals)
        if self.var_gambling.get():
            selected.extend(self.commands_gambling)
        # Deduplicate while preserving order
        seen = set()
        unique = []
        for cmd in selected:
            if cmd not in seen:
                seen.add(cmd)
                unique.append(cmd)
        return unique

    def _refresh_preview(self) -> None:
        # Generate live preview of strategy
        if self.var_minute_plan.get():
            r = random.Random()
            cmds = []
            # Build one-minute plan preview
            for _ in range(4):
                cmds.append(self._random_simple("hunt", r))
            for _ in range(5):
                cmds.append(self._random_coinflip(r))
            for _ in range(3):
                cmds.append(self._random_slots(r))
            for _ in range(2):
                cmds.append(self._random_blackjack(r))
            # Occasional noise
            noise = [f"{self._prefix(r)} cash", self._random_simple("hunt", r), self._random_simple("battle", r)]
            cmds.extend(r.sample(noise, k=2))
            r.shuffle(cmds)
        elif self.var_cashfarm.get():
            try:
                hunts_per_sell = max(1, int(self.var_hunts_per_sell.get()))
            except ValueError:
                hunts_per_sell = 10
            cmds = []
            for i in range(1, 13):
                # Mostly hunts
                cmds.append(self._random_simple("hunt"))
                if i % hunts_per_sell == 0:
                    cmds.append(self._random_simple("sell all"))
                if self.var_tiny_cf.get() and i % max(1, int(self.var_cf_every.get() or 7)) == 0:
                    cmds.append(self._random_coinflip())
        else:
            # Show per-command schedule sample
            cmds = []
            if self.en_hunt.get():
                cmds.append(f"every {self.iv_hunt.get()}s -> {self._random_simple('hunt')}")
            if self.en_cf.get():
                cmds.append(f"every {self.iv_cf.get()}s -> {self._random_coinflip()}")
            if self.en_slots.get():
                cmds.append(f"every {self.iv_slots.get()}s -> {self._random_slots()}")
            if self.en_pray.get():
                cmds.append(f"every {self.iv_pray.get()}s -> {self._prefix()} pray")
            if self.en_battle.get():
                cmds.append(f"every {self.iv_battle.get()}s -> {self._random_simple('battle')}")
        self.preview_box.delete('1.0', tk.END)
        for c in cmds:
            self.preview_box.insert(tk.END, f"{c}\n")

    def toggle(self) -> None:
        if not self.is_running:
            self.start()
        else:
            self.stop()

    def start(self) -> None:
        if not self.var_minute_plan.get() and not self.var_cashfarm.get() and not (self.var_economy.get() or self.var_animals.get() or self.var_gambling.get()):
            messagebox.showwarning("No commands", "Please select at least one category of commands.")
            return

        try:
            interval = max(1, int(self.interval_seconds.get()))
        except ValueError:
            messagebox.showerror("Invalid interval", "Interval must be an integer in seconds.")
            return

        self.is_running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.status_label.config(text=f"Running every {interval}s. Press Ctrl+P to stop.")

        self.worker = threading.Thread(target=self._run_loop, args=(interval,), daemon=True)
        self.worker.start()

    def stop(self) -> None:
        self.is_running = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status_label.config(text="Stopped.")

    def _run_loop(self, interval: int) -> None:
        base_tick_next = time.monotonic()
        rng = random.Random()
        hunts_done = 0

        # Initialize per-command next times
        def iv_safe(var: tk.StringVar, default: int) -> int:
            try:
                return max(1, int(var.get()))
            except Exception:
                return default

        sched = {
            'hunt': {'en': self.en_hunt, 'iv': lambda: iv_safe(self.iv_hunt, 15), 'next': time.monotonic()},
            'cf': {'en': self.en_cf, 'iv': lambda: iv_safe(self.iv_cf, 10), 'next': time.monotonic()},
            'slots': {'en': self.en_slots, 'iv': lambda: iv_safe(self.iv_slots, 10), 'next': time.monotonic()},
            'pray': {'en': self.en_pray, 'iv': lambda: iv_safe(self.iv_pray, 300), 'next': time.monotonic()},
            'battle': {'en': self.en_battle, 'iv': lambda: iv_safe(self.iv_battle, 15), 'next': time.monotonic()},
        }

        while self.is_running:
            base_tick_next += interval

            if self.var_minute_plan.get():
                # Construct the minute plan on first entry or when elapsed
                minute_start = time.monotonic()
                r = rng
                # Build list of 60-second schedule entries (command strings)
                tasks: list[str] = []
                tasks += [self._random_simple('hunt', r) for _ in range(4)]
                # Gambling amounts 200-500 (clamped)
                def clamp_200_500(cmd: str) -> str:
                    parts = cmd.split()
                    if parts:
                        try:
                            amt = int(parts[-1])
                            if amt < 200 or amt > 500:
                                parts[-1] = str(r.randint(200, 500))
                                return ' '.join(parts)
                        except ValueError:
                            pass
                    return cmd
                tasks += [clamp_200_500(self._random_coinflip(r)) for _ in range(5)]
                tasks += [clamp_200_500(self._random_slots(r)) for _ in range(3)]
                tasks += [clamp_200_500(self._random_blackjack(r)) for _ in range(2)]
                # Add a bit of noise
                noise_pool = [f"{self._prefix(r)} cash", self._random_simple('hunt', r), self._random_simple('battle', r)]
                tasks += r.sample(noise_pool, k=2)
                r.shuffle(tasks)

                # Evenly space across the minute with small jitter
                gap = 60.0 / max(1, len(tasks))
                for i, cmd in enumerate(tasks):
                    if not self.is_running or not self.var_minute_plan.get():
                        break
                    target = minute_start + i * gap + r.uniform(-0.4, 0.4)
                    # Wait until target time
                    while self.is_running and time.monotonic() < target:
                        time.sleep(0.05)
                    # Send command at 100wpm
                    self._type_at_100_wpm(cmd)
                    pyautogui.press('enter')
                    time.sleep(random.uniform(1.0, 2.0))
                    self.root.after(0, lambda c=cmd: self.status_label.config(text=f"Sent: {c}"))
                # Loop continues; base tick sleep below keeps cadence

            elif self.var_cashfarm.get():
                # 1) Hunt
                hunt_cmd = self._random_simple("hunt", rng)
                self._type_at_100_wpm(hunt_cmd)
                pyautogui.press('enter')
                time.sleep(random.uniform(1.0, 2.0))
                hunts_done += 1
                self.root.after(0, lambda c=hunt_cmd: self.status_label.config(text=f"Sent: {c}"))

                # 2) Periodic sell all
                try:
                    hunts_per_sell = max(1, int(self.var_hunts_per_sell.get()))
                except ValueError:
                    hunts_per_sell = 10
                if hunts_done % hunts_per_sell == 0 and self.is_running:
                    time.sleep(0.4)
                    sell_cmd = self._random_simple("sell all", rng)
                    self._type_at_100_wpm(sell_cmd)
                    pyautogui.press('enter')
                    time.sleep(random.uniform(1.0, 2.0))
                    self.root.after(0, lambda c=sell_cmd: self.status_label.config(text=f"Sent: {c}"))

                # 3) Optional tiny coinflip every N hunts
                if self.var_tiny_cf.get() and self.is_running:
                    try:
                        every = max(1, int(self.var_cf_every.get()))
                    except ValueError:
                        every = 7
                    if hunts_done % every == 0:
                        time.sleep(0.25)
                        cf_cmd = self._random_coinflip(rng)
                        # Force small amounts for safety
                        # Replace ending amount with small value if too large
                        parts = cf_cmd.split()
                        if parts:
                            try:
                                amt = int(parts[-1])
                                if amt > 25:
                                    parts[-1] = str(rng.randint(2, 25))
                                    cf_cmd = " ".join(parts)
                            except ValueError:
                                pass
                        self._type_at_100_wpm(cf_cmd)
                        pyautogui.press('enter')
                        time.sleep(random.uniform(1.0, 2.0))
                        self.root.after(0, lambda c=cf_cmd: self.status_label.config(text=f"Sent: {c}"))
            else:
                # Per-command scheduling
                now = time.monotonic()
                sent_any = False
                # For each enabled scheduled task, check and fire
                for key in ('hunt','cf','slots','pray','battle'):
                    entry = sched[key]
                    if not entry['en'].get():
                        continue
                    if now >= entry['next']:
                        if key == 'hunt':
                            cmd = self._random_simple('hunt', rng)
                        elif key == 'cf':
                            cmd = self._random_coinflip(rng)
                        elif key == 'slots':
                            cmd = self._random_slots(rng)
                        elif key == 'pray':
                            cmd = f"{self._prefix(rng)} pray"
                        else:  # battle
                            cmd = self._random_simple('battle', rng)
                        self._type_at_100_wpm(cmd)
                        pyautogui.press('enter')
                        time.sleep(random.uniform(1.0, 2.0))
                        self.root.after(0, lambda c=cmd: self.status_label.config(text=f"Sent: {c}"))
                        entry['next'] = now + entry['iv']()
                        sent_any = True
                        time.sleep(0.2)  # small gap if multiple fire together

                # If nothing fired this cycle, adjust sleep target to earliest next
                if not sent_any:
                    earliest_next = min(entry['next'] for entry in sched.values() if entry['en'].get())
                    base_tick_next = min(base_tick_next, earliest_next)

            # Sleep precisely until next slot
            remaining = base_tick_next - time.monotonic()
            while remaining > 0 and self.is_running:
                time.sleep(min(0.2, remaining))
                remaining = base_tick_next - time.monotonic()

    def _type_at_100_wpm(self, text: str) -> None:
        # 100 words/min = 0.6s per word; assume ~5 chars per word -> ~0.12s per char
        delay_per_char = 0.6 / 5.0
        for ch in text:
            if not self.is_running:
                break
            pyautogui.typewrite(ch)
            time.sleep(delay_per_char)

    # -------- Command generation with aliases and amounts --------
    def _prefix(self, rng: random.Random | None = None) -> str:
        use_alias = self.var_aliases.get()
        if use_alias:
            choices = ["owo", "o"]
            return (rng or random).choice(choices)
        return "owo"

    def _random_amount(self, rng: random.Random | None = None, lo: int = 2, hi: int = 1500) -> int:
        r = rng or random
        return r.randint(lo, hi)

    def _random_coinflip(self, rng: random.Random | None = None) -> str:
        r = rng or random
        # Hardcoded random variants
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
        r = rng or random
        amt = self._random_amount(r, 2, 500)
        token = "s" if (self.var_aliases.get() and r.random() < 0.5) else "slots"
        return f"{self._prefix(r)} {token} {amt}"

    def _random_blackjack(self, rng: random.Random | None = None) -> str:
        r = rng or random
        amt = self._random_amount(r, 2, 500)
        token = "bj" if (self.var_aliases.get() and r.random() < 0.7) else "blackjack"
        return f"{self._prefix(r)} {token} {amt}"

    def _random_lottery(self, rng: random.Random | None = None) -> str:
        r = rng or random
        tickets = self._random_amount(r, 2, 50)
        return f"{self._prefix(r)} lottery {tickets}"

    def _random_bet(self, rng: random.Random | None = None) -> str:
        r = rng or random
        amt = self._random_amount(r, 2, 1000)
        return f"{self._prefix(r)} bet {amt}"

    def _random_simple(self, word: str, rng: random.Random | None = None) -> str:
        r = rng or random
        # Support short aliases
        alias_map = {
            # Hardcoded variants, e.g., "owo hunt" | "owo h" | "o h"
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
        return f"{self._prefix(r)} {token}" if not token.startswith("o ") and token not in ("oh","ob") else f"{token}"

    def _random_social(self, rng: random.Random | None = None) -> str:
        r = rng or random
        action = r.choice(["hug", "kiss", "marry"])  # limited set
        target = r.choice(["@owo", "@friend", "@buddy"]) if action in ("hug", "kiss") else ""
        if target:
            return f"{self._prefix(r)} {action} {target}"
        return f"{self._prefix(r)} {action}"

    def _random_command(self, rng: random.Random | None = None) -> str:
        r = rng or random
        buckets = []
        if self.var_economy.get():
            buckets.append("economy")
        if self.var_animals.get():
            buckets.append("animals")
        if self.var_gambling.get():
            buckets.append("gambling")
        if not buckets:
            return f"{self._prefix(r)} ping"

        bucket = r.choice(buckets)
        if bucket == "gambling":
            return r.choice([
                self._random_coinflip(r),
                self._random_slots(r),
                self._random_blackjack(r),
                self._random_lottery(r),
                self._random_bet(r),
            ])
        if bucket == "animals":
            word = r.choice(self.commands_animals)
            return self._random_simple(word, r)
        # economy
        econ_word = r.choice(self.commands_economy)
        # Some economy commands need simple generation
        if any(econ_word.startswith(x) for x in ["sell all", "lootbox all", "crate all", "checklist", "cash", "team", "zoo", "inv", "autohunt"]):
            return self._random_simple(econ_word, r)
        return f"{self._prefix(r)} {econ_word}"


def main() -> None:
    root = tk.Tk()
    app = OwoAutoTyper(root)
    root.mainloop()


if __name__ == "__main__":
    main()


