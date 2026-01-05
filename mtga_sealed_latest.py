import tkinter as tk
import random
import webbrowser
import winsound
from tkinter import font

# ---------------- CONFIG ----------------
BG = "#0b1026"
FG = "white"
HIGHLIGHT = "#f5d76e"
RED = "#cc3333"
GREEN = "#33cc66"

DRAFT_TIME = 50 * 60
SEALED_TIME = 30 * 60

SETS = [
    ("Core Set 2021", "M21"),
    ("Zendikar Rising", "ZNR"),
    ("Kaldheim", "KHM"),
    ("Strixhaven: School of Mages", "STX"),
    ("Adventures in the Forgotten Realms", "AFR"),
    ("Innistrad: Midnight Hunt", "MID"),
    ("Innistrad: Crimson Vow", "VOW"),
    ("Kamigawa: Neon Dynasty", "NEO"),
    ("Streets of New Capenna", "SNC"),
    ("Dominaria United", "DMU"),
    ("The Brothers' War", "BRO"),
    ("Phyrexia: All Will Be One", "ONE"),
    ("March of the Machine", "MOM"),
    ("Wilds of Eldraine", "WOE"),
    ("The Lost Caverns of Ixalan", "LCI"),
    ("Murders at Karlov Manor", "MKM"),
    ("Outlaws of Thunder Junction", "OTJ"),
    ("Bloomburrow", "BLB"),
    ("Duskmourn: House of Horror", "DSK"),
    ("Aetherdrift", "DFT"),
    ("Edge of Eternity", "EOE"),
    ("Tarkir: Dragonstorm", "TDM"),
    ("Foundations", "FDN"),
    ("Amonkhet Remastered", "AKR"),
    ("Kaladesh Remastered", "KLR"),
    ("Dominaria Remastered", "DMR"),
    ("Innistrad Remastered", "INR"),
    ("Shadows over Innistrad Remastered", "SIR"),
    ("Ravnica Remastered", "RVR"),
    ("Khans of Tarkir", "KTK"),
    ("Pioneer Masters", "PIO"),
    ("Modern Horizons 3", "MH3"),
    ("Lord of the Rings: Tales of Middle-earth", "LTR"),
    ("Avatar: The Last Airbender", "TLA"),
    ("Final Fantasy", "FIN"),
]

