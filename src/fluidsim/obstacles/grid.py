import numpy as np

def generate_obstacle_grid(obstacles, grid_size):
    largeur, hauteur = grid_size

    grille = np.zeros((largeur, hauteur), dtype=bool)

    if not isinstance(obstacles, (list, tuple)):
        obstacles = [obstacles]

    for obs in obstacles:
        grille = grille | obs.get_grid()
    
    return grille
