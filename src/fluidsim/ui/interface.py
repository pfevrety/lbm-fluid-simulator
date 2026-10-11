import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

from src.fluidsim.ui.dependencies import (
    start_computing,
    get_all_fluids,
    open_custom_fluid_window,
    fonction_obstacles,
    start_computing_gif
)
from src.fluidsim.fluids.Fluid import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from src.fluidsim.obstacles.grid import generate_obstacle_grid
import matplotlib.pyplot as plt
import numpy as np

##---------------------------------------------------------------------------------------------
FUNCTIONS = ["vorticity", "streamlines", "pressure", "velocity"]
FLUID_DICT = get_all_fluids()
LARGEUR = 400
HAUTEUR = 100

object_specs: List[Dict[str, Any]] = []
GLOBAL_GRID = np.zeros((HAUTEUR, LARGEUR), dtype=bool)

print("Démarrage de l'interface graphique...")

# Main window
root = tk.Tk()
root.title("Simulateur LBM")
root.geometry("1000x750")

ttk.Label(root, text="Simulateur LBM", font=("Arial", 16)).pack(pady=10)

main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=8, pady=8)

left_frame = ttk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=(0,12))

right_frame = ttk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True)

############### Matplotlib Figure (Right Side) -----------------------------------------------------------
fig = Figure(figsize=(7, 3.5), dpi=100)
ax = fig.add_subplot(111)
ax.set_title("Prévisualisation de la grille d’obstacles")
ax.set_aspect("equal")
ax.set_xlim(0, LARGEUR)
ax.set_ylim(0, HAUTEUR)
ax.set_xlabel("X")
ax.set_ylabel("Y")
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().pack(fill="both", expand=True)

############### Controls (Left Side) ------------------------------------------------------------------
# Fluid Choice
ttk.Label(left_frame, text="Choix du fluide:").pack()
fluid_choice = ttk.Combobox(left_frame, values=list(FLUID_DICT.keys()), state="readonly")
fluid_choice.current(0)
fluid_choice.pack(pady=5)

ttk.Button(left_frame, text="Fluide personnalisé",
           command=lambda : open_custom_fluid_window(root, FLUID_DICT, fluid_choice)).pack(pady=10)

# Flow Speed
ttk.Label(left_frame, text="Vitesse à l'infini (vinf):").pack()
flow_speed_entry = ttk.Entry(left_frame)
flow_speed_entry.insert(0, "0.1")
flow_speed_entry.pack(pady=5)

# Object Type
ttk.Label(left_frame, text="Choix de l'objet:").pack()
OBJECT_TYPES = ["Cylindre", "Aile Naca", "Png"]
object_type_choice = ttk.Combobox(left_frame, values=OBJECT_TYPES, state="readonly")
object_type_choice.current(0)
object_type_choice.pack(pady=5)

# Object Name
ttk.Label(left_frame, text="Nom de l'objet:").pack()
object_name_entry = ttk.Entry(left_frame)
object_name_entry.insert(0, "Nom objet")
object_name_entry.pack(pady=5)

# Specific Object Options
object_frame = ttk.Frame(left_frame)
object_frame.pack(pady=10)

# Cylinder Frame
cyl_frame = ttk.Frame(object_frame)
ttk.Label(cyl_frame, text="Rayon:").pack()
cyl_radius_entry = ttk.Entry(cyl_frame)
cyl_radius_entry.insert(0, "12")
cyl_radius_entry.pack()
ttk.Label(cyl_frame, text="Centre X:").pack()
cyl_cx_entry = ttk.Entry(cyl_frame)
cyl_cx_entry.insert(0, "70")
cyl_cx_entry.pack()
ttk.Label(cyl_frame, text="Centre Y:").pack()
cyl_cy_entry = ttk.Entry(cyl_frame)
cyl_cy_entry.insert(0, "50")
cyl_cy_entry.pack()

# NACA Frame
naca_frame = ttk.Frame(object_frame)
ttk.Label(naca_frame, text="Code NACA (ex: 2412):").pack()
naca_code_entry = ttk.Entry(naca_frame)
naca_code_entry.insert(0, "2412")
naca_code_entry.pack()
ttk.Label(naca_frame, text="xmin:").pack()
naca_xmin_entry = ttk.Entry(naca_frame)
naca_xmin_entry.insert(0, "20")
naca_xmin_entry.pack()
ttk.Label(naca_frame, text="Longueur de la corde:").pack()
naca_length_entry = ttk.Entry(naca_frame)
naca_length_entry.insert(0, "80")
naca_length_entry.pack()
ttk.Label(naca_frame, text="Angle d'attaque (en degré):").pack()
naca_angle_entry = ttk.Entry(naca_frame)
naca_angle_entry.insert(0, "10")
naca_angle_entry.pack()

