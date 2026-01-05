import tkinter as tk
import random
import webbrowser
import winsound
from tkinter import font, messagebox

# ---------------- CONFIG ----------------
BG = "#0b1026"
FG = "white"
HIGHLIGHT = "#f5d76e"
RED = "#cc3333"
GREEN = "#33cc66"

# Använder dina ursprungliga tider från koden
DRAFT_TIME = 50 * 60
SEALED_TIME = 30 * 60

SETS = [
    ("Core Set 2021", "M21"), ("Zendikar Rising", "ZNR"), ("Kaldheim", "KHM"),
    ("Strixhaven: School of Mages", "STX"), ("Adventures in the Forgotten Realms", "AFR"),
    ("Innistrad: Midnight Hunt", "MID"), ("Innistrad: Crimson Vow", "VOW"),
    ("Kamigawa: Neon Dynasty", "NEO"), ("Streets of New Capenna", "SNC"),
    ("Dominaria United", "DMU"), ("The Brothers' War", "BRO"),
    ("Phyrexia: All Will Be One", "ONE"), ("March of the Machine", "MOM"),
    ("Wilds of Eldraine", "WOE"), ("The Lost Caverns of Ixalan", "LCI"),
    ("Murders at Karlov Manor", "MKM"), ("Outlaws of Thunder Junction", "OTJ"),
    ("Bloomburrow", "BLB"), ("Duskmourn: House of Horror", "DSK"),
    ("EFL Aetherdrift", "DFT"), ("Edge of Eternity", "EOE"),
    ("Tarkir: Dragonstorm", "TDM"), ("Foundations", "FDN"),
    ("Amonkhet Remastered", "AKR"), ("Kaladesh Remastered", "KLR"),
    ("Dominaria Remastered", "DMR"), ("Innistrad Remastered", "INR"),
    ("Shadows over Innistrad Remastered", "SIR"), ("Ravnica Remastered", "RVR"),
    ("Khans of Tarkir", "KTK"), ("Pioneer Masters", "PIO"),
    ("Modern Horizons 3", "MH3"), ("Lord of the Rings: Tales of Middle-earth", "LTR"),
    ("Avatar: The Last Airbender", "TLA"), ("Final Fantasy", "FIN"),
]

