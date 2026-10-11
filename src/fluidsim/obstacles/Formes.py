import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from abc import ABC, abstractmethod
from typing import Tuple, Optional

class Obstacle(ABC):
    """Abstract base class for all simulation obstacles."""
    def __init__(self, grid_size: Tuple[int, int]):
        self.grid_size = grid_size # (height, width)
        self.obstacle_map = np.zeros(grid_size, dtype=bool)

    @abstractmethod
    def generate_mask(self) -> None:
        """Generates the boolean mask for the obstacle."""
        pass

    def get_grid(self) -> np.ndarray:
        """Returns the generated boolean grid."""
        return self.obstacle_map

    def plot(self) -> None:
        """Displays the obstacle in a matplotlib window."""
        grid = self.get_grid()
        plt.figure(figsize=(6, 6))
        plt.imshow(grid, origin='lower', cmap='gray_r')
        plt.title(f"{self.__class__.__name__} Obstacle")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid(False)
        plt.show()

class Circle(Obstacle):
    def __init__(self, rayon: float, center: Tuple[float, float], grid_size: Tuple[int, int]):
        super().__init__(grid_size)
        self.rayon = rayon
        self.center = center
        self.generate_mask()

    def generate_mask(self) -> None:
        h, w = self.grid_size
        x = np.arange(w) - (w - 1) / 2
        y = np.arange(h)
        X, Y = np.meshgrid(x, y)
        cx, cy = self.center
        self.obstacle_map = (X - cx)**2 + (Y - cy)**2 < self.rayon**2

class Naca(Obstacle):
    def __init__(self, m: float, p: float, t: float, grid_size: Tuple[int, int], xmin: int, length: int, theta: float):
        super().__init__(grid_size)
        self.m, self.p, self.t = m, p, t
        self.xmin, self.length = xmin, length
        self.theta = theta
        self.generate_mask()

    def fYt(self, X: np.ndarray, t: float) -> np.ndarray:
        return 5*t*(0.2969*np.sqrt(X) - 0.1260*X - 0.3516*X**2 + 0.2843*X**3 - 0.1036*X**4)

    def fYc(self, X: np.ndarray, m: float, p: float) -> np.ndarray:
        return np.where(X <= p,
                      m * (2*p*X - X**2) / p**2,
                      m * ((1-2*p) + 2*p*X - X**2) / (1-p)**2)

    def generate_mask(self) -> None:
        h, w = self.grid_size
        X_naca = np.linspace(0, 1, self.length)
        Yc = self.fYc(X_naca, self.m, self.p)
        Yt = self.fYt(X_naca, self.t)
        Y_top = np.round(h//2 + self.length * (Yc + Yt)).astype(int)
        Y_bottom = np.round(h//2 + self.length * (Yc - Yt)).astype(int)

        temp_mask = np.zeros((h, w), dtype=bool)
        for x in range(self.length):
            x_idx = self.xmin + x
            if 0 <= x_idx < w:
                y_min = max(0, Y_bottom[x])
                y_max = min(h-1, Y_top[x])
                temp_mask[y_min:y_max+1, x_idx] = True

        angle_rad = np.radians(self.theta)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)
        cx = self.xmin + self.length // 2
        cy = h // 2
        x_grid = np.arange(w) - cx
        y_grid = np.arange(h) - cy
        X, Y = np.meshgrid(x_grid, y_grid)
        X_old = cos_a * X + sin_a * Y
        Y_old = -sin_a * X + cos_a * Y
        abs_X_old = np.round(X_old + cx).astype(int)
        abs_Y_old = np.round(Y_old + cy).astype(int)
        valid = (abs_X_old >= 0) & (abs_X_old < w) & (abs_Y_old >= 0) & (abs_Y_old < h)
        self.obstacle_map = np.zeros((h, w), dtype=bool)
        self.obstacle_map[valid] = temp_mask[abs_Y_old[valid], abs_X_old[valid]]

class Png(Obstacle):
    def __init__(self, image_name: str, x_min: int, length: int, grid_size: Tuple[int, int]):
        super().__init__(grid_size)
        self.image_name = image_name
        self.x_min = x_min
        self.length = length
        self.generate_mask()

    def generate_mask(self) -> None:
        h, w = self.grid_size
        try:
            with Image.open(f"./assets/{self.image_name}.png") as im:
                im = im.convert("RGBA")
                im.thumbnail((w, self.length), Image.Resampling.LANCZOS)
                image_array = np.array(im)
                binary_grid = image_array[:, :, 3] != 0
                binary_grid = np.flipud(binary_grid)
                img_h, img_w = binary_grid.shape
                y_offset = (h - img_h) // 2
                x_offset = self.x_min
                y_start, y_end = max(0, y_offset), min(h, y_offset + img_h)
                x_start, x_end = max(0, x_offset), min(w, x_offset + img_w)
                img_y_start, img_y_end = max(0, -y_offset), img_h - max(0, (y_offset + img_h) - h)
                img_x_start, img_x_end = max(0, -x_offset), img_w - max(0, (x_offset + img_w) - w)
                self.obstacle_map[y_start:y_end, x_start:x_end] = \
                    binary_grid[img_y_start:img_y_end, img_x_start:img_x_end]
        except FileNotFoundError:
            print(f"Error: File {self.image_name}.png not found in assets/")
