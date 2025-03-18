"""
Boids Simulation Package

Ce package contient les classes et fonctions nécessaires pour simuler
le comportement de boids (entités qui se déplacent en groupe) et leur
interaction avec un prédateur.
"""

from .utils import pathRotate
from .boid import Boid
from .predaboid import Predaboid
from .simulation import Simulation
