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

    # Arena Remastered
    ("Amonkhet Remastered", "AKR"),
    ("Kaladesh Remastered", "KLR"),
    ("Dominaria Remastered", "DMR"),
    ("Innistrad Remastered", "INR"),
    ("Shadows over Innistrad Remastered", "SIR"),
    ("Ravnica Remastered", "RVR"),
    ("Khans of Tarkir", "KTK"),

    # Special
    ("Pioneer Masters", "PIO"),
    ("Modern Horizons 3", "MH3"),
    ("Lord of the Rings: Tales of Middle-earth", "LTR"),
]

class ArenaRoller:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Arena Roller")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG)

        self.mode = tk.StringVar(value="Sealed")
        self.players = tk.IntVar(value=2)

        self.roll_mode = None  # "AR" or "AP"
        self.excluded = set()
        self.picked = set()
        self.result_set = None

        self.build_ui()

    # ---------- UI ----------
    def build_ui(self):
        title_font = font.Font(size=26, weight="bold")
        text_font = font.Font(size=13)

        tk.Label(self.root, text="MTG ARENA",
                 fg=HIGHLIGHT, bg=BG,
                 font=title_font).pack(pady=10)

        # MODE
        mode_frame = tk.Frame(self.root, bg=BG)
        mode_frame.pack()

        for m in ("Sealed", "Draft"):
            tk.Radiobutton(
                mode_frame, text=m,
                variable=self.mode, value=m,
                bg=BG, fg=FG, selectcolor=BG,
                font=text_font
            ).pack(side="left", padx=10)

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

        self.ar_btn = tk.Button(
            roll_frame, text="AR",
            width=5,
            command=lambda: self.select_mode("AR")
        )
        self.ar_btn.pack(side="left", padx=8)

        self.dice_btn = tk.Button(
            roll_frame, text="🎲",
            font=("Arial", 42),
            command=self.roll_dice
        )
        self.dice_btn.pack(side="left", padx=12)

        self.ap_btn = tk.Button(
            roll_frame, text="AP",
            width=5,
            command=lambda: self.select_mode("AP")
        )
        self.ap_btn.pack(side="left", padx=8)

        tk.Button(self.root, text="Reset",
                  command=self.reset).pack(pady=5)

        # SET LIST
        self.set_frame = tk.Frame(self.root, bg=BG)
        self.set_frame.pack(pady=10)

        self.set_labels = {}
        self.draw_sets()

        self.link_frame = tk.Frame(self.root, bg=BG)
        self.link_frame.pack(pady=12)

    # ---------- MODE ----------
    def select_mode(self, mode):
        self.roll_mode = mode
        if mode == "AR":
            self.ar_btn.config(state="disabled")
            self.ap_btn.config(state="normal")
        else:
            self.ap_btn.config(state="disabled")
            self.ar_btn.config(state="normal")

    # ---------- SET LIST ----------
    def draw_sets(self):
        cols = 3
        for i, (name, code) in enumerate(SETS):
            lbl = tk.Label(
                self.set_frame, text=name,
                fg=FG, bg=BG, cursor="hand2"
            )
            lbl.grid(row=i // cols, column=i % cols,
                     padx=20, pady=3, sticky="w")
            lbl.bind("<Button-1>",
                     lambda e, c=code: self.toggle_set(c))
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

        self.animate_dice(6)

        if self.roll_mode == "AR":
            pool = [s for s in SETS if s[1] not in self.excluded]
        else:
            pool = [s for s in SETS if s[1] in self.picked]

        if not pool:
            return

        self.result_set = random.choice(pool)
        self.show_links()

    def animate_dice(self, steps):
        if steps <= 0:
            winsound.MessageBeep()
            return
        winsound.Beep(800, 30)
        self.root.after(40, lambda: self.animate_dice(steps - 1))

    # ---------- LINKS ----------
    def build_link(self, code):
        return f"https://draftsim.com/draft.php?mode={self.mode.get()}_{code}"

    def show_links(self):
        for w in self.link_frame.winfo_children():
            w.destroy()

        name, code = self.result_set
        tk.Label(
            self.link_frame,
            text=name,
            fg=HIGHLIGHT,
            bg=BG,
            font=("Arial", 18, "bold")
        ).pack(pady=6)

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


# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    ArenaRoller(root)
    root.mainloop()
