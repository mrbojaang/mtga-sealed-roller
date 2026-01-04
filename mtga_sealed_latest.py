import tkinter as tk
from tkinter import font
import copy

BG = "#0b1026"
WIN = 3
DRAW = 1
MAX_PLAYERS = 8

MEDAL_ORDER = {"🥇": 0, "🥈": 1, "🥉": 2, "": 3}
MEDAL_COLOR = {"🥇": "#ffd700", "🥈": "#dcdcdc", "🥉": "#cd7f32", "": "white"}


class SealedTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Sealed Tournament")
        self.root.geometry("1300x850")
        self.root.configure(bg=BG)

        self.players = []
        self.best_of_group = tk.IntVar(value=3)
        self.best_of_playoff = tk.IntVar(value=1)
        self.max_rounds = tk.IntVar(value=3)

        self.current_round = 0
        self.round_results = {}

        self.in_playoffs = False
        self.playoff_scores = {}   # match wins
        self.medals = {}

        self.undo_stack = []

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        self.title_font = font.Font(size=26, weight="bold")
        self.header_font = font.Font(size=16, weight="bold")
        self.text_font = font.Font(size=13)
        self.medal_font = font.Font(size=18, weight="bold")

        tk.Label(self.root, text="MTG SEALED TOURNAMENT",
                 fg="#f5d76e", bg=BG,
                 font=self.title_font).pack(pady=12)

        setup = tk.Frame(self.root, bg=BG)
        setup.pack()

        tk.Label(setup, text="Best of (Matches):", fg="white", bg=BG,
                 font=self.text_font).grid(row=0, column=0)
        tk.OptionMenu(setup, self.best_of_group, 1, 3, 5, 7)\
            .grid(row=0, column=1)

        tk.Label(setup, text="Group rounds:", fg="white", bg=BG,
                 font=self.text_font).grid(row=0, column=2)
        tk.OptionMenu(setup, self.max_rounds, 1, 2, 3, 4, 5, 6, 7)\
            .grid(row=0, column=3)

        tk.Label(setup, text="Best of (Playoffs):", fg="white", bg=BG,
                 font=self.text_font).grid(row=0, column=4)
        tk.OptionMenu(setup, self.best_of_playoff, 1, 3, 5, 7)\
            .grid(row=0, column=5)

        self.entries = []
        for i in range(MAX_PLAYERS):
            e = tk.Entry(setup, width=22, font=self.text_font)
            e.grid(row=i + 1, column=0, columnspan=6, pady=3)
            self.entries.append(e)

        tk.Button(self.root, text="Start Group Stage",
                  font=self.text_font,
                  command=self.start_group).pack(pady=10)

        self.info = tk.Label(self.root, text="",
                             fg="white", bg=BG,
                             font=self.header_font)
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
            self.root, text="Start Playoffs",
            font=self.header_font,
            command=self.start_playoffs
        )

    # ---------------- Utilities ----------------
    def snapshot(self):
        self.undo_stack.append(copy.deepcopy(self.__dict__))

    def undo(self):
        if not self.undo_stack:
            return
        state = self.undo_stack.pop()
        self.__dict__.update(state)
        self.redraw()

    def redraw(self):
        if self.in_playoffs:
            self.render_playoffs()
            self.update_playoff_scoreboard()
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
        self.match_frame.destroy()
        self.match_frame = tk.Frame(self.root, bg=BG)
        self.match_frame.pack(side="left", padx=20)

        self.info.config(
            text=f"GROUP STAGE – ROUND {self.current_round}/{self.max_rounds.get()}"
        )

        temp = self.players[:]
        while len(temp) >= 2:
            a = temp.pop(0)
            b = temp.pop(0)
            self.group_match(a, b)

        self.update_group_scoreboard()

    def group_match(self, a, b):
        row = tk.Frame(self.match_frame, bg=BG)
        row.pack(pady=4)

        tk.Label(row, text=f"{a} vs {b}",
                 fg="white", bg=BG,
                 font=self.text_font,
                 width=24).pack(side="left")

        tk.Button(row, text=a,
                  command=lambda: self.group_result(a, b, "A")).pack(side="left")
        tk.Button(row, text="Draw",
                  command=lambda: self.group_result(a, b, "D")).pack(side="left")
        tk.Button(row, text=b,
                  command=lambda: self.group_result(a, b, "B")).pack(side="left")

    def group_result(self, a, b, res):
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
        self.round_results[self.current_round] = {p: 0 for p in self.players}
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
        self.score_frame.destroy()
        self.score_frame = tk.Frame(self.root, bg=BG)
        self.score_frame.pack(side="right", padx=20)

        tk.Label(self.score_frame, text="GROUP SCOREBOARD",
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).pack()

        totals = {
            p: sum(r.get(p, 0) for r in self.round_results.values())
            for p in self.players
        }

        for p, pts in sorted(totals.items(), key=lambda x: x[1], reverse=True):
            tk.Label(self.score_frame,
                     text=f"{p}: {pts}",
                     fg="white", bg=BG,
                     font=self.text_font).pack(anchor="w")

    # ---------------- Playoffs ----------------
    def start_playoffs(self):
        self.snapshot()
        self.in_playoffs = True
        self.medals = {}

        totals = {
            p: sum(r.get(p, 0) for r in self.round_results.values())
            for p in self.players
        }
        ranked = sorted(totals, key=totals.get, reverse=True)[:4]

        self.playoff_scores = {p: 0 for p in ranked}
        self.render_playoffs()
        self.update_playoff_scoreboard()

    def render_playoffs(self):
        self.match_frame.destroy()
        self.match_frame = tk.Frame(self.root, bg=BG)
        self.match_frame.pack(side="left", padx=20)

        p = list(self.playoff_scores.keys())
        self.playoff_match("FINAL", p[0], p[1])
        self.playoff_match("3RD PLACE", p[2], p[3])

    def playoff_match(self, title, a, b):
        tk.Label(self.match_frame, text=title,
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).pack(pady=4)

        row = tk.Frame(self.match_frame, bg=BG)
        row.pack(pady=4)

        tk.Label(row, text=f"{a} vs {b}",
                 fg="white", bg=BG,
                 font=self.text_font).pack(side="left")

        tk.Button(row, text=a,
                  command=lambda: self.playoff_result(title, a, b)).pack(side="left")
        tk.Button(row, text=b,
                  command=lambda: self.playoff_result(title, b, a)).pack(side="left")

    def playoff_result(self, match, winner, loser):
        self.snapshot()
        self.playoff_scores[winner] += 1

        needed = self.best_of_playoff.get() // 2 + 1
        if self.playoff_scores[winner] >= needed:
            if match == "FINAL":
                self.medals[winner] = "🥇"
                self.medals[loser] = "🥈"
            else:
                self.medals[winner] = "🥉"

        self.update_playoff_scoreboard()

    def update_playoff_scoreboard(self):
        self.playoff_frame.destroy()
        self.playoff_frame = tk.Frame(self.root, bg=BG)
        self.playoff_frame.pack(side="left", padx=20)

        tk.Label(self.playoff_frame, text="PLAYOFF SCOREBOARD",
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).pack()

        players = sorted(
            self.playoff_scores.keys(),
            key=lambda p: MEDAL_ORDER.get(self.medals.get(p, ""), 3)
        )

        for p in players:
            medal = self.medals.get(p, "")
            tk.Label(self.playoff_frame,
                     text=f"{medal} {p}",
                     fg=MEDAL_COLOR[medal],
                     bg=BG,
                     font=self.medal_font if medal else self.text_font)\
                .pack(anchor="w")


# ---------------- RUN ----------------
root = tk.Tk()
app = SealedTournament(root)
root.mainloop()