# PNG Frame
png_frame = ttk.Frame(object_frame)
ttk.Label(png_frame, text="xmin:").pack()
png_frame_xmin_entry = ttk.Entry(png_frame)
png_frame_xmin_entry.insert(0, "20")
png_frame_xmin_entry.pack()
ttk.Label(png_frame, text="Longueur de l'image:").pack()
png_frame_length_entry = ttk.Entry(png_frame)
png_frame_length_entry.insert(0, "80")
png_frame_length_entry.pack()

def update_object_frame(e=None):
    for w in object_frame.winfo_children():
        w.pack_forget()
    if object_type_choice.get() == "Cylindre":
        cyl_frame.pack()
    elif object_type_choice.get() == "Aile Naca":
        naca_frame.pack()
    else:
        png_frame.pack()

object_type_choice.bind("<<ComboboxSelected>>", update_object_frame)
update_object_frame()

# Added Objects List
ttk.Label(root, text="Objet(s) ajouté(s):", font=("Arial", 12)).pack()
list_frame = ttk.Frame(left_frame)
list_frame.pack(pady=5, fill="both", expand=True)
object_listbox = tk.Listbox(list_frame, height=1)
object_listbox.pack(side="left", fill="both", expand=True)
scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=object_listbox.yview)
scrollbar.pack(side="right", fill="y")
object_listbox.config(yscrollcommand=scrollbar.set)

def add_object():
    global GLOBAL_GRID
    name = object_name_entry.get().strip()
    if not name:
        name = f"Object_{len(object_specs)+1}"

    if object_type_choice.get() == "Cylindre":
        try:
            r = float(cyl_radius_entry.get())
            cx = int(cyl_cx_entry.get())
            cy = int(cyl_cy_entry.get())
        except:
            print("Paramètres cylindre invalides.")
            return
        object_specs.append({"name": name, "type": "cylinder", "radius": r, "cx": cx, "cy": cy})

    elif object_type_choice.get() == "Aile Naca":
        code = naca_code_entry.get()
        try:
            xmin = int(naca_xmin_entry.get())
            l = int(naca_length_entry.get())
            theta = naca_angle_entry.get()
        except:
            print("Paramètres NACA invalides.")
            return
        object_specs.append({"name": name, "type": "naca", "code": code, "xmin": xmin, "length": l, "angle": theta})

    else:
        try:
            xmin = int(png_frame_xmin_entry.get())
            l = int(png_frame_length_entry.get())
        except:
            print("Objet invalide.")
            return
        object_specs.append({"name": name, "type": "png", "xmin": xmin, "length": l})

    obstacles = fonction_obstacles(object_specs)
    refresh_object_list()
    grille = generate_obstacle_grid(obstacles, (HAUTEUR, LARGEUR))
    GLOBAL_GRID = GLOBAL_GRID + grille
    add_object_to_preview(GLOBAL_GRID)

def add_object_to_preview(grille):
    ax.imshow(grille, origin='lower', cmap="gray_r")
    canvas.draw()

def refresh_object_list():
    object_listbox.delete(0, tk.END)
    for obj in object_specs:
        object_listbox.insert(tk.END, f"{obj['name']}  ({obj['type']})")

ttk.Button(left_frame, text="Ajouter l'objet", command=add_object).pack(pady=10)

# Visualization Mode
ttk.Label(left_frame, text="Mode de visualisation:").pack()
function_choice = ttk.Combobox(left_frame, values=FUNCTIONS, state="readonly")
function_choice.current(0)
function_choice.pack(pady=5)

# Start Simulation
ttk.Button(left_frame, text="Démarrer la simulation",
           command=lambda: start_computing(fluid_choice, flow_speed_entry, function_choice, object_specs, FLUID_DICT)).pack(pady=5)
ttk.Button(left_frame, text="Créer un GIF",
           command=lambda: start_computing_gif(fluid_choice, flow_speed_entry, function_choice, object_specs, FLUID_DICT)).pack(pady=5)

root.mainloop()