# ---------------- APP ----------------
class ArenaRoller:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Arena Roller")
        self.root.geometry("1200x820")
        self.root.configure(bg=BG)

        self.mode = tk.StringVar(value=None)
        self.players = tk.IntVar(value=2)

        self.roll_mode = None
        self.excluded = set()
        self.picked = set()
        self.result = None

        self.timer_running = False
        self.timer_paused = False
        self.time_left = 0

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        title = font.Font(size=26, weight="bold")
        tk.Label(self.root, text="MTG ARENA",
                 fg=HIGHLIGHT, bg=BG, font=title).pack(pady=10)

        # MODE
        mode_frame = tk.Frame(self.root, bg=BG)
        mode_frame.pack()

        for m in ("Sealed", "Draft"):
            tk.Radiobutton(
                mode_frame, text=m, variable=self.mode, value=m,
                bg=BG, fg=FG, selectcolor=BG
            ).pack(side="left", padx=10)

        # PLAYERS
        pframe = tk.Frame(self.root, bg=BG)
        pframe.pack(pady=6)
        tk.Label(pframe, text="Players:", fg=FG, bg=BG).pack(side="left")
        tk.Spinbox(pframe, from_=2, to=8,
                   textvariable=self.players, width=5).pack(side="left")

        # ROLL CONTROLS
        roll = tk.Frame(self.root, bg=BG)
        roll.pack(pady=15)

        self.ar_btn = tk.Button(roll, text="AR", width=5,
                                 command=lambda: self.select_roll_mode("AR"))
        self.ar_btn.pack(side="left", padx=8)

        self.dice_btn = tk.Button(
            roll, text="🎲", font=("Arial", 48),
            command=self.roll_dice
        )
        self.dice_btn.pack(side="left", padx=12)

        self.ap_btn = tk.Button(roll, text="AP", width=5,
                                 command=lambda: self.select_roll_mode("AP"))
        self.ap_btn.pack(side="left", padx=8)

        tk.Button(self.root, text="Reset", command=self.reset).pack(pady=4)

        # SET LIST
        self.set_frame = tk.Frame(self.root, bg=BG)
        self.set_frame.pack(pady=10)

        self.labels = {}
        cols = 3
        for i, (name, code) in enumerate(SETS):
            lbl = tk.Label(self.set_frame, text=name,
                           fg=FG, bg=BG, cursor="hand2")
            lbl.grid(row=i // cols, column=i % cols,
                     padx=20, pady=3, sticky="w")
            lbl.bind("<Button-1>", lambda e, c=code: self.toggle_set(c))
            self.labels[code] = lbl

        # LINKS
        self.link_frame = tk.Frame(self.root, bg=BG)
        self.link_frame.pack(pady=12)

        # TIMER
        self.timer_frame = tk.Frame(self.root, bg=BG)
        self.timer_frame.place(x=10, y=770)

        self.timer_label = tk.Label(self.timer_frame, text="",
                                    fg=FG, bg=BG,
                                    font=("Arial", 16, "bold"))
        self.timer_label.pack(side="left")

        self.start_btn = tk.Button(self.timer_frame, text="Start",
                                   command=self.start_timer)
        self.start_btn.pack(side="left", padx=4)

        self.pause_btn = tk.Button(self.timer_frame, text="Pause",
                                   command=self.pause_timer)
        self.pause_btn.pack(side="left", padx=4)

        self.hide_timer()

    # ---------------- SET TOGGLE ----------------
    def toggle_set(self, code):
        lbl = self.labels[code]
        if code in self.excluded:
            self.excluded.remove(code)
            lbl.config(fg=FG)
        elif code in self.picked:
            self.picked.remove(code)
            self.excluded.add(code)
            lbl.config(fg=RED)
        else:
            self.picked.add(code)
            lbl.config(fg=GREEN)

    # ---------------- ROLL ----------------
    def select_roll_mode(self, mode):
        self.roll_mode = mode
        self.ar_btn.config(state="disabled" if mode == "AR" else "normal")
        self.ap_btn.config(state="disabled" if mode == "AP" else "normal")

    def roll_dice(self):
        if not self.roll_mode:
            return
        self.anim_steps = 12
        self.animate_dice()

    def animate_dice(self):
        if self.anim_steps <= 0:
            self.finish_roll()
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            return
        winsound.Beep(600, 20)
        self.anim_steps -= 1
        self.root.after(70, self.animate_dice)

    def finish_roll(self):
        pool = (
            [s for s in SETS if s[1] not in self.excluded]
            if self.roll_mode == "AR"
            else [s for s in SETS if s[1] in self.picked]
        )
        if not pool:
            return
        self.result = random.choice(pool)
        self.show_links()

    # ---------------- LINKS ----------------
    def show_links(self):
        for w in self.link_frame.winfo_children():
            w.destroy()

        name, code = self.result
        tk.Label(self.link_frame, text=name,
                 fg=HIGHLIGHT, bg=BG,
                 font=("Arial", 18, "bold")).pack(pady=6)

        if not self.mode.get():
            return

        for i in range(self.players.get()):
            url = f"https://draftsim.com/draft.php?mode={self.mode.get()}_{code}"
            tk.Button(self.link_frame,
                      text=f"{self.mode.get()} {i+1}",
                      command=lambda u=url: webbrowser.open(u)).pack(pady=2)

    # ---------------- TIMER ----------------
    def start_timer(self):
        if not self.mode.get():
            return
        self.time_left = DRAFT_TIME if self.mode.get() == "Draft" else SEALED_TIME
        self.timer_running = True
        self.timer_paused = False
        self.update_timer()
        self.show_timer()

    def update_timer(self):
        if not self.timer_running:
            return
        if not self.timer_paused:
            mins = self.time_left // 60
            secs = self.time_left % 60
            self.timer_label.config(
                text=f"{mins:02}:{secs:02}",
                fg=RED if self.time_left <= 300 else FG
            )
            if self.time_left == 0:
                winsound.Beep(1000, 800)
                self.timer_running = False
                return
            self.time_left -= 1
        self.root.after(1000, self.update_timer)

    def pause_timer(self):
        if self.timer_running:
            self.timer_paused = not self.timer_paused
            self.pause_btn.config(text="Resume" if self.timer_paused else "Pause")

    def hide_timer(self):
        self.timer_label.config(text="")
        self.start_btn.pack_forget()
        self.pause_btn.pack_forget()

    def show_timer(self):
        self.start_btn.pack(side="left", padx=4)
        self.pause_btn.pack(side="left", padx=4)

    # ---------------- RESET ----------------
    def reset(self):
        self.roll_mode = None
        self.excluded.clear()
        self.picked.clear()
        self.result = None

        self.ar_btn.config(state="normal")
        self.ap_btn.config(state="normal")

        for lbl in self.labels.values():
            lbl.config(fg=FG)

        for w in self.link_frame.winfo_children():
            w.destroy()

        self.timer_running = False
        self.hide_timer()
        self.mode.set(None)


# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    ArenaRoller(root)
    root.mainloop()
