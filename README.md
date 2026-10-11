# Fluid Simulation using Lattice Boltzmann Method (LBM)

A professional-grade 2D fluid dynamics simulator implemented in Python. This project uses the Lattice Boltzmann Method (LBM) to simulate fluid flow around various obstacles, providing real-time visualization of velocity fields, vorticity, and pressure.

## Features

- **High-Performance Core**: Fully vectorized LBM engine using NumPy for efficient streaming and collision steps (BGK approximation).
- **Dynamic Obstacle System**: 
  - **Geometric Shapes**: Support for cylinders and NACA airfoil profiles.
  - **Image-based Obstacles**: Load any `.png` image from the `assets/` folder to use as a fluid obstacle (automatic alpha-channel masking).
  - **Customizable Physics**: Define custom fluids by specifying density ($\rho$) and dynamic viscosity ($\mu$).
- **Interactive UI**: A Tkinter-based launcher to configure simulation parameters, add multiple obstacles, and choose visualization modes.
- **Visualization Suite**:
  - Real-time plotting of velocity and density fields.
  - Generation of high-quality GIFs for simulation results.
  - Support for vorticity and streamlines analysis.

## Technical Architecture

The project follows a modular package structure:
- `src/fluidsim/core`: The LBM solver and simulation loop.
- `src/fluidsim/obstacles`: Geometric logic for mask generation (Circle, NACA, PNG).
- `src/fluidsim/fluids`: Management of physical fluid properties.
- `src/fluidsim/ui`: Interface and configuration layer.
- `src/fluidsim/utils`: Visualization and animation tools.

### Mathematical Foundation
The simulation implements the **D2Q9** (2 Dimensions, 9 Velocities) model. The core process follows three main steps:
1. **Streaming**: Particles move to neighboring cells based on their velocity vectors.
2. **Collision**: Distributions relax toward a local equilibrium using the BGK operator: 
   $f_i(\mathbf{x}, t+\Delta t) = f_i(\mathbf{x}, t) - \frac{1}{\tau}(f_i - f_i^{eq})$
3. **Bounce-Back**: No-slip boundary conditions are enforced at obstacle interfaces.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/fluidsimulation.git
   cd fluidsimulation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the simulator:
   ```bash
   python main.py
   ```

## Usage Guide

1. **Fluid Selection**: Choose a pre-defined fluid (Air, Water, Honey, etc.) or create a custom one.
2. **Configure Flow**: Set the inlet velocity ($v_{\infty}$). *Note: Keep values between 0.05 and 0.2 for numerical stability.*
3. **Add Obstacles**:
   - **Cylinder**: Define radius and position.
   - **NACA Airfoil**: Enter a 4-digit NACA code (e.g., `2412`), position, length, and angle of attack.
   - **PNG**: Enter the name of a file in `assets/` (e.g., `cybertruck`).
4. **Visualize**: Select the desired field (vorticity, pressure, etc.) and click **"Démarrer la simulation"**.
5. **Export**: Use **"Créer un GIF"** to save the simulation as an animation.

## Future Improvements
- [ ] Implementation of Multi-grid/Adaptive Mesh Refinement (AMR).
- [ ] Addition of Thermal LBM for heat transfer simulation.
- [ ] Integration with GPU acceleration via CuPy.

---
*This project was developed as part of an academic course at CentraleSupélec.