# ---------------- APP ----------------
class ArenaRoller:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Arena Roller")
        self.root.geometry("1000x820")
        self.root.configure(bg=BG)

        self.mode = tk.StringVar(value=None)
        self.players = tk.IntVar(value=2)

        self.excluded = set()
        self.picked = set()
        self.result = None

        self.timer_id = None
        self.time_left = 0
        self.is_paused = False

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        title = font.Font(size=26, weight="bold")
        tk.Label(self.root, text="MTG ARENA",
                 fg=HIGHLIGHT, bg=BG, font=title).pack(pady=10)

        # MODE & PLAYERS FRAME
        controls_frame = tk.Frame(self.root, bg=BG)
        controls_frame.pack(pady=10)

        for m in ("Sealed", "Draft"):
            tk.Radiobutton(
                controls_frame, text=m, variable=self.mode, value=m,
                bg=BG, fg=FG, selectcolor=BG, activebackground=BG
            ).pack(side="left", padx=10)

        tk.Label(controls_frame, text="Players:", fg=FG, bg=BG).pack(side="left", padx=(20, 5))
        tk.Spinbox(controls_frame, from_=2, to=8,
                   textvariable=self.players, width=5).pack(side="left")

        # ROLL CONTROLS FRAME
        roll_frame = tk.Frame(self.root, bg=BG)
        roll_frame.pack(pady=15)

        self.ar_btn = tk.Button(roll_frame, text="AR", width=5, command=lambda: self.select_roll_mode("AR"))
        self.ar_btn.pack(side="left", padx=8)

        # Use a Label for the dice symbol which we can update during animation
        self.dice_label = tk.Label(roll_frame, text="🎲", font=("Arial", 48), bg=BG, cursor="hand2")
        self.dice_label.pack(side="left", padx=12)
        self.dice_label.bind("<Button-1>", lambda e: self.roll_dice())

        self.ap_btn = tk.Button(roll_frame, text="AP", width=5, command=lambda: self.select_roll_mode("AP"))
        self.ap_btn.pack(side="left", padx=8)
        
        tk.Button(self.root, text="Reset App", command=self.reset_app).pack(pady=4)

        # SET LIST FRAME
        self.set_frame = tk.Frame(self.root, bg=BG)
        self.set_frame.pack(pady=20)

        self.labels = {}
        cols = 3
        for i, (name, code) in enumerate(SETS):
            lbl = tk.Label(self.set_frame, text=name,
                           fg=FG, bg=BG, cursor="hand2")
            lbl.grid(row=i // cols, column=i % cols,
                     padx=30, pady=4, sticky="w")
            lbl.bind("<Button-1>", lambda e, c=code: self.toggle_set(c))
            self.labels[code] = lbl

        # LINKS FRAME (Result Display Area)
        self.link_frame = tk.Frame(self.root, bg=BG)
        self.link_frame.pack(pady=12)

        # TIMER FRAME (Bottom Left as in image context)
        self.timer_frame = tk.Frame(self.root, bg=BG)
        # Using place for exact positioning as implied by the original image's context
        self.timer_frame.place(x=10, y=770) 

        self.timer_label = tk.Label(self.timer_frame, text="00:00",
                                    fg=FG, bg=BG,
                                    font=("Arial", 16, "bold"))
        self.timer_label.pack(side="left")

        self.start_btn = tk.Button(self.timer_frame, text="Start",
                                   command=self.start_timer)
        self.start_btn.pack(side="left", padx=4)

        self.pause_btn = tk.Button(self.timer_frame, text="Pause",
                                   command=self.toggle_pause)
        self.pause_btn.pack(side="left", padx=4)
        
        self.stop_btn = tk.Button(self.timer_frame, text="Stop",
                                   command=self.stop_timer)
        self.stop_btn.pack(side="left", padx=4)

    # ---------------- SET TOGGLE ----------------
    def toggle_set(self, code):
        lbl = self.labels[code]
        if code in self.excluded:
            self.excluded.remove(code)
            lbl.config(fg=FG)
        elif code in self.picked:
            # If a set is picked (green), clicking makes it excluded (red)
            self.picked.remove(code)
            self.excluded.add(code)
            lbl.config(fg=RED)
        else:
            # Default state (white) -> picked (green)
            self.picked.add(code)
            lbl.config(fg=GREEN)

    # ---------------- ROLL ----------------
    def select_roll_mode(self, mode):
        self.roll_mode = mode
        # Visually indicate which mode is active via button state
        self.ar_btn.config(state="disabled" if mode == "AR" else "normal")
        self.ap_btn.config(state="disabled" if mode == "AP" else "normal")

    def roll_dice(self):
        if not hasattr(self, 'roll_mode') or not self.roll_mode:
            messagebox.showwarning("Varning", "Välj AR (All Random) eller AP (All Picked) först!")
            return
        
        self.anim_steps = 10
        self.animate_dice()

    def animate_dice(self):
        if self.anim_steps <= 0:
            self.finish_roll()
            # Använd winsound för ljudeffekt
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
            return
        
        # Byt tärningssymbol under animering
        symbols = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        self.dice_label.config(text=random.choice(symbols))
        winsound.Beep(500, 50)
        self.anim_steps -= 1
        self.root.after(80, self.animate_dice)

    def finish_roll(self):
        # Återställ till standard tärningssymbol
        self.dice_label.config(text="🎲")

        if self.roll_mode == "AR":
            # Använd alla set utom de exkluderade (röda)
            pool = [s for s in SETS if s[1] not in (self.excluded | self.picked)] 
        else: # AP mode
            # Använd endast de markerade (gröna) seten
            pool = [s for s in SETS if s[1] in self.picked]

        if not pool:
            messagebox.showinfo("Tom Pool", "Inga set tillgängliga att rulla från den valda poolen!")
            return
            
        self.result = random.choice(pool)
        self.show_links()

    # ---------------- LINKS & RESULTS ----------------
    def show_links(self):
        for w in self.link_frame.winfo_children():
            w.destroy()

        name, code = self.result
        tk.Label(self.link_frame, text=f"Rullat Set: {name}",
                 fg=HIGHLIGHT, bg=BG,
                 font=("Arial", 18, "bold")).pack(pady=6)

        if not self.mode.get():
            return

        for i in range(self.players.get()):
            url = f"draftsim.com{self.mode.get()}_{code}"
            tk.Button(self.link_frame,
                      text=f"Spelare {i+1} {self.mode.get()}",
                      command=lambda u=url: webbrowser.open(u)).pack(pady=2)

    # ---------------- TIMER ----------------
    def start_timer(self):
        if self.timer_id: # Avbryt befintlig timer först
            self.root.after_cancel(self.timer_id)
        if not self.mode.get():
            messagebox.showwarning("Varning", "Välj Sealed eller Draft för att starta timern!")
            return
            
        self.time_left = DRAFT_TIME if self.mode.get() == "Draft" else SEALED_TIME
        self.is_paused = False
        self.update_timer_display()

    def update_timer_display(self):
        if self.time_left >= 0 and not self.is_paused:
            mins = self.time_left // 60
            secs = self.time_left % 60
            self.timer_label.config(
                text=f"{mins:02}:{secs:02}",
                fg=RED if self.time_left <= 300 else FG # Röd färg sista 5 minuterna
            )
            if self.time_left == 0:
                winsound.PlaySound("SystemExit", winsound.SND_ALIAS)
                # Kanske lägga in en messagebox här också?
                return
            self.time_left -= 1
        
        # Schemalägg nästa uppdatering
        self.timer_id = self.root.after(1000, self.update_timer_display)

    def toggle_pause(self):
        self.is_paused = not self.is_paused

    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.time_left = 0
        self.is_paused = False
        self.timer_label.config(text="00:00", fg=FG)

    def reset_app(self):
        """Fullständig nollställning av applikationen."""
        self.stop_timer()
        self.excluded.clear()
        self.picked.clear()
        # Återställ alla labels färger
        for lbl in self.labels.values(): lbl.config(fg=FG)
        # Rensa resultatlänkarna
        for w in self.link_frame.winfo_children(): w.destroy()
        # Återställ roll-lägesknapparna
        self.ar_btn.config(state="normal")
        self.ap_btn.config(state="normal")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = ArenaRoller(root)
    root.mainloop()

