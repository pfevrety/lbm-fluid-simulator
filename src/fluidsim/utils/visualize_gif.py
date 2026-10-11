import numpy as np

def update_visualisation_gif(fig, vx, vy, densite, obstacle):
    fig.clf()
    obstacle_mask = obstacle.astype(bool) # Ensure it is boolean
    # Calculate fields (velocity, pressure, vorticity)
    vx = vx.copy()
    vy = vy.copy()
    vx[obstacle_mask] = 0
    vy[obstacle_mask] = 0
    velocity = np.sqrt(vx**2 + vy**2)
    pressure = densite * (1/3)
    vorticity = (np.roll(vx, -1, 0) - np.roll(vx, 1, 0)) - (np.roll(vy, -1, 1) - np.roll(vy, 1, 1))
    velocity = np.ma.array(velocity, mask=obstacle_mask)
    pressure = np.ma.array(pressure, mask=obstacle_mask)
    vorticity = np.ma.array(vorticity, mask=obstacle_mask)
    axes = fig.subplots(2, 2).ravel()

    # velocity
    ax = axes[0]
    vmax = np.nanmax(velocity)
    im = ax.imshow(velocity, cmap="inferno", vmin=0, vmax=vmax)
    ax.imshow(~obstacle_mask, cmap="gray", alpha=0.3)
    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", pad=0.05, fraction=0.046)
    cbar.set_label("Velocity", fontsize=10)
    cbar.set_ticks([])
    ax.set_title("Velocity")

    # pressure
    ax = axes[1]
    pmin, pmax = np.nanmin(pressure), np.nanmax(pressure)
    im = ax.imshow(pressure, cmap="viridis", vmin=pmin, vmax=pmax)
    ax.imshow(~obstacle_mask, cmap="gray", alpha=0.3)
    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", pad=0.05, fraction=0.046)
    cbar.set_label("Pressure", fontsize=10)
    cbar.set_ticks([])
    ax.set_title("Pressure")

    # vorticity
    ax = axes[2]
    vort_abs_max = np.nanmax(np.abs(vorticity))
    im = ax.imshow(vorticity, cmap="bwr", vmin=-vort_abs_max, vmax=vort_abs_max)
    ax.imshow(~obstacle_mask, cmap="gray", alpha=0.3)
    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", pad=0.05, fraction=0.046)
    cbar.set_label("Vorticity", fontsize=10)
    cbar.set_ticks([])
    ax.set_title("Vorticity")

    # Streamlines
    ax = axes[3]
    Y, X = np.mgrid[0:vx.shape[0], 0:vx.shape[1]]
    strm = ax.streamplot(X, Y, vx, vy,
                            color=velocity,
                            density=0.5,
                            cmap="viridis"
                            )
    ax.imshow(~obstacle_mask, cmap="gray", alpha=0.3)
    cbar = fig.colorbar(strm.lines, ax=ax, orientation="horizontal", pad=0.05, fraction=0.046)
    cbar.set_label("Velocity magnitude", fontsize=10)
    cbar.set_ticks([])
    ax.set_title("Streamlines")

    # Matplotlib adjustments
    for ax in axes:
        ax.invert_yaxis()
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
