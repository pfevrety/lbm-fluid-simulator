import numpy as np
from obstacle.grid import generate_obstacle_grid
from obstacle.Formes import Circle

def test_generate_obstacle_grid():
    c1 = Circle(rayon=3, center=(0, 10), grid=(20, 20))
    final_grid = generate_obstacle_grid(c1, (20, 20))

    assert final_grid.shape == (20, 20)
    assert final_grid.dtype == bool
