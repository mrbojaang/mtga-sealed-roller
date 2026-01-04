import tkinter as tk
from tkinter import font

MAX_PLAYERS = 8
WIN = 3
DRAW = 1

class SealedTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Sealed Tournament")
        self.root.geometry("820x720")
        self.root.configure(bg="#0b1026")

        self.players = []
        self.scores = {}
        self.matches = []
        self.best_of = tk.IntVar(value=3)

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        title = tk.Label(
            self.root, text="MTG SEALED TOURNAMENT",
            fg="#f5d76e", bg="#0b1026",
            font=font.Font(size=22, weight="bold")
        )
        title.pack(pady=10)

        setup = tk.Frame(self.root, bg="#0b1026")
        setup.pack()

        tk.Label(setup, text="Best of:", fg="white", bg="#0b1026").grid(row=0, column=0)
        tk.OptionMenu(setup, self.best_of, 1, 3, 5, 7).grid(row=0, column=1)

        self.entries = []
        for i in range(MAX_PLAYERS):
            e = tk.Entry(setup, width=18)
            e.grid(row=i+1, column=0, columnspan=2, pady=2)
            self.entries.append(e)

        tk.Button(
            self.root, text="Start Group Stage",
            command=self.start_group
        ).pack(pady=10)

        self.match_frame = tk.Frame(self.root, bg="#0b1026")
        self.match_frame.pack()

        self.standings = tk.Label(
            self.root, text="", fg="white",
            bg="#0b1026", justify="left"
        )
        self.standings.pack(pady=10)

        self.playoff_btn = tk.Button(
            self.root, text="Start Playoffs",
            command=self.start_playoffs
        )

    # ---------------- GROUP STAGE ----------------
    def start_group(self):
        self.players = [e.get() for e in self.entries if e.get()]
        if len(self.players) < 2:
            return

        self.scores = {p: 0 for p in self.players}
        self.generate_matches()

    def generate_matches(self):
        for w in self.match_frame.winfo_children():
            w.destroy()

        self.matches = []
        temp = self.players.copy()

        while len(temp) >= 2:
            a = temp.pop(0)
            b = temp.pop(0)
            self.matches.append((a, b))
            self.match_row(a, b)

    def match_row(self, a, b):
        row = tk.Frame(self.match_frame, bg="#0b1026")
        row.pack(pady=4)

        tk.Label(
            row, text=f"{a} vs {b} (Bo{self.best_of.get()})",
            fg="white", bg="#0b1026", width=30
        ).pack(side="left")

        tk.Button(row, text=a, command=lambda: self.result(a, b, "A")).pack(side="left")
        tk.Button(row, text="Draw", command=lambda: self.result(a, b, "D")).pack(side="left")
        tk.Button(row, text=b, command=lambda: self.result(a, b, "B")).pack(side="left")

    def result(self, a, b, res):
        if res == "A":
            self.scores[a] += WIN
        elif res == "B":
            self.scores[b] += WIN
        else:
            self.scores[a] += DRAW
            self.scores[b] += DRAW

        self.update_standings()

    def update_standings(self):
        text = "STANDINGS\n"
        for i, (p, s) in enumerate(
            sorted(self.scores.items(), key=lambda x: x[1], reverse=True), 1
        ):
            text += f"{i}. {p} – {s}p\n"
        self.standings.config(text=text)

        if len(self.players) >= 4:
            self.playoff_btn.pack(pady=10)

    # ---------------- PLAYOFFS ----------------
    def start_playoffs(self):
        for w in self.match_frame.winfo_children():
            w.destroy()

        top4 = sorted(self.scores, key=self.scores.get, reverse=True)[:4]

        tk.Label(
            self.match_frame, text="PLAYOFF BRACKET",
            fg="#f5d76e", bg="#0b1026",
            font=font.Font(size=16, weight="bold")
        ).pack(pady=6)

        self.bracket_match(top4[0], top4[3])
        self.bracket_match(top4[1], top4[2])

    def bracket_match(self, a, b):
        row = tk.Frame(self.match_frame, bg="#0b1026")
        row.pack(pady=6)

        tk.Label(row, text=f"{a} vs {b}", fg="white", bg="#0b1026").pack(side="left")
        tk.Button(row, text=a, command=lambda: self.champion(a)).pack(side="left", padx=6)
        tk.Button(row, text=b, command=lambda: self.champion(b)).pack(side="left", padx=6)

    def champion(self, name):
        self.standings.config(text=f"🏆 CHAMPION: {name}")

# ---------------- RUN ----------------
root = tk.Tk()
app = SealedTournament(root)
root.mainloop()
