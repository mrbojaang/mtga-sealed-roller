import random
import tkinter as tk
from tkinter import font
import webbrowser
from PIL import Image, ImageTk
import os

WINDOW_W = 740
WINDOW_H = 760

# ================= SET LIST =================

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

# ================= HELPERS =================

def load_background(path, w, h):
    """Load image, scale proportionally and center-crop to window size."""
    img = Image.open(path)
    img_ratio = img.width / img.height
    target_ratio = w / h

    if img_ratio > target_ratio:
        # Image is wider → fit height, crop width
        new_height = h
        new_width = int(h * img_ratio)
    else:
        # Image is taller → fit width, crop height
        new_width = w
        new_height = int(w / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - w) // 2
    top = (new_height - h) // 2
    right = left + w
    bottom = top + h

    return img.crop((left, top, right, bottom))

# ================= STATE =================

excluded = set()
reset_clicks = 0
sealed_buttons = []
number_names = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"]

# ================= LOGIC =================

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

    available = [s for s in arena_sets if s not in excluded]
    if not available:
        result_label.config(text="No sets available")
        return

    chosen = random.choice(available)
    result_label.config(text=chosen)

    code = arena_sets[chosen]
    players = player_count.get()

    for i in range(players):
        url = f"https://draftsim.com/draft.php?mode=Sealed_{code}"
        btn = tk.Button(
            main_frame,
            text=f"Sealed {number_names[i]}",
            command=lambda u=url: webbrowser.open(u)
        )
        btn.pack(pady=2)
        sealed_buttons.append(btn)

def reset():
    global reset_clicks
    reset_clicks += 1
    result_label.config(text="ROLL")
    clear_sealed_buttons()

    if reset_clicks >= 2:
        excluded.clear()
        for lbl in labels:
            lbl.config(fg="#9fb3c8")
        reset_clicks = 0

# ================= UI =================

root = tk.Tk()
root.title("MTG Arena – Sealed")
root.geometry(f"{WINDOW_W}x{WINDOW_H}")
root.resizable(False, False)

# --- BACKGROUND SAFE LOAD ---
if os.path.exists("background.jpg"):
    bg_img = load_background("background.jpg", WINDOW_W, WINDOW_H)
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(x=0, y=0)
else:
    root.configure(bg="#0b1a23")

# --- CONTENT FRAME ---
main_frame = tk.Frame(root, bg="#000000")
main_frame.place(relwidth=1, relheight=1)

title_font = font.Font(size=24, weight="bold")
result_font = font.Font(size=20, weight="bold")
list_font = font.Font(size=10)

tk.Label(main_frame, text="MTG ARENA – SEALED",
         fg="#f5d76e", bg="#000000",
         font=title_font).pack(pady=10)

result_label = tk.Label(main_frame, text="ROLL",
                        fg="white", bg="#000000",
                        font=result_font)
result_label.pack(pady=6)

player_frame = tk.Frame(main_frame, bg="#000000")
player_frame.pack(pady=2)

tk.Label(player_frame, text="Players:", fg="white", bg="#000000").pack(side="left")
player_count = tk.IntVar(value=2)
tk.OptionMenu(player_frame, player_count, *range(2, 9)).pack(side="left", padx=6)

tk.Button(main_frame, text="🎲", font=font.Font(size=36), command=roll).pack(pady=4)
tk.Button(main_frame, text="Reset", command=reset).pack(pady=4)

grid_frame = tk.Frame(main_frame, bg="#000000")
grid_frame.pack(pady=10)

labels = []
columns = 3
row = col = 0

for name in arena_sets:
    lbl = tk.Label(grid_frame, text=name,
                   fg="#9fb3c8", bg="#000000",
                   font=list_font, cursor="hand2",
                   anchor="w", padx=8)
    lbl.grid(row=row, column=col, sticky="w", pady=2)
    lbl.bind("<Button-1>", lambda e, n=name, l=lbl: toggle(l, n))
    labels.append(lbl)

    col += 1
    if col >= columns:
        col = 0
        row += 1

root.mainloop()
