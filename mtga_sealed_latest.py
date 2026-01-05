import tkinter as tk
import random
import webbrowser
import winsound
from tkinter import font

BG = "#0b1026"
FG = "white"
HIGHLIGHT = "#f5d76e"
EXCLUDED = "#cc3333"
PICKED = "#33cc66"

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


class ArenaRoller:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Arena Roller")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG)

        self.mode = tk.StringVar(value="")
        self.players = tk.IntVar(value=2)

        self.roll_mode = None
        self.excluded = set()
        self.picked = set()
        self.result_set = None

        # Timer state
        self.time_left = 0
        self.timer_running = False
        self.timer_paused = False

        self.build_ui()

    # ---------- UI ----------
    def build_ui(self):
        title_font = font.Font(size=26, weight="bold")

        tk.Label(self.root, text="MTG ARENA",
                 fg=HIGHLIGHT, bg=BG,
                 font=title_font).pack(pady=10)

        # MODE SELECTION
        mode_frame = tk.Frame(self.root, bg=BG)
        mode_frame.pack()

        tk.Radiobutton(mode_frame, text="Sealed",
                       variable=self.mode, value="Sealed",
                       bg=BG, fg=FG, selectcolor=BG,
                       command=self.start_timer).pack(side="left", padx=10)

        tk.Radiobutton(mode_frame, text="Draft",
                       variable=self.mode, value="Draft",
                       bg=BG, fg=FG, selectcolor=BG,
                       command=self.start_timer).pack(side="left", padx=10)

        # PLAYERS
        pframe = tk.Frame(self.root, bg=BG)
        pframe.pack(pady=6)

        tk.Label(pframe, text="Players:", fg=FG, bg=BG).pack(side="left")
        tk.Spinbox(pframe, from_=2, to=8,
                   textvariable=self.players,
                   width=5).pack(side="left", padx=6)

        # ROLL CONTROLS
        roll_frame = tk.Frame(self.root, bg=BG)
        roll_frame.pack(pady=15)

        self.ar_btn = tk.Button(roll_frame, text="AR", width=5,
                                 command=lambda: self.select_mode("AR"))
        self.ar_btn.pack(side="left", padx=8)

        self.dice_btn = tk.Button(roll_frame, text="🎲",
                                   font=("Arial", 44),
                                   command=self.roll_dice)
        self.dice_btn.pack(side="left", padx=12)

        self.ap_btn = tk.Button(roll_frame, text="AP", width=5,
                                 command=lambda: self.select_mode("AP"))
        self.ap_btn.pack(side="left", padx=8)

        tk.Button(self.root, text="Reset", command=self.reset).pack(pady=5)

        # SET LIST
        self.set_frame = tk.Frame(self.root, bg=BG)
        self.set_frame.pack(pady=10)

        self.set_labels = {}
        self.draw_sets()

        # LINKS
        self.link_frame = tk.Frame(self.root, bg=BG)
        self.link_frame.pack(pady=12)

        # TIMER (bottom left)
        self.timer_frame = tk.Frame(self.root, bg=BG)
        self.timer_frame.place(x=10, y=740)

        self.timer_label = tk.Label(self.timer_frame, text="",
                                    fg=FG, bg=BG,
                                    font=("Arial", 16, "bold"))
        self.timer_label.pack(side="left")

        self.pause_btn = tk.Button(self.timer_frame, text="Pause",
                                   command=self.toggle_pause)
        self.pause_btn.pack(side="left", padx=6)

        self.hide_timer()

    # ---------- TIMER ----------
    def start_timer(self):
        if self.mode.get() == "Draft":
            self.time_left = DRAFT_TIME
        elif self.mode.get() == "Sealed":
            self.time_left = SEALED_TIME
        else:
            return

        self.timer_running = True
        self.timer_paused = False
        self.pause_btn.config(text="Pause")
        self.update_timer()
        self.show_timer()

    def update_timer(self):
        if not self.timer_running:
            return

        if not self.timer_paused:
            mins = self.time_left // 60
            secs = self.time_left % 60
            color = EXCLUDED if self.time_left <= 300 else FG
            self.timer_label.config(
                text=f"{mins:02}:{secs:02}",
                fg=color
            )

            if self.time_left == 0:
                winsound.Beep(1000, 700)
                self.timer_running = False
                return

            self.time_left -= 1

        self.root.after(1000, self.update_timer)

    def toggle_pause(self):
        if not self.timer_running:
            return
        self.timer_paused = not self.timer_paused
        self.pause_btn.config(text="Resume" if self.timer_paused else "Pause")

    def hide_timer(self):
        self.timer_label.config(text="")
        self.pause_btn.pack_forget()

    def show_timer(self):
        self.pause_btn.pack(side="left", padx=6)

    # ---------- MODE ----------
    def select_mode(self, mode):
        self.roll_mode = mode
        self.ar_btn.config(state="disabled" if mode == "AR" else "normal")
        self.ap_btn.config(state="disabled" if mode == "AP" else "normal")

    # ---------- SET LIST ----------
    def draw_sets(self):
        cols = 3
        for i, (name, code) in enumerate(SETS):
            lbl = tk.Label(self.set_frame, text=name,
                           fg=FG, bg=BG, cursor="hand2")
            lbl.grid(row=i // cols, column=i % cols,
                     padx=20, pady=3, sticky="w")
            lbl.bind("<Button-1>", lambda e, c=code: self.toggle_set(c))
            self.set_labels[code] = lbl

    def toggle_set(self, code):
        lbl = self.set_labels[code]
        if code in self.excluded:
            self.excluded.remove(code)
            lbl.config(fg=FG)
        elif code in self.picked:
            self.picked.remove(code)
            self.excluded.add(code)
            lbl.config(fg=EXCLUDED)
        else:
            self.picked.add(code)
            lbl.config(fg=PICKED)

    # ---------- ROLL ----------
    def roll_dice(self):
        if not self.roll_mode:
            return

        winsound.Beep(700, 40)

        pool = (
            [s for s in SETS if s[1] not in self.excluded]
            if self.roll_mode == "AR"
            else [s for s in SETS if s[1] in self.picked]
        )

        if not pool:
            return

        self.result_set = random.choice(pool)
        self.show_links()

    # ---------- LINKS ----------
    def build_link(self, code):
        return f"https://draftsim.com/draft.php?mode={self.mode.get()}_{code}"

    def show_links(self):
        for w in self.link_frame.winfo_children():
            w.destroy()

        name, code = self.result_set
        tk.Label(self.link_frame, text=name,
                 fg=HIGHLIGHT, bg=BG,
                 font=("Arial", 18, "bold")).pack(pady=6)

        for i in range(self.players.get()):
            tk.Button(
                self.link_frame,
                text=f"{self.mode.get()} {i + 1}",
                command=lambda u=self.build_link(code): webbrowser.open(u)
            ).pack(pady=2)

    # ---------- RESET ----------
    def reset(self):
        self.roll_mode = None
        self.excluded.clear()
        self.picked.clear()
        self.result_set = None

        self.ar_btn.config(state="normal")
        self.ap_btn.config(state="normal")

        for lbl in self.set_labels.values():
            lbl.config(fg=FG)

        for w in self.link_frame.winfo_children():
            w.destroy()

        self.timer_running = False
        self.hide_timer()
        self.mode.set("")


# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    ArenaRoller(root)
    root.mainloop()
