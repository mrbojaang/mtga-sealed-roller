import tkinter as tk
from tkinter import font, messagebox, ttk
import random
import webbrowser
import winsound

# ---------------- CONFIG ----------------
BG_COLOR = "#0b1026"
SECONDARY_BG = "#161b33"
FG_COLOR = "#ffffff"
HIGHLIGHT = "#f5d76e"
RED = "#ff4c4c"
GREEN = "#44ff44"

# Uppdaterade tider enligt officiella regler (ungefärliga)
DRAFT_TIME = 25 * 60 
SEALED_TIME = 30 * 60

SETS = [
    ("Foundations", "FDN"), ("Duskmourn", "DSK"), ("Bloomburrow", "BLB"),
    ("Modern Horizons 3", "MH3"), ("Outlaws of Thunder Junction", "OTJ"),
    ("Murders at Karlov Manor", "MKM"), ("Lost Caverns of Ixalan", "LCI"),
    ("Wilds of Eldraine", "WOE"), ("March of the Machine", "MOM"),
    ("Phyrexia: All Will Be One", "ONE"), ("The Brothers' War", "BRO"),
    ("Dominaria United", "DMU"), ("Streets of New Capenna", "SNC"),
    ("Kamigawa: Neon Dynasty", "NEO"), ("Innistrad: Crimson Vow", "VOW"),
    ("Innistrad: Midnight Hunt", "MID"), ("Strixhaven", "STX"),
    ("Kaldheim", "KHM"), ("Zendikar Rising", "ZNR")
]

