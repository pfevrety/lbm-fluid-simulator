import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

from src.fluidsim.core.simulate import simulate
from src.fluidsim.fluids.Fluid import *
from src.fluidsim.obstacles.Formes import *

from src.fluidsim.utils.simulate_gif import simulate_gif

def get_all_fluids():
    fluid_classes = Fluid.__subclasses__()
    d = {cls.__name__: cls for cls in fluid_classes}
    if "CustomFluid" in d:
        del d["CustomFluid"]
    return d

def open_custom_fluid_window(root, FLUID_DICT, fluid_choice):
    win = tk.Toplevel(root)
    win.title("Custom Fluid")
    win.geometry("350x250")

    ttk.Label(win, text="Définir un fluide personnalisé").pack(pady=10)

    ttk.Label(win, text="Densité:").pack()
    density_entry = ttk.Entry(win)
    density_entry.insert(0, "1.0")
    density_entry.pack(pady=5)

    ttk.Label(win, text="Viscosité:").pack()
    viscosity_entry = ttk.Entry(win)
    viscosity_entry.insert(0, "0.1")
    viscosity_entry.pack(pady=5)

    def save_custom_fluid():
        try:
            density = float(density_entry.get())
            viscosity = float(viscosity_entry.get())
        except ValueError:
            print("Valeurs invalides.")
            return

        FLUID_DICT["CustomFluid"] = lambda: CustomFluid("CustomFluid", density, viscosity)
        fluid_choice["values"] = list(FLUID_DICT.keys())
        fluid_choice.set("CustomFluid")
        win.destroy()

    ttk.Button(win, text="Créer", command=save_custom_fluid).pack(pady=15)

def start_computing_gif(fluid_choice, flow_speed_entry, function_choice, object_specs, FLUID_DICT):
    fluid_name = fluid_choice.get()
    fluid_class = FLUID_DICT.get(fluid_name)
    fluid = fluid_class()

    try:
        flow_speed = float(flow_speed_entry.get())
    except:
        flow_speed = 0.1
        print("Vitesse invalide")

    obstacles = fonction_obstacles(object_specs)
    simulate_gif(fluid, flow_speed, obstacles)

def start_computing(fluid_choice, flow_speed_entry, function_choice, object_specs, FLUID_DICT):
    fluid_name = fluid_choice.get()
    fluid_class = FLUID_DICT.get(fluid_name)
    fluid = fluid_class()

    try:
        flow_speed = float(flow_speed_entry.get())
    except:
        flow_speed = 0.1
        print("Vitesse invalide")

    obstacles = fonction_obstacles(object_specs)
    view_func = function_choice.get()
    simulate(fluid, flow_speed, obstacles, view_func)

def fonction_obstacles(object_specs: List[Dict[str, Any]]):
    width = 400   # Nx
    height = 100  # Ny
    obstacles = []

    for obj in object_specs:
        if obj["type"] == "cylinder":
            r = obj["radius"]
            cx = obj["cx"]
            cy = obj["cy"]
            obstacles.append(Circle(rayon=r, center=(cx, cy), grid_size=(height, width)))
        elif obj["type"] == "naca":
            code = obj["code"]
            try:
                m = int(code[0]) / 100.0
                p = int(code[1]) / 10.0
                t = int(code[2:]) / 100.0
            except:
                print(f"Code Naca invalide")
                m, p, t = 0.02, 0.4, 0.12

            xmin = obj["xmin"]
            length = obj["length"]
            theta = obj["angle"]
            obstacles.append(Naca(m=m, p=p, t=t, grid_size=(height, width), xmin=xmin, length=length, theta=theta))
        elif obj["type"] == "png":
            name = obj["name"]
            xmin = obj["xmin"]
            length = obj["length"]
            obstacles.append(Png(image_name=name, x_min=xmin, length=length, grid_size=(height, width)))
        else:
            raise Exception("Mauvais type d'objet")

    return obstacles
