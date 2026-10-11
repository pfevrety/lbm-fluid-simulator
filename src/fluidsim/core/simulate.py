import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.fluidsim.core.lbm import lbm
import numpy as np
import sys

from src.fluidsim.utils.visualize import update_visualisation
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from src.fluidsim.obstacles.grid import generate_obstacle_grid
from src.fluidsim.obstacles.Formes import *


def initial_conditions(mean_density, width, height, nb_directions, indices, vit_x, vit_y, weight, v0):
    ux0 = v0 * np.ones((height, width))
    uy0 = np.zeros((height, width))

    populations = np.zeros((height, width, nb_directions))

    # Initial equilibrium distribution
    for i, cx, cy, w in zip(indices, vit_x, vit_y, weight):
        cu = cx * ux0 + cy * uy0
        populations[:, :, i] = mean_density * w * (1 + 3*cu + 4.5*cu**2 - 1.5*(ux0**2 + uy0**2))

    density = np.sum(populations, axis=2)
    return populations, density


def simulate(fluide, fluid_vinf, objects, phys_visual):
    width = 400 # Resolution along x
    height = 100 # Resolution along y
    mean_density = fluide.rho # Average density (equilibrium)
    nb_iterations = 4000
    real_time_plotting = True
    nb_directions = 9 # Number of lattice nodes

    # D2Q9 Modeling with BGK approximation
    # Convention:
    # e8(-1, 1)     e1( 0, 1)      e2( 1, 1)
    #          \         |        /
    #           \        |       /
    #            \       |      /
    #             \      |     /
    # e7(-1, 0) <-- e0( 0, 0) --> e3( 1, 0)
    #             /      |     \
    #            /       |      \
    #           /        |       \
    #          /         |        \
    # e6(-1,-1)     e5( 0,-1)     e4( 1, -1)
    #
    # Distribution functions: f0, f1, f2, f3, f4, f5, f6, f7, f8
    # Velocities: c(0,0), c(0,1), c(1,1), c(1,0), c(1,-1), c(0,-1), c(-1,-1), c(-1,0), c(-1,1)
    # weights: 4/9, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36
    indices = np.arange(nb_directions) # Node IDs
    vit_x = [0,0,1,1,1,0,-1,-1,-1] # X-coordinates of nodes
    vit_y = [0,1,1,0,-1,-1,-1,0,1] # Y-coordinates of nodes
    weight = [4/9,1/9,1/36,1/9,1/36,1/9,1/36,1/9,1/36] # D2Q9 weights

    fluid_v0 = 0.0 # Initial fluid velocity (static)
    populations, density = initial_conditions(mean_density, width, height, nb_directions, indices, vit_x, vit_y, weight, fluid_v0)

    obstacle = generate_obstacle_grid(objects, (height, width))

    plt.ion() # Interactive mode for real-time display
    fig=plt.figure(figsize=(4, 2), dpi=80)

    # Fluid velocity initialization
    time_ramp = nb_iterations // 8  # Iterations before final speed is reached

    def start_speed(t):
        """Linear ramp: 0 --> fluid_vinf over the ramp duration """
        if t >= time_ramp:
            return fluid_vinf
        return fluid_vinf * (t / time_ramp)

    # Main simulation loop
    for iteration in range(nb_iterations):

        if not plt.fignum_exists(fig.number):
            print("Simulation stopped by the user")
            return
       # Inlet flow from the left with density regulation
        vin = start_speed(iteration)

        # Inlet: impose velocity + equilibrium density
        rho_in = mean_density  # Force constant density at inlet

        # Vectorized Inlet implementation
        inlet_dirs = [i for i, vx in enumerate(vit_x) if vx == 1]
        for i in inlet_dirs:
            cu = vit_x[i] * vin
            f_eq = rho_in * weight[i] * (1 + 3*cu + 4.5*cu**2 - 1.5*(vin**2))
            populations[:, 0, i] = f_eq

        # LBM Update
        populations, velocity_x, velocity_y, density = lbm(
            populations,
            np.array(indices),
            np.array(vit_x),
            np.array(vit_y),
            obstacle,
            density,
            np.array(weight)
        )

        # Outlet: extrapolation + force same density as inlet
        populations[:, -1, :] = populations[:, -2, :]
        density[:, -1] = mean_density  # Critical: maintain mass balance

        # Visualization
        if (real_time_plotting and (iteration % 10) == 0) or (iteration == nb_iterations - 1):
            update_visualisation(plt, velocity_x, velocity_y, density, obstacle, phys_visual)
            plt.pause(0.001)

    plt.show()
