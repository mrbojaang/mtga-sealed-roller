import random
import tkinter as tk
from tkinter import font

arena_sets = [
    "Pioneer Masters",
    "Foundations",
    "Duskmourn: House of Horror",
    "Bloomburrow",
    "Modern Horizons 3",
    "Outlaws of Thunder Junction",
    "Murders at Karlov Manor",
    "The Lost Caverns of Ixalan",
    "Wilds of Eldraine",
    "March of the Machine",
    "Phyrexia: All Will Be One",
    "The Brothers' War",
    "Dominaria United",
    "Alchemy Horizons: Baldur's Gate",
    "Streets of New Capenna",
    "Kamigawa: Neon Dynasty",
    "Innistrad: Crimson Vow",
    "Innistrad: Midnight Hunt",
    "D&D: Adventures in the Forgotten Realms",
    "Strixhaven: School of Mages",
    "Kaldheim",
    "Zendikar Rising",
    "Core Set 2021",
    "Ikoria: Lair of Behemoths",
    "Theros Beyond Death",
    "Amonkhet Remastered",
    "Kaladesh Remastered",
    "Shadows Over Innistrad Remastered",
    "Ravnica Remastered",
    "Khans of Tarkir",

    # Nya set
    "Final Fantasy",
    "Avatar: The Last Airbender",
]

excluded = set()
reset_clicks = 0

def toggle(lbl, name):
    if name in excluded:
        excluded.remove(name)
        lbl.config(fg="#9fb3c8")
    else:
        excluded.add(name)
        lbl.config(fg="#ff5252")

def roll():
    global reset_clicks
    reset_clicks = 0
    pool = [s for s in arena_sets if s not in excluded]
    if not pool:
        result.config(text="No sets selected")
        return
    result.config(text=random.choice(pool))

def reset():
    global reset_clicks
    reset_clicks += 1
    result.config(text="ROLL")
    if reset_clicks >= 2:
        excluded.clear()
        for l in labels:
            l.config(fg="#9fb3c8")
        reset_clicks = 0

root = tk.Tk()
root.title("MTG Arena – Sealed")
root.geometry("700x720")
root.configure(bg="#0b1a23")

title_font = font.Font(size=24, weight="bold")
result_font = font.Font(size=20, weight="bold")
list_font = font.Font(size=10)

tk.Label(
    root,
    text="MTG ARENA – SEALED",
    fg="#f5d76e",
    bg="#0b1a23",
    font=title_font
).pack(pady=16)

result = tk.Label(
    root,
    text="ROLL",
    fg="white",
    bg="#0b1a23",
    font=result_font
)
result.pack(pady=14)

tk.Button(
    root,
    text="🎲",
    font=font.Font(size=36),
    command=roll
).pack()

tk.Button(
    root,
    text="Reset",
    command=reset
).pack(pady=6)

# Scrollbar + kompakt lista
frame = tk.Frame(root, bg="#0b1a23")
frame.pack(fill="both", expand=True, padx=20, pady=10)

canvas = tk.Canvas(frame, bg="#0b1a23", highlightthickness=0)
scroll = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
inner = tk.Frame(canvas, bg="#0b1a23")

inner.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=inner, anchor="nw")
canvas.configure(yscrollcommand=scroll.set)

canvas.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")

labels = []
for s in arena_sets:
    lbl = tk.Label(
        inner,
        text=s,
        fg="#9fb3c8",
        bg="#0b1a23",
        font=list_font,
        cursor="hand2"
    )
    lbl.pack(anchor="w", pady=1)  # 👈 kompakt spacing
    lbl.bind("<Button-1>", lambda e, n=s, l=lbl: toggle(l, n))
    labels.append(lbl)

root.mainloop()
