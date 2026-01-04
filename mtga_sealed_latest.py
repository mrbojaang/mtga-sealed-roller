import random
import tkinter as tk
from tkinter import font
import webbrowser

arena_sets = {
    # Core / Standard / Premier
    "Core Set 2021": "M21",
    "Zendikar Rising": "ZNR",
    "Kaldheim": "KHM",
    "Strixhaven: School of Mages": "STX",
    "Adventures in the Forgotten Realms": "AFR",
    "Innistrad: Midnight Hunt": "MID",
    "Innistrad: Crimson Vow": "VOW",
    "Kamigawa: Neon Dynasty": "NEO",
    "Streets of New Capenna": "SNC",
    "Dominaria United": "DMU",
    "The Brothers’ War": "BRO",
    "Phyrexia: All Will Be One": "ONE",
    "March of the Machine": "MOM",
    "Wilds of Eldraine": "WOE",
    "The Lost Caverns of Ixalan": "LCI",
    "Murders at Karlov Manor": "MKM",
    "Outlaws of Thunder Junction": "OTJ",
    "Bloomburrow": "BLB",
    "Duskmourn: House of Horror": "DSK",

    # Masters / Remastered / Explorer
    "Amonkhet Remastered": "AKR",
    "Kaladesh Remastered": "KLR",
    "Pioneer Masters": "PM",
    "Shadows over Innistrad Remastered": "SIR",
    "Ravnica Remastered": "RVR",
    "Dominaria Remastered": "DMR",
    "Innistrad Remastered": "INR",
    "Khans of Tarkir": "KTK",

    # Modern / Special
    "Modern Horizons 3": "MH3",

    # Universes Beyond
    "Lord of the Rings: Tales of Middle-earth": "LTR",
    "Final Fantasy": "FF",
    "Avatar: The Last Airbender": "ATLA",
}

excluded = set()
reset_clicks = 0
sealed_buttons = []

number_names = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"]

def toggle(lbl, name):
    if name in excluded:
        excluded.remove(name)
        lbl.config(fg="#9fb3c8")
    else:
        excluded.add(name)
        lbl.config(fg="#ff5252")

def clear_sealed_buttons():
    for b in sealed_buttons:
        b.destroy()
    sealed_buttons.clear()

def roll():
    global reset_clicks
    reset_clicks = 0
    clear_sealed_buttons()

    pool = [s for s in arena_sets if s not in excluded]
    if not pool:
        result.config(text="No sets selected")
        return

    chosen = random.choice(pool)
    result.config(text=chosen)

    code = arena_sets[chosen]
    players = player_count.get()

    for i in range(players):
        url = f"https://draftsim.com/draft.php?mode=Sealed_{code}"
        btn = tk.Button(
            sealed_frame,
            text=f"Sealed {number_names[i]}",
            command=lambda u=url: webbrowser.open(u)
        )
        btn.pack(pady=2)
        sealed_buttons.append(btn)

def reset():
    global reset_clicks
    reset_clicks += 1
    result.config(text="ROLL")
    clear_sealed_buttons()

    if reset_clicks >= 2:
        excluded.clear()
        for l in labels:
            l.config(fg="#9fb3c8")
        reset_clicks = 0

root = tk.Tk()
root.title("MTG Arena – Sealed")
root.geometry("700x760")
root.configure(bg="#0b1a23")

title_font = font.Font(size=24, weight="bold")
result_font = font.Font(size=20, weight="bold")
list_font = font.Font(size=10)

tk.Label(root, text="MTG ARENA – SEALED",
         fg="#f5d76e", bg="#0b1a23",
         font=title_font).pack(pady=12)

result = tk.Label(root, text="ROLL",
                  fg="white", bg="#0b1a23",
                  font=result_font)
result.pack(pady=8)

# Player selector
player_frame = tk.Frame(root, bg="#0b1a23")
player_frame.pack(pady=4)

tk.Label(player_frame, text="Players:",
         fg="white", bg="#0b1a23").pack(side="left")

player_count = tk.IntVar(value=2)
tk.OptionMenu(player_frame, player_count, *range(2, 9)).pack(side="left", padx=6)

tk.Button(root, text="🎲",
          font=font.Font(size=36),
          command=roll).pack()

tk.Button(root, text="Reset",
          command=reset).pack(pady=4)

sealed_frame = tk.Frame(root, bg="#0b1a23")
sealed_frame.pack(pady=6)

# --- Centered compact list ---
outer = tk.Frame(root, bg="#0b1a23")
outer.pack(fill="both", expand=True)

list_container = tk.Frame(outer, bg="#0b1a23", width=420)
list_container.pack(pady=10)
list_container.pack_propagate(False)

canvas = tk.Canvas(list_container, bg="#0b1a23",
                   highlightthickness=0, width=420)
scroll = tk.Scrollbar(list_container, orient="vertical",
                      command=canvas.yview)
inner = tk.Frame(canvas, bg="#0b1a23")

inner.bind("<Configure>",
           lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=inner, anchor="nw")
canvas.configure(yscrollcommand=scroll.set)

canvas.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")

labels = []
for s in arena_sets:
    lbl = tk.Label(inner, text=s,
                   fg="#9fb3c8", bg="#0b1a23",
                   font=list_font, cursor="hand2",
                   anchor="w", width=50)
    lbl.pack(pady=0)
    lbl.bind("<Button-1>", lambda e, n=s, l=lbl: toggle(l, n))
    labels.append(lbl)

root.mainloop()
