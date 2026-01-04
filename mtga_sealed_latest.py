import tkinter as tk
from tkinter import font

MAX_PLAYERS = 8
WIN = 3
DRAW = 1
BG = "#0b1026"

class SealedTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Sealed Tournament")
        self.root.geometry("1150x800")
        self.root.configure(bg=BG)

        self.players = []
        self.best_of = tk.IntVar(value=3)
        self.max_rounds = tk.IntVar(value=3)

        self.current_round = 0
        self.round_results = {}
        self.playoffs_started = False

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        self.title_font = font.Font(size=26, weight="bold")
        self.header_font = font.Font(size=16, weight="bold")
        self.text_font = font.Font(size=13)

        tk.Label(
            self.root, text="MTG SEALED TOURNAMENT",
            fg="#f5d76e", bg=BG, font=self.title_font
        ).pack(pady=12)

        setup = tk.Frame(self.root, bg=BG)
        setup.pack()

        tk.Label(setup, text="Best of:", fg="white", bg=BG, font=self.text_font)\
            .grid(row=0, column=0, padx=4)
        tk.OptionMenu(setup, self.best_of, 1, 3, 5, 7)\
            .grid(row=0, column=1, padx=4)

        tk.Label(setup, text="Group rounds:", fg="white", bg=BG, font=self.text_font)\
            .grid(row=0, column=2, padx=4)
        tk.OptionMenu(setup, self.max_rounds, 1, 2, 3, 4, 5, 6, 7)\
            .grid(row=0, column=3, padx=4)

        self.entries = []
        for i in range(MAX_PLAYERS):
            e = tk.Entry(setup, width=22, font=self.text_font)
            e.grid(row=i+1, column=0, columnspan=4, pady=3)
            self.entries.append(e)

        tk.Button(self.root, text="Start Group Stage",
                  font=self.text_font,
                  command=self.start_group).pack(pady=10)

        self.info = tk.Label(self.root, text="", fg="white", bg=BG,
                             font=self.header_font)
        self.info.pack(pady=6)

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True)

        self.match_frame = tk.Frame(main, bg=BG)
        self.match_frame.pack(side="left", padx=20)

        self.score_frame = tk.Frame(main, bg=BG)
        self.score_frame.pack(side="right", padx=20)

        nav = tk.Frame(self.root, bg=BG)
        nav.pack(pady=8)

        tk.Button(nav, text="◀ Previous Round",
                  font=self.text_font,
                  command=self.prev_round).pack(side="left", padx=6)

        tk.Button(nav, text="Next Round ▶",
                  font=self.text_font,
                  command=self.next_round).pack(side="left", padx=6)

        self.playoff_btn = tk.Button(
            self.root, text="Start Playoffs",
            font=self.header_font,
            command=self.start_playoffs
        )

    # ---------------- GROUP STAGE ----------------
    def start_group(self):
        self.players = [e.get() for e in self.entries if e.get()]
        if len(self.players) < 4:
            return

        self.current_round = 1
        self.round_results = {1: {p: 0 for p in self.players}}
        self.playoffs_started = False
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
        row = tk.Frame(self.match_frame, bg=BG)
        row.pack(pady=6)

        tk.Label(
            row, text=f"{a} vs {b} (Bo{self.best_of.get()})",
            fg="white", bg=BG, width=30, font=self.text_font
        ).pack(side="left")

        tk.Button(row, text=a, font=self.text_font,
                  command=lambda: self.result(a, b, "A")).pack(side="left", padx=2)
        tk.Button(row, text="Draw", font=self.text_font,
                  command=lambda: self.result(a, b, "D")).pack(side="left", padx=2)
        tk.Button(row, text=b, font=self.text_font,
                  command=lambda: self.result(a, b, "B")).pack(side="left", padx=2)

    def result(self, a, b, res):
        if res == "A":
            self.round_results[self.current_round][a] += WIN
        elif res == "B":
            self.round_results[self.current_round][b] += WIN
        else:
            self.round_results[self.current_round][a] += DRAW
            self.round_results[self.current_round][b] += DRAW

        self.update_scoreboard()

    # ---------------- ROUND NAV ----------------
    def next_round(self):
        if self.current_round >= self.max_rounds.get():
            if not self.playoffs_started:
                self.playoff_btn.pack(pady=10)
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

        tk.Label(self.score_frame, text="SCOREBOARD",
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).grid(row=0, column=0, columnspan=10, pady=6)

        totals = {p: 0 for p in self.players}
        for r in self.round_results.values():
            for p, pts in r.items():
                totals[p] += pts

        sorted_players = sorted(totals.items(), key=lambda x: x[1], reverse=True)

        tk.Label(self.score_frame, text="Player", fg="white", bg=BG,
                 font=self.text_font).grid(row=1, column=0, sticky="w")

        for r in range(1, self.current_round + 1):
            tk.Label(self.score_frame, text=f"R{r}", fg="white", bg=BG,
                     font=self.text_font).grid(row=1, column=r)

        tk.Label(self.score_frame, text="Total", fg="white", bg=BG,
                 font=self.text_font).grid(row=1, column=self.current_round + 1)

        for i, (p, total) in enumerate(sorted_players, start=2):
            tk.Label(self.score_frame, text=p, fg="white", bg=BG,
                     font=self.text_font).grid(row=i, column=0, sticky="w")

            for r in range(1, self.current_round + 1):
                val = self.round_results.get(r, {}).get(p, 0)
                tk.Label(self.score_frame, text=str(val),
                         fg="white", bg=BG,
                         font=self.text_font).grid(row=i, column=r)

            tk.Label(self.score_frame, text=str(total),
                     fg="white", bg=BG,
                     font=self.text_font).grid(row=i, column=self.current_round + 1)

    # ---------------- PLAYOFFS ----------------
    def start_playoffs(self):
        self.playoffs_started = True
        for w in self.match_frame.winfo_children():
            w.destroy()

        totals = {p: 0 for p in self.players}
        for r in self.round_results.values():
            for p, pts in r.items():
                totals[p] += pts

        ranked = [p for p, _ in sorted(totals.items(), key=lambda x: x[1], reverse=True)]

        self.info.config(text="PLAYOFFS")

        self.playoff_match("FINAL", ranked[0], ranked[1])
        self.playoff_match("3RD PLACE", ranked[2], ranked[3])

    def playoff_match(self, title, a, b):
        tk.Label(self.match_frame, text=title,
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).pack(pady=6)

        row = tk.Frame(self.match_frame, bg=BG)
        row.pack(pady=6)

        tk.Label(row, text=f"{a} vs {b}",
                 fg="white", bg=BG,
                 font=self.text_font).pack(side="left", padx=6)

        tk.Button(row, text=a, font=self.text_font,
                  command=lambda: self.info.config(text=f"🏆 WINNER: {a}")).pack(side="left", padx=4)
        tk.Button(row, text=b, font=self.text_font,
                  command=lambda: self.info.config(text=f"🏆 WINNER: {b}")).pack(side="left", padx=4)

# ---------------- RUN ----------------
root = tk.Tk()
app = SealedTournament(root)
root.mainloop()
