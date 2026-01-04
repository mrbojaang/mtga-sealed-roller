import tkinter as tk
from tkinter import font

MAX_PLAYERS = 8
WIN_POINTS = 3

class SealedTournament:
    def __init__(self, root):
        self.root = root
        self.root.title("MTG Sealed Tournament")
        self.root.geometry("700x700")
        self.root.configure(bg="#0b1026")

        self.players = []
        self.scores = {}
        self.round = 0
        self.matches = []
        self.playoffs = False
        self.bracket = []

        self.build_ui()

    # ---------- UI ----------
    def build_ui(self):
        title = tk.Label(
            self.root, text="MTG SEALED TOURNAMENT",
            fg="#f5d76e", bg="#0b1026",
            font=font.Font(size=22, weight="bold")
        )
        title.pack(pady=10)

        self.player_frame = tk.Frame(self.root, bg="#0b1026")
        self.player_frame.pack()

        self.player_entries = []
        for i in range(MAX_PLAYERS):
            e = tk.Entry(self.player_frame, width=20)
            e.grid(row=i, column=0, pady=2)
            self.player_entries.append(e)

        tk.Button(
            self.root, text="Start Group Stage",
            command=self.start_group
        ).pack(pady=10)

        self.info = tk.Label(
            self.root, text="",
            fg="white", bg="#0b1026"
        )
        self.info.pack()

        self.match_frame = tk.Frame(self.root, bg="#0b1026")
        self.match_frame.pack(pady=10)

        self.standings = tk.Label(
            self.root, text="",
            fg="white", bg="#0b1026",
            justify="left"
        )
        self.standings.pack(pady=10)

        self.playoff_btn = tk.Button(
            self.root, text="Start Playoffs",
            command=self.start_playoffs
        )

    # ---------- GROUP STAGE ----------
    def start_group(self):
        self.players = [e.get() for e in self.player_entries if e.get()]
        if len(self.players) < 4:
            self.info.config(text="Need at least 4 players")
            return

        self.scores = {p: 0 for p in self.players}
        self.round = 1
        self.generate_round()
        self.info.config(text=f"Group Stage – Round {self.round}")

    def generate_round(self):
        for w in self.match_frame.winfo_children():
            w.destroy()

        self.matches = []
        temp = self.players.copy()

        while len(temp) >= 2:
            a = temp.pop(0)
            b = temp.pop(0)
            self.matches.append((a, b))

        for a, b in self.matches:
            row = tk.Frame(self.match_frame, bg="#0b1026")
            row.pack(pady=2)

            tk.Label(row, text=f"{a} vs {b}", fg="white", bg="#0b1026").pack(side="left")

            tk.Button(row, text=a, command=lambda p=a: self.win(p)).pack(side="left", padx=2)
            tk.Button(row, text=b, command=lambda p=b: self.win(p)).pack(side="left", padx=2)

    def win(self, player):
        self.scores[player] += WIN_POINTS
        self.update_standings()

    def update_standings(self):
        text = "STANDINGS\n"
        for i, (p, s) in enumerate(
            sorted(self.scores.items(), key=lambda x: x[1], reverse=True), 1
        ):
            text += f"{i}. {p} – {s}p\n"
        self.standings.config(text=text)

        self.playoff_btn.pack(pady=10)

    # ---------- PLAYOFFS ----------
    def start_playoffs(self):
        top4 = sorted(self.scores, key=self.scores.get, reverse=True)[:4]
        self.playoffs = True

        for w in self.match_frame.winfo_children():
            w.destroy()

        self.info.config(text="PLAYOFFS – SEMIFINALS")

        semi1 = (top4[0], top4[3])
        semi2 = (top4[1], top4[2])

        self.playoff_match(semi1, "Final")
        self.playoff_match(semi2, "Final")

    def playoff_match(self, match, next_stage):
        a, b = match
        row = tk.Frame(self.match_frame, bg="#0b1026")
        row.pack(pady=4)

        tk.Label(row, text=f"{a} vs {b}", fg="white", bg="#0b1026").pack(side="left")

        tk.Button(row, text=a, command=lambda: self.champion(a)).pack(side="left", padx=4)
        tk.Button(row, text=b, command=lambda: self.champion(b)).pack(side="left", padx=4)

    def champion(self, name):
        self.info.config(text=f"🏆 CHAMPION: {name}")

# ---------- RUN ----------
root = tk.Tk()
app = SealedTournament(root)
root.mainloop()
