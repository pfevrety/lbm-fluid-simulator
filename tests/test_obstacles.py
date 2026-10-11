from obstacle.Formes import Circle, Naca

def test_circle_obstacle_shape():
    circle = Circle(rayon=5, center=(0, 10), grid=(20, 20))
    grid = circle.get_grid()
    assert grid.shape == (20, 20)
    assert grid.dtype == bool

def test_naca_grid_size():
    naca = Naca(0.05, 0.5, 0.1, (50, 100), 10, 30, 0)
    grid = naca.get_grid()
    assert len(grid) == 50
    assert len(grid[0]) == 100
    assert all(isinstance(cell, bool) for row in grid for cell in row)
