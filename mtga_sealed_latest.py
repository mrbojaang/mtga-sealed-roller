import tkinter as tk
from tkinter import font
import copy

# ================== KONSTANTER ==================
BG = "#0b1026"
WIN = 3
DRAW = 1

MEDAL_ORDER = {"🥇": 0, "🥈": 1, "🥉": 2, "": 3}
MEDAL_COLOR = {"🥇": "#ffd700", "🥈": "#dcdcdc", "🥉": "#cd7f32", "": "white"}


# ================== APP ==================
class SealedTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Sealed Tournament")
        self.root.geometry("1300x850")
        self.root.configure(bg=BG)

        # -------- DATA --------
        self.players = []
        self.current_round = 1
        self.max_rounds = tk.IntVar(value=3)
        self.best_of_playoff = tk.IntVar(value=1)

        self.round_results = {}
        self.in_playoffs = False
        self.playoff_scores = {}
        self.medals = {}

        self.undo_stack = []

        self.build_ui()

    # ================== UI ==================
    def build_ui(self):
        self.title_font = font.Font(size=26, weight="bold")
        self.header_font = font.Font(size=16, weight="bold")
        self.text_font = font.Font(size=13)
        self.medal_font = font.Font(size=18, weight="bold")

        tk.Label(
            self.root,
            text="MTG SEALED TOURNAMENT",
            fg="#f5d76e",
            bg=BG,
            font=self.title_font
        ).pack(pady=10)

        setup = tk.Frame(self.root, bg=BG)
        setup.pack()

        tk.Label(setup, text="Group rounds:", fg="white", bg=BG)\
            .grid(row=0, column=0)
        tk.OptionMenu(setup, self.max_rounds, 1, 2, 3, 4, 5)\
            .grid(row=0, column=1)

        tk.Label(setup, text="Best of (Playoffs):", fg="white", bg=BG)\
            .grid(row=0, column=2)
        tk.OptionMenu(setup, self.best_of_playoff, 1, 3, 5, 7)\
            .grid(row=0, column=3)

        self.entries = []
        for i in range(8):
            e = tk.Entry(setup, width=24)
            e.grid(row=i + 1, column=0, columnspan=4, pady=2)
            self.entries.append(e)

        tk.Button(
            self.root,
            text="Start Group Stage",
            font=self.text_font,
            command=self.start_group
        ).pack(pady=8)

        self.info = tk.Label(
            self.root,
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

        tk.Button(nav, text="◀ Previous Round", command=self.prev_round)\
            .pack(side="left", padx=5)
        tk.Button(nav, text="Undo", command=self.undo)\
            .pack(side="left", padx=5)
        tk.Button(nav, text="Next Round ▶", command=self.next_round)\
            .pack(side="left", padx=5)

        self.playoff_btn = tk.Button(
            self.root,
            text="Start Playoffs",
            font=self.header_font,
            command=self.start_playoffs
        )

    # ================== UNDO ==================
    def snapshot(self):
        self.undo_stack.append({
            "players": self.players[:],
            "current_round": self.current_round,
            "round_results": copy.deepcopy(self.round_results),
            "in_playoffs": self.in_playoffs,
            "playoff_scores": copy.deepcopy(self.playoff_scores),
            "medals": copy.deepcopy(self.medals)
        })

    def undo(self):
        if not self.undo_stack:
            return
        state = self.undo_stack.pop()
        self.players = state["players"]
        self.current_round = state["current_round"]
        self.round_results = state["round_results"]
        self.in_playoffs = state["in_playoffs"]
        self.playoff_scores = state["playoff_scores"]
        self.medals = state["medals"]
        self.redraw()

    # ================== GROUP ==================
    def start_group(self):
        self.players = [e.get() for e in self.entries if e.get()]
        if len(self.players) < 4:
            return

        self.undo_stack.clear()
        self.in_playoffs = False
        self.current_round = 1
        self.round_results = {1: {p: 0 for p in self.players}}
        self.redraw()

    def redraw(self):
        for frame in (self.match_frame, self.playoff_frame, self.score_frame):
            for w in frame.winfo_children():
                w.destroy()

        if self.in_playoffs:
            self.draw_playoffs()
        else:
            self.draw_group()

    def draw_group(self):
        self.info.config(
            text=f"GROUP STAGE – ROUND {self.current_round}/{self.max_rounds.get()}"
        )

        temp = self.players[:]
        while len(temp) >= 2:
            a = temp.pop(0)
            b = temp.pop(0)
            self.group_match(a, b)

        self.draw_group_scoreboard()

    def group_match(self, a, b):
        row = tk.Frame(self.match_frame, bg=BG)
        row.pack(pady=4)

        tk.Label(row, text=f"{a} vs {b}",
                 fg="white", bg=BG, width=24).pack(side="left")

        tk.Button(row, text=a,
                  command=lambda: self.group_result(a, b, a)).pack(side="left")
        tk.Button(row, text="Draw",
                  command=lambda: self.group_result(a, b, None)).pack(side="left")
        tk.Button(row, text=b,
                  command=lambda: self.group_result(a, b, b)).pack(side="left")

    def group_result(self, a, b, winner):
        self.snapshot()
        if winner == a:
            self.round_results[self.current_round][a] += WIN
        elif winner == b:
            self.round_results[self.current_round][b] += WIN
        else:
            self.round_results[self.current_round][a] += DRAW
            self.round_results[self.current_round][b] += DRAW
        self.draw_group_scoreboard()

    def next_round(self):
        if self.current_round >= self.max_rounds.get():
            self.playoff_btn.pack(pady=8)
            return
        self.snapshot()
        self.current_round += 1
        self.round_results[self.current_round] = {p: 0 for p in self.players}
        self.redraw()

    def prev_round(self):
        if self.current_round <= 1:
            return
        self.snapshot()
        del self.round_results[self.current_round]
        self.current_round -= 1
        self.redraw()

    def draw_group_scoreboard(self):
        for w in self.score_frame.winfo_children():
            w.destroy()

        tk.Label(self.score_frame, text="GROUP SCOREBOARD",
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).pack()

        totals = {
            p: sum(r.get(p, 0) for r in self.round_results.values())
            for p in self.players
        }

        for p, pts in sorted(totals.items(), key=lambda x: x[1], reverse=True):
            tk.Label(self.score_frame, text=f"{p}: {pts}",
                     fg="white", bg=BG,
                     font=self.text_font).pack(anchor="w")

    # ================== PLAYOFF ==================
    def start_playoffs(self):
        self.snapshot()
        self.in_playoffs = True

        totals = {
            p: sum(r.get(p, 0) for r in self.round_results.values())
            for p in self.players
        }
        ranked = sorted(totals, key=totals.get, reverse=True)[:4]

        self.playoff_scores = {p: 0 for p in ranked}
        self.medals = {}
        self.redraw()

    def draw_playoffs(self):
        self.info.config(text="PLAYOFFS")

        p = list(self.playoff_scores.keys())
        self.playoff_match("FINAL", p[0], p[1])
        self.playoff_match("3RD PLACE", p[2], p[3])
        self.draw_playoff_scoreboard()

    def playoff_match(self, title, a, b):
        tk.Label(self.match_frame, text=title,
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).pack(pady=4)

        row = tk.Frame(self.match_frame, bg=BG)
        row.pack(pady=4)

        tk.Label(row, text=f"{a} vs {b}",
                 fg="white", bg=BG).pack(side="left")

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

        self.draw_playoff_scoreboard()

    def draw_playoff_scoreboard(self):
        for w in self.playoff_frame.winfo_children():
            w.destroy()

        tk.Label(self.playoff_frame, text="PLAYOFF SCOREBOARD",
                 fg="#f5d76e", bg=BG,
                 font=self.header_font).pack()

        for p in sorted(self.playoff_scores,
                        key=lambda x: MEDAL_ORDER.get(self.medals.get(x, ""), 3)):
            medal = self.medals.get(p, "")
            tk.Label(
                self.playoff_frame,
                text=f"{medal} {p}",
                fg=MEDAL_COLOR[medal],
                bg=BG,
                font=self.medal_font if medal else self.text_font
            ).pack(anchor="w")


# ================== RUN ==================
if __name__ == "__main__":
    root = tk.Tk()
    app = SealedTournament(root)
    root.mainloop()
