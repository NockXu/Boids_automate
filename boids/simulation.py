"""
Module contenant la classe Simulation pour la simulation de boids.
"""

from __future__ import annotations
import numpy as np
from .boid import Boid, buildBoidCentripete
from .predaboid import Predaboid

class Simulation:
    """
    Classe gérant la simulation de boids et leur interaction avec un prédateur.
    """
    
    def __init__(self: Simulation, n: int, seed: int = 2042) -> None:
        """
        Initialise une nouvelle simulation avec n boids et un prédateur.
        
        Args:
            n: nombre de boids
            seed: graine pour la génération aléatoire
        """
        np.random.seed(seed)

        self.boids = list(buildBoidCentripete() for _ in range(n))
        self.predator = Predaboid()  # Ajouter un predaboid

    def iteration(self: Simulation):
        """
        Effectue une itération de la simulation.
        """
        # Optimisation: éviter de créer une nouvelle liste à chaque itération
        for boid in self.boids:
            boid.interaction(self.boids + [self.predator])
        
        # Predator eats boids
        self.boids = self.predator.eat(self.boids)
        
        # Le predaboid n'interagit qu'avec les boids normaux, pas avec lui-même
        self.predator.interaction(self.boids)
