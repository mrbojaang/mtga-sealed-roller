import random
import tkinter as tk
from tkinter import font
import webbrowser
import os

WINDOW_W = 740
WINDOW_H = 760

arena_sets = {
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
    "Amonkhet Remastered": "AKR",
    "Kaladesh Remastered": "KLR",
    "Pioneer Masters": "PM",
    "Shadows over Innistrad Remastered": "SIR",
    "Ravnica Remastered": "RVR",
    "Dominaria Remastered": "DMR",
    "Innistrad Remastered": "INR",
    "Khans of Tarkir": "KTK",
    "Modern Horizons 3": "MH3",
    "Lord of the Rings: Tales of Middle-earth": "LTR",
    "Final Fantasy": "FF",
    "Avatar: The Last Airbender": "ATLA",
}

excluded = set()
reset_clicks = 0
sealed_buttons = []
number_names = ["One","Two","Three","Four","Five","Six","Seven","Eight"]

def toggle(label, name):
    if name in excluded:
        excluded.remove(name)
        label.config(fg="#9fb3c8")
    else:
        excluded.add(name)
        label.config(fg="#ff5252")

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
        result_label.config(text="No sets available")
        return

    chosen = random.choice(pool)
    result_label.config(text=chosen)

    code = arena_sets[chosen]
    players = player_count.get()

    for i in range(players):
        r = i // 2
        c = i % 2
        url = f"https://draftsim.com/draft.php?mode=Sealed_{code}"
        btn = tk.Button(
            sealed_frame,
            text=f"Sealed {number_names[i]}",
            width=14,
            command=lambda u=url: webbrowser.open(u)
        )
        btn.grid(row=r, column=c, padx=6, pady=4)
        sealed_buttons.append(btn)

def reset():
    global reset_clicks
    reset_clicks += 1
    result_label.config(text="ROLL")
    clear_sealed_buttons()
    if reset_clicks >= 2:
        excluded.clear()
        for l in labels:
            l.config(fg="#9fb3c8")
        reset_clicks = 0

# ================= UI =================

root = tk.Tk()
root.title("MTG Arena – Sealed")
root.geometry(f"{WINDOW_W}x{WINDOW_H}")
root.resizable(False, False)

# BACKGROUND
if os.path.exists("background.png"):
    bg_img = tk.PhotoImage(file="background.png")
    bg_label = tk.Label(root, image=bg_img)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# MAIN FRAME (transparent)
main_frame = tk.Frame(root)
main_frame.place(relwidth=1, relheight=1)

title_font = font.Font(size=24, weight="bold")
result_font = font.Font(size=20, weight="bold")
list_font = font.Font(size=10)

tk.Label(main_frame, text="MTG ARENA – SEALED",
         fg="#f5d76e", font=title_font).pack(pady=10)

result_label = tk.Label(main_frame, text="ROLL",
                        fg="white", font=result_font)
result_label.pack(pady=6)

player_frame = tk.Frame(main_frame)
player_frame.pack(pady=2)

tk.Label(player_frame, text="Players:", fg="white").pack(side="left")
player_count = tk.IntVar(value=2)
tk.OptionMenu(player_frame, player_count, *range(2,9)).pack(side="left", padx=6)

tk.Button(main_frame, text="🎲", font=font.Font(size=36),
          command=roll).pack(pady=4)
tk.Button(main_frame, text="Reset", command=reset).pack(pady=4)

sealed_frame = tk.Frame(main_frame)
sealed_frame.pack(pady=8)

grid_frame = tk.Frame(main_frame)
grid_frame.pack(pady=10)

labels = []
row = col = 0
for name in arena_sets:
    lbl = tk.Label(grid_frame, text=name,
                   fg="#9fb3c8", font=list_font,
                   cursor="hand2", anchor="w", padx=8)
    lbl.grid(row=row, column=col, sticky="w", pady=2)
    lbl.bind("<Button-1>", lambda e,n=name,l=lbl: toggle(l,n))
    labels.append(lbl)
    col += 1
    if col >= 3:
        col = 0
        row += 1

root.mainloop()