class ArenaRoller:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Arena Tournament Assistant")
        self.root.geometry("900x850")
        self.root.configure(bg=BG_COLOR)

        self.mode = tk.StringVar(value="")
        self.players = tk.IntVar(value=2)
        self.excluded = set()
        self.picked = set()
        self.timer_id = None
        self.time_left = 0
        self.is_paused = False

        self.build_ui()

    def build_ui(self):
        # Header
        header_font = font.Font(family="Segoe UI", size=28, weight="bold")
        tk.Label(self.root, text="MTG ARENA ROLLER", fg=HIGHLIGHT, bg=BG_COLOR, font=header_font).pack(pady=20)

        # Control Panel (Mode & Players)
        ctrl_frame = tk.Frame(self.root, bg=SECONDARY_BG, padx=20, pady=15, relief="flat")
        ctrl_frame.pack(fill="x", padx=50)

        # Mode Selection
        mode_subframe = tk.Frame(ctrl_frame, bg=SECONDARY_BG)
        mode_subframe.pack(side="left")
        tk.Label(mode_subframe, text="Format:", fg=FG_COLOR, bg=SECONDARY_BG, font=("Arial", 10, "bold")).pack(side="left", padx=5)
        for m in ["Sealed", "Draft"]:
            tk.Radiobutton(mode_subframe, text=m, variable=self.mode, value=m, 
                           bg=SECONDARY_BG, fg=FG_COLOR, selectcolor=BG_COLOR,
                           activebackground=SECONDARY_BG).pack(side="left", padx=10)

        # Player Count
        p_subframe = tk.Frame(ctrl_frame, bg=SECONDARY_BG)
        p_subframe.pack(side="right")
        tk.Label(p_subframe, text="Players:", fg=FG_COLOR, bg=SECONDARY_BG, font=("Arial", 10, "bold")).pack(side="left", padx=5)
        tk.Spinbox(p_subframe, from_=1, to=8, textvariable=self.players, width=3).pack(side="left")

        # Scrollable Set List
        self.canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(50, 0), pady=20)
        self.scrollbar.pack(side="left", fill="y", pady=20)

        self.labels = {}
        for i, (name, code) in enumerate(SETS):
            lbl = tk.Label(self.scroll_frame, text=f"• {name}", fg=FG_COLOR, bg=BG_COLOR, 
                           font=("Segoe UI", 11), cursor="hand2", anchor="w")
            lbl.grid(row=i // 2, column=i % 2, padx=20, pady=5, sticky="w")
            lbl.bind("<Button-1>", lambda e, c=code: self.toggle_set(c))
            self.labels[code] = lbl

        # Action Side Panel
        side_panel = tk.Frame(self.root, bg=BG_COLOR, padx=20)
        side_panel.pack(side="right", fill="y", pady=20)

        self.dice_btn = tk.Button(side_panel, text="🎲 ROLL", font=("Arial", 14, "bold"),
                                  bg=HIGHLIGHT, fg=BG_COLOR, width=10, height=2,
                                  command=self.roll_dice)
        self.dice_btn.pack(pady=10)

        # Timer Display
        self.timer_label = tk.Label(side_panel, text="00:00", fg=FG_COLOR, bg=BG_COLOR, font=("Consolas", 24, "bold"))
        self.timer_label.pack(pady=10)
        
        tk.Button(side_panel, text="Start Timer", command=self.start_timer, width=12).pack(pady=2)
        tk.Button(side_panel, text="Pause/Resume", command=self.toggle_pause, width=12).pack(pady=2)
        tk.Button(side_panel, text="Reset", command=self.reset_app, width=12).pack(pady=20)

        # Link Area
        self.link_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.link_frame.pack(side="bottom", fill="x", pady=20)

    # ---------------- LOGIC ----------------
    def toggle_set(self, code):
        if code in self.excluded:
            self.excluded.remove(code)
            self.labels[code].config(fg=FG_COLOR)
        elif code in self.picked:
            self.picked.remove(code)
            self.excluded.add(code)
            self.labels[code].config(fg=RED)
        else:
            self.picked.add(code)
            self.labels[code].config(fg=GREEN)

    def roll_dice(self):
        if not self.mode.get():
            messagebox.showwarning("Warning", "Select Sealed or Draft first!")
            return
        
        # Animation simulation
        for _ in range(5):
            self.root.update()
            winsound.Beep(400, 50)
        
        pool = [s for s in SETS if s[1] not in self.excluded]
        if self.picked:
            pool = [s for s in SETS if s[1] in self.picked]
            
        if not pool: return
        result = random.choice(pool)
        self.display_result(result)

    def display_result(self, result):
        for w in self.link_frame.winfo_children(): w.destroy()
        name, code = result
        tk.Label(self.link_frame, text=f"Result: {name}", fg=HIGHLIGHT, bg=BG_COLOR, font=("Arial", 14, "bold")).pack()
        
        btn_frame = tk.Frame(self.link_frame, bg=BG_COLOR)
        btn_frame.pack()
        
        for i in range(self.players.get()):
            url = f"https://draftsim.com/draft.php?mode={self.mode.get()}_{code}"
            tk.Button(btn_frame, text=f"Player {i+1}", command=lambda u=url: webbrowser.open(u)).pack(side="left", padx=5, pady=10)

    def start_timer(self):
        if self.timer_id: self.root.after_cancel(self.timer_id)
        if not self.mode.get(): return
        
        self.time_left = DRAFT_TIME if self.mode.get() == "Draft" else SEALED_TIME
        self.is_paused = False
        self.run_timer()

    def run_timer(self):
        if self.time_left >= 0 and not self.is_paused:
            mins, secs = divmod(self.time_left, 60)
            self.timer_label.config(text=f"{mins:02}:{secs:02}", fg=RED if self.time_left < 60 else FG_COLOR)
            if self.time_left == 0:
                winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
                messagebox.showinfo("Time's Up!", "Time to start the matches!")
                return
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.run_timer)
        elif self.is_paused:
            self.timer_id = self.root.after(1000, self.run_timer)

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def reset_app(self):
        if self.timer_id: self.root.after_cancel(self.timer_id)
        self.excluded.clear()
        self.picked.clear()
        for lbl in self.labels.values(): lbl.config(fg=FG_COLOR)
        self.timer_label.config(text="00:00", fg=FG_COLOR)
        for w in self.link_frame.winfo_children(): w.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ArenaRoller(root)
    root.mainloop()
