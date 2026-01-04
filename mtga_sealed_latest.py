import tkinter as tk
from tkinter import font
import copy

BG = "#0b1026"
WIN = 3
DRAW = 1
MAX_PLAYERS = 8


class SealedTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Sealed Tournament")
        self.root.geometry("1300x850")
        self.root.configure(bg=BG)

        # ---- State ----
        self.players = []
        self.best_of_group = tk.IntVar(value=3)
        self.best_of_playoff = tk.IntVar(value=3)
        self.max_rounds = tk.IntVar(value=3)

        self.current_round = 0
        self.round_results = {}
        self.playoff_scores = {}
        self.in_playoffs = False

        self.undo_stack = []

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        self.title_font = font.Font(size=26, weight="bold")
        self.header_font = font.Font(size=16, weight="bold")
        self.text_font = font.Font(size=13)

        tk.Label(
            self.root,
            text="MTG SEALED TOURNAMENT",
            fg="#f5d76e",
            bg=BG,
            font=self.title_font
        ).pack(pady=12)

        setup = tk.Frame(self.root, bg=BG)
        setup.pack()

        tk.Label(setup, text="Best of (Group):", fg="white", bg=BG,
                 font=self.text_font).grid(row=0, column=0, padx=4)
        tk.OptionMenu(setup, self.best_of_group, 1, 3, 5, 7)\
            .grid(row=0, column=1)

        tk.Label(setup, text="Group rounds:", fg="white", bg=BG,
                 font=self.text_font).grid(row=0, column=2, padx=4)
        tk.OptionMenu(setup, self.max_rounds, 1, 2, 3, 4, 5, 6, 7)\
            .grid(row=0, column=3)

        tk.Label(setup, text="Best of (Playoffs):", fg="white", bg=BG,
                 font=self.text_font).grid(row=0, column=4, padx=4)
        tk.OptionMenu(setup, self.best_of_playoff, 1, 3, 5, 7)\
            .grid(row=0, column=5)

        self.entries = []
        for i in range(MAX_PLAYERS):
            e = tk.Entry(setup, width=22, font=self.text_font)
            e.grid(row=i + 1, column=0, columnspan=6, pady=3)
            self.entries.append(e)

        tk.Button(
            self.root,
            text="Start Group Stage",
            font=self.text_font,
            command=self.start_group
        ).pack(pady=10)

        self.info = tk.Label(
            self.root,
            text="",
            fg="white",
            bg=BG,
            font=self.header_font
        )
        self.info.pack(pady=6)

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True)

        self.match_frame = tk.Frame(main, bg=BG)
        self.match_frame.pack(side="left", padx=20)

        self.playoff_frame = tk.Frame(main, bg=BG)
        self.playoff_frame.pack(side="left", padx=20)

        self.score_frame = tk.Frame(main, bg=BG)
        self.score_frame.pack(side="right", padx=20)

        nav = tk.Frame(self.root, bg=BG)
        nav.pack(pady=10)

        tk.Button(nav, text="◀ Previous Round",
                  font=self.text_font,
                  command=self.prev_round).pack(side="left", padx=6)

        tk.Button(nav, text="Undo",
                  font=self.text_font,
                  command=self.undo).pack(side="left", padx=6)

        tk.Button(nav, text="Next Round ▶",
                  font=self.text_font,
                  command=self.next_round).pack(side="left", padx=6)

        self.playoff_btn = tk.Button(
            self.root,
            text="Start Playoffs",
            font=self.header_font,
            command=self.start_playoffs
        )

    # ---------------- Utilities ----------------
    def snapshot(self):
        self.undo_stack.append({
            "players": self.players[:],
            "current_round": self.current_round,
            "round_results": copy.deepcopy(self.round_results),
            "playoff_scores": copy.deepcopy(self.playoff_scores),
            "in_playoffs": self.in_playoffs
        })

    def undo(self):
        if not self.undo_stack:
            return

        state = self.undo_stack.pop()
        self.players = state["players"]
        self.current_round = state["current_round"]
        self.round_results = state["round_results"]
        self.playoff_scores = state["playoff_scores"]
        self.in_playoffs = state["in_playoffs"]

        if self.in_playoffs:
            self.render_playoffs()
        else:
            self.show_round()

    # ---------------- Group Stage ----------------
    def start_group(self):
        self.players = [e.get() for e in self.entries if e.get()]
        if len(self.players) < 4:
            return

        self.undo_stack.clear()
        self.in_playoffs = False
        self.current_round = 1
        self.round_results = {1: {p: 0 for p in self.players}}
        self.show_round()

    def show_round(self):
        for f in (self.match_frame, self.playoff_frame):
            for w in f.winfo_children():
                w.destroy()

        self.info.config(
            text=f"GROUP STAGE – ROUND {self.current_round}/{self.max_rounds.get()} "
                 f"(Bo{self.best_of_group.get()})"
        )

        temp = self.players[:]
        while len(temp) >= 2:
            a = temp.pop(0)
            b = temp.pop(0)
            self.match_row(a, b)

        self.update_group_scoreboard()

    def match_row(self, a, b):
        row = tk.Frame(self.match_frame, bg=BG)
        row.pack(pady=6)

        tk.Label(row, text=f"{a} vs {b}",
                 fg="white", bg=BG,
                 font=self.text_font,
                 width=28).pack(side="left")

        tk.Button(row, text=a, font=self.text_font,
                  command=lambda: self.result(a, b, "A")).pack(side="left", padx=2)
        tk.Button(row, text="Draw", font=self.text_font,
                  command=lambda: self.result(a, b, "D")).pack(side="left", padx=2)
        tk.Button(row, text=b, font=self.text_font,
                  command=lambda: self.result(a, b, "B")).pack(side="left", padx=2)

    def result(self, a, b, res):
        self.snapshot()

        if res == "A":
            self.round_results[self.current_round][a] += WIN
        elif res == "B":
            self.round_results[self.current_round][b] += WIN
        else:
            self.round_results[self.current_round][a] += DRAW
            self.round_results[self.current_round][b] += DRAW

        self.update_group_scoreboard()

    def next_round(self):
        if self.current_round >= self.max_rounds.get():
            self.playoff_btn.pack(pady=10)
            return

        self.snapshot()
        self.current_round += 1
        if self.current_round not in self.round_results:
            self.round_results[self.current_round] = {p: 0 for p in self.players}
            self.players = self.players[1:] + self.players[:1]

        self.show_round()

    def prev_round(self):
        if self.current_round <= 1:
            return

        self.snapshot()
        del self.round_results[self.current_round]
        self.current_round -= 1
        self.show_round()

    # ---------------- Group Scoreboard ----------------
    def update_group_scoreboard(self):
        for w in self.score_frame.winfo_children():
            w.destroy()

        tk.Label(self.score_frame, text="GROUP SCOREBOARD",
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

    # ---------------- Playoffs ----------------
    def start_playoffs(self):
        self.snapshot()
        self.in_playoffs = True

        for w in self.match_frame.winfo_children():
            w.destroy()
        for w in self.playoff_frame.winfo_children():
            w.destroy()

        totals = {p: 0 for p in self.players}
        for r in self.round_results.values():
            for p, pts in r.items():
                totals[p] += pts

        ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        top4 = [p for p, _ in ranked[:4]]

        self.playoff_scores = {p: 0 for p in top4}

        self.info.config(
            text=f"PLAYOFFS – Best of {self.best_of_playoff.get()}"
        )

        self.update_playoff_scoreboard()

        self.playoff_match("FINAL", top4[0], top4[1])
        self.playoff_match("3RD PLACE", top4[2], top4[3])

    def update_playoff_scoreboard(self):
        for w in self.playoff_frame.winfo_children():
            w.destroy()

        tk.Label(self.playoff_frame, text="PLAYOFF SCOREBOARD",
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).pack(pady=6)

        for p, pts in self.playoff_scores.items():
            tk.Label(self.playoff_frame,
                     text=f"{p}: {pts}",
                     fg="white", bg=BG,
                     font=self.text_font).pack(anchor="w")

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
                  command=lambda: self.playoff_win(a)).pack(side="left", padx=4)
        tk.Button(row, text=b, font=self.text_font,
                  command=lambda: self.playoff_win(b)).pack(side="left", padx=4)

    def playoff_win(self, player):
        self.snapshot()
        self.playoff_scores[player] += 1
        self.update_playoff_scoreboard()


# ---------------- RUN ----------------
root = tk.Tk()
app = SealedTournament(root)
root.mainloop()
