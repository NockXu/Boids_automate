"""
Fonctions utilitaires pour la simulation de boids.
"""

from __future__ import annotations
import numpy as np
from matplotlib import path

# Forme du boid utilisant path.Path
boid_shape = path.Path(
    # coordonnées du schéma, orienté vers la droite
    vertices=np.array([[0, 0], [-100, 100], [200, 0], [-100, -100], [0, 0]]),
    # 1: moveto, 2: lineto, 79: closepoly
    # https://matplotlib.org/stable/api/path_api.html#matplotlib.path.Path
    codes=np.array([1, 2, 2, 2, 79], dtype=np.uint8),
)

def pathRotate(p: path.Path, angle: float) -> path.Path:
    """
    Rotation d'un path.Path selon un angle donné.

    Args:
        p: path.Path
        angle: angle en radians

    Returns:
        path.Path : nouveau path.Path après rotation
    """
    cos, sin = np.cos(angle), np.sin(angle)
    newpath = p.vertices @ (np.array([[cos, sin], [-sin, cos]]))
    return path.Path(newpath, p.codes)
