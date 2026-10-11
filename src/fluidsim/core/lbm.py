import numpy as np
from typing import Tuple, Any

def lbm(
    populations: np.ndarray,
    indices: np.ndarray,
    vit_x: np.ndarray,
    vit_y: np.ndarray,
    obstacle: np.ndarray,
    densite: np.ndarray,
    poids: np.ndarray,
    tau: float = 1.0
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Performs one iteration of the Lattice Boltzmann Method (D2Q9).

    Args:
        populations: Distribution functions array (height, width, 9)
        indices: Direction indices
        vit_x: X-components of lattice velocities
        vit_y: Y-components of lattice velocities
        obstacle: Boolean mask of obstacles
        densite: Current density field
        poids: Lattice weights
        tau: Relaxation time

    Returns:
        Updated populations, velocity_x, velocity_y, and density.
    """
    # 1. Streaming step (Vectorized roll for each direction)
    for i in range(len(indices)):
        populations[:, :, i] = np.roll(
            np.roll(populations[:, :, i], vit_x[i], axis=1),
            vit_y[i], axis=0
        )

    # 2. Boundary Condition: Bounce-back on obstacles
    # Reverses the directions for cells inside obstacles
    # Mapping: [0,1,2,3,4,5,6,7,8] -> [0,5,4,6,2,8,3,7,1] (Approximate reversal based on D2Q9 logic)
    # The user's original reversal was [0,5,6,7,8,1,2,3,4]
    bounce_indices = [0, 5, 6, 7, 8, 1, 2, 3, 4]
    populations[obstacle, :] = populations[obstacle, :][:, bounce_indices]

    # 3. Macroscopic variables
    densite[:] = np.sum(populations, axis=2)
    # Avoid division by zero
    safe_densite = np.where(densite == 0, 1.0, densite)

    # Vectorized velocity calculation: sum(f_i * c_i) / rho
    vitesse_x = np.sum(populations * vit_x, axis=2) / safe_densite
    vitesse_y = np.sum(populations * vit_y, axis=2) / safe_densite

    # No velocity inside obstacles
    vitesse_x[obstacle] = 0.0
    vitesse_y[obstacle] = 0.0

    # 4. Collision step (BGK Approximation - Fully Vectorized)
    # pre-calculate common terms to avoid redundant computation
    v_sq = vitesse_x**2 + vitesse_y**2

    # We calculate equilibrium for all 9 directions at once using broadcasting
    # vit_x/y are (9,), vitesse_x/y are (H, W)
    # cu result: (H, W, 9)
    cu = vit_x * vitesse_x[..., np.newaxis] + vit_y * vitesse_y[..., np.newaxis]

    equilibrium = densite[..., np.newaxis] * poids * (
        1 + 3*cu + 4.5*cu**2 - 1.5*v_sq[..., np.newaxis]
    )

    # Update populations: f_new = f_old - (f_old - f_eq)/tau
    populations -= (populations - equilibrium) / tau

    return populations, vitesse_x, vitesse_y, densite
