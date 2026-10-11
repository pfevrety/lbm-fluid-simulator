from simulation.lbm import lbm
import numpy as np
import sys

from gif.visualize_gif import update_visualisation_gif
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from tqdm import tqdm # Barre de progression terminal

from obstacle.grid import generate_obstacle_grid
from obstacle.Formes import *

def initial_conditions(mean_density, width, height, nb_directions, 
                         indices, vit_x, vit_y, weight, v0):
    ux0 = v0 * np.ones((height, width))
    uy0 = np.zeros((height, width))


    populations = np.zeros((height, width, nb_directions))

    # Distribution d'équilibre initiale
    for i, cx, cy, w in zip(indices, vit_x, vit_y, weight):
        cu = cx * ux0 + cy * uy0
        populations[:, :, i] = mean_density * w * (1 + 3*cu + 4.5*cu**2 - 1.5*(ux0**2 + uy0**2))

    density = np.sum(populations, axis=2)
    return populations, density

def simulate_gif(fluide,fluid_vinf,objects,fps=10):
    matplotlib.use("Agg")   # Desactive les fenetres matplotlib
    width = 400 # Résolution selon x
    height = 100 # Résolution selon y
    mean_density = fluide.rho # Densité moyenne (equilibre)
    nb_iterations = 2000
    real_time_plotting = True
    nb_directions = 9 # Nombre de noeuds

    indices = np.arange(nb_directions) # Id des noeuds
    vit_x = [0,0,1,1,1,0,-1,-1,-1] # Coordonnée x des noeuds
    vit_y = [0,1,1,0,-1,-1,-1,0,1] # Coordonnée y des noeuds
    weight = [4/9,1/9,1/36,1/9,1/36,1/9,1/36,1/9,1/36] # weight D2Q9

    fluid_v0 = 0.0 # Vitesse initiale du fluide (statique)
    populations, density = initial_conditions(mean_density, width,height, nb_directions, indices, vit_x, vit_y, weight, fluid_v0)

    obstacle = generate_obstacle_grid(objects, (height, width))
    fig = plt.figure(figsize=(10, 5), dpi=80)
    writer = PillowWriter(fps=fps)

    # Initialisation de la vitesse du fluide
    time_ramp = nb_iterations // 8  # Nombre d'iteration avant la vitesse finale
    
    def start_speed(t):
        """Rampe linéaire : 0 --> fluid_vinf sur la duree de la rampe """
        if t >= time_ramp:
            return fluid_vinf
        return fluid_vinf * (t / time_ramp)

    # Boucle principale
    with writer.saving(fig, "simulation.gif", dpi=80):
        print("Début de la simulation GIF…")
        for iteration in tqdm(range(nb_iterations), desc="Simulation LBM"):
            if not plt.fignum_exists(fig.number):
                print("Simulation stoppée par l'utilisateur")
                return
            # Arrivee de l'air par la gauche et acceleration du fluide
            vin = start_speed(iteration)
            # Noeuds 2, 3 et 4 sont updatés avec l'equilibre de l'arrivée d'air à gauche
            rho_in = density[:, 1]
            for i, cx, cy, w in zip(indices, vit_x, vit_y, weight):
                if cx == 1:  # Directions venant de la gauche
                    cu = cx * vin
                    f_eq = rho_in * w * (1 + 3*cu + 4.5*cu**2 - 1.5*(vin**2))
                    populations[:, 1, i] = f_eq

            populations[:, -1, [6,7,8]] = populations[:, -2, [6,7,8]]

            populations, vitesse_x, vitesse_y, density = lbm(
                populations, indices, vit_x, vit_y, obstacle,
                density, weight
            )

            if (real_time_plotting and (iteration % 15) == 0 and (iteration > time_ramp)) or (iteration == nb_iterations - 1):
                update_visualisation_gif(fig, vitesse_x, vitesse_y, density, obstacle)
                writer.grab_frame()