import tkinter as tk
from tkinter import font

MAX_PLAYERS = 8
WIN = 3
DRAW = 1

class SealedTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Sealed Tournament")
        self.root.geometry("1100x780")
        self.root.configure(bg="#0b1026")

        self.players = []
        self.best_of = tk.IntVar(value=3)
        self.max_rounds = tk.IntVar(value=3)

        self.current_round = 0
        self.round_results = {}

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        tk.Label(
            self.root, text="MTG SEALED TOURNAMENT",
            fg="#f5d76e", bg="#0b1026",
            font=font.Font(size=22, weight="bold")
        ).pack(pady=10)

        setup = tk.Frame(self.root, bg="#0b1026")
        setup.pack()

        tk.Label(setup, text="Best of:", fg="white", bg="#0b1026").grid(row=0, column=0)
        tk.OptionMenu(setup, self.best_of, 1, 3, 5, 7).grid(row=0, column=1)

        tk.Label(setup, text="Group rounds:", fg="white", bg="#0b1026").grid(row=0, column=2)
        tk.OptionMenu(setup, self.max_rounds, 1, 2, 3, 4, 5, 6, 7).grid(row=0, column=3)

        self.entries = []
        for i in range(MAX_PLAYERS):
            e = tk.Entry(setup, width=20)
            e.grid(row=i+1, column=0, columnspan=4, pady=2)
            self.entries.append(e)

        tk.Button(self.root, text="Start Group Stage",
                  command=self.start_group).pack(pady=8)

        self.info = tk.Label(self.root, text="", fg="white", bg="#0b1026")
        self.info.pack()

        main = tk.Frame(self.root, bg="#0b1026")
        main.pack(fill="both", expand=True)

        self.match_frame = tk.Frame(main, bg="#0b1026")
        self.match_frame.pack(side="left", padx=20)

        self.score_frame = tk.Frame(main, bg="#0b1026")
        self.score_frame.pack(side="right", padx=20)

        nav = tk.Frame(self.root, bg="#0b1026")
        nav.pack(pady=6)

        tk.Button(nav, text="◀ Previous Round",
                  command=self.prev_round).pack(side="left", padx=6)
        tk.Button(nav, text="Next Round ▶",
                  command=self.next_round).pack(side="left", padx=6)

    # ---------------- GROUP STAGE ----------------
    def start_group(self):
        self.players = [e.get() for e in self.entries if e.get()]
        if len(self.players) < 2:
            return

        self.current_round = 1
        self.round_results = {1: {p: 0 for p in self.players}}
        self.show_round()

    def show_round(self):
        for w in self.match_frame.winfo_children():
            w.destroy()

        self.info.config(
            text=f"GROUP STAGE – ROUND {self.current_round}/{self.max_rounds.get()}"
        )

        temp = self.players.copy()
        while len(temp) >= 2:
            a = temp.pop(0)
            b = temp.pop(0)
            self.match_row(a, b)

        self.update_scoreboard()

    def match_row(self, a, b):
        row = tk.Frame(self.match_frame, bg="#0b1026")
        row.pack(pady=4)

        tk.Label(
            row, text=f"{a} vs {b} (Bo{self.best_of.get()})",
            fg="white", bg="#0b1026", width=32
        ).pack(side="left")

        tk.Button(row, text=a,
                  command=lambda: self.result(a, b, "A")).pack(side="left")
        tk.Button(row, text="Draw",
                  command=lambda: self.result(a, b, "D")).pack(side="left")
        tk.Button(row, text=b,
                  command=lambda: self.result(a, b, "B")).pack(side="left")

    def result(self, a, b, res):
        if res == "A":
            self.round_results[self.current_round][a] += WIN
        elif res == "B":
            self.round_results[self.current_round][b] += WIN
        else:
            self.round_results[self.current_round][a] += DRAW
            self.round_results[self.current_round][b] += DRAW

        self.update_scoreboard()

    # ---------------- ROUND NAVIGATION ----------------
    def next_round(self):
        if self.current_round >= self.max_rounds.get():
            return

        self.current_round += 1
        if self.current_round not in self.round_results:
            self.round_results[self.current_round] = {p: 0 for p in self.players}
            self.players = self.players[1:] + self.players[:1]

        self.show_round()

    def prev_round(self):
        if self.current_round <= 1:
            return

        del self.round_results[self.current_round]
        self.current_round -= 1
        self.show_round()

    # ---------------- SCOREBOARD ----------------
    def update_scoreboard(self):
        for w in self.score_frame.winfo_children():
            w.destroy()

        tk.Label(
            self.score_frame, text="ROUND SCORES",
            fg="#f5d76e", bg="#0b1026",
            font=font.Font(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=10, pady=4)

        tk.Label(self.score_frame, text="Player",
                 fg="white", bg="#0b1026").grid(row=1, column=0, sticky="w")

        for r in range(1, self.current_round + 1):
            tk.Label(self.score_frame, text=f"R{r}",
                     fg="white", bg="#0b1026").grid(row=1, column=r)

        tk.Label(self.score_frame, text="Total",
                 fg="white", bg="#0b1026").grid(row=1, column=self.current_round + 1)

        totals = {p: 0 for p in self.players}
        for r, data in self.round_results.items():
            for p, pts in data.items():
                totals[p] += pts

        for i, p in enumerate(self.players, start=2):
            tk.Label(self.score_frame, text=p,
                     fg="white", bg="#0b1026").grid(row=i, column=0, sticky="w")

            for r in range(1, self.current_round + 1):
                val = self.round_results.get(r, {}).get(p, 0)
                tk.Label(self.score_frame, text=str(val),
                         fg="white", bg="#0b1026").grid(row=i, column=r)

            tk.Label(self.score_frame, text=str(totals[p]),
                     fg="white", bg="#0b1026").grid(row=i, column=self.current_round + 1)

# ---------------- RUN ----------------
root = tk.Tk()
app = SealedTournament(root)
root.mainloop()
