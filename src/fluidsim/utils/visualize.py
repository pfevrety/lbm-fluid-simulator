import numpy as np

def update_visualisation(plt, speed_x, speed_y, density, obstacle, phys_visual):
    fig = plt.gcf()
    fig.clear()
    axe = fig.add_subplot(111)
    
    obstacle_mask = obstacle.astype(bool)  # S'assure que c'est bien booléen
    
    speed_x[obstacle_mask] = 0 # Vitesse x nulle dans l'obstacle
    speed_y[obstacle_mask] = 0 # Vitesse y nulle dans l'obstacle

    phys_visual_function = globals()[phys_visual] # Visualisation physique choisie
    phys_visual_function(fig, axe, speed_x, speed_y, density, obstacle_mask) # Plot de la visualisation
        
    # Ajustements matplotlib
    axe.invert_yaxis()
    axe.get_xaxis().set_visible(False)
    axe.get_yaxis().set_visible(False)
    axe.set_aspect("equal")
    
    plt.pause(0.001)
    return plt


def velocity(fig, axe, speed_x, speed_y, density, obstacle_mask):
    velocity = np.sqrt(speed_x**2 + speed_y**2)

    velocity[obstacle_mask] = np.nan # Masquage dans l'obstacle
    velocity = np.ma.array(velocity, mask=obstacle_mask)

    img = axe.imshow(velocity,cmap="inferno") # Affichage du champ de vitesse
    axe.imshow(~obstacle_mask, cmap="gray", alpha=0.3) # Dessiner l'obstacle gris

    # Ajuster l'échelle des couleurs
    vmax = np.nanmax(velocity)
    img.set_clim(0, vmax)
    
    # Colorbar
    cbar = fig.colorbar(img, ax=axe, orientation="horizontal", pad=0.05, fraction=0.046)
    cbar.set_label("Velocity", fontsize=10)
    cbar.set_ticks([])


def vorticity(fig, axe, speed_x, speed_y, density, obstacle_mask):
    # Calcul de la vorticité 
    vorticity = (np.roll(speed_x, -1, axis=0) - np.roll(speed_x, 1, axis=0)) - (
        np.roll(speed_y, -1, axis=1) - np.roll(speed_y, 1, axis=1)
    )
    
    vorticity[obstacle_mask] = np.nan # Masquage dans l'obstacle
    vorticity = np.ma.array(vorticity, mask=obstacle_mask)
        
    img = axe.imshow(vorticity) # Affichage du champ de vorticité
    axe.imshow(~obstacle_mask, cmap="gray", alpha=0.3) # Dessiner l'obstacle gris
    
    # Ajuster l'échelle des couleurs
    vort_abs_max = np.max(np.abs(vorticity))
    img.set_clim(-vort_abs_max,vort_abs_max)
    
    # Colorbar
    cbar = fig.colorbar(img, ax=axe, orientation="horizontal", pad=0.05, fraction=0.046)
    cbar.set_label("Vorticity", fontsize=10)
    cbar.set_ticks([])


def pressure(fig, axe, speed_x, speed_y, density, obstacle_mask):
    cs2 = 1/3  # Vitesse du son au carre pour la modelisation D2Q9
    pressure = density * cs2  # Modelisation pression D2Q9
    pressure[obstacle_mask] = np.nan  # Masquage dans l'obstacle
    pressure = np.ma.array(pressure, mask=obstacle_mask)
    
    img = axe.imshow(pressure, cmap="viridis")
    axe.imshow(~obstacle_mask, cmap="gray", alpha=0.3)
    
    # Ajuster l'échelle des couleurs
    vmin, vmax = np.nanmin(pressure), np.nanmax(pressure)
    img.set_clim(vmin, vmax)
    
    # Colorbar
    cbar = fig.colorbar(img, ax=axe, orientation="horizontal", pad=0.05, fraction=0.046)
    cbar.set_label("Pressure", fontsize=10)
    cbar.set_ticks([])


def streamlines(fig, axe, speed_x, speed_y, density, obstacle_mask):
    # Masquage dans l'obstacle
    vx, vy = speed_x.copy(), speed_y.copy()

    vx[obstacle_mask] = np.nan
    vy[obstacle_mask] = np.nan

    Y, X = np.mgrid[0:vx.shape[0], 0:vx.shape[1]]
    
    velocity = np.sqrt(vx**2 + vy**2)

    # Streamplot 
    strm = axe.streamplot(
        X, Y, vx, vy,
        density=0.5,           # Densité des lignes (plus il y en a, plus ça rame)
        linewidth=1,            # Epaisseur des lignes
        color=velocity,  # Couleur des lignes = vitesse
        cmap="viridis"
    )
    
    axe.imshow(~obstacle_mask, cmap="gray", alpha=0.3) # Plot de l'obstacle
    
    # Colorbar
    cbar = fig.colorbar(strm.lines, ax=axe, orientation="horizontal", pad=0.05, fraction=0.046)
    cbar.set_label("Velocity magnitude", fontsize=10)
    cbar.set_ticks([])
