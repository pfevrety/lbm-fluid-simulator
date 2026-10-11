import numpy as np
from simulation.lbm import lbm

def test_lbm_output_shapes():
    Nx, Ny, Q = 20, 10, 9
    populations = np.ones((Ny, Nx, Q))
    densite = np.ones((Ny, Nx))

    obstacle = np.zeros((Ny, Nx), dtype=bool)
    obstacle[5, 5] = True

    indices = range(Q)
    vit_x = [0,0,1,1,1,0,-1,-1,-1]
    vit_y = [0,1,1,0,-1,-1,-1,0,1]
    poids = [4/9,1/9,1/36,1/9,1/36,1/9,1/36,1/9,1/36]

    pop2, vx, vy, rho = lbm(populations, indices, vit_x, vit_y, obstacle, densite, poids)

    assert pop2.shape == populations.shape
    assert vx.shape == (Ny, Nx)
    assert vy.shape == (Ny, Nx)
    assert rho.shape == (Ny, Nx)
