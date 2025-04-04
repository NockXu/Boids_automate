"""
Module contenant la classe Predaboid pour la simulation de boids.
"""

from __future__ import annotations
import numpy as np
from .boid import Boid

class Predaboid(Boid):
    """
    Classe représentant un prédateur de boids.
    Le predaboid chasse et mange les boids normaux.
    """
    
    def __init__(self, position=None, vitesse=None):
        """
        Initialise un nouveau predaboid.
        
        Args:
            position: position initiale (aléatoire si None)
            vitesse: vitesse initiale (aléatoire si None)
        """
        super().__init__(position, vitesse)
        self.eating_range = 20  # Rayon dans lequel le prédateur peut manger les boids
        self.boostValue: float = 1.2  # Vitesse de base plus élevée

    def eat(self, population: list[Boid]) -> list[Boid]:
        """
        Mange les boids qui sont dans le rayon d'action du prédateur.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            list[Boid]: liste des boids restants après que le prédateur ait mangé
        """
        new_population = []
        for boid in population:
            if self.distance(boid) > self.eating_range:
                new_population.append(boid)
        return new_population
        
    def flee_predator(self, population: list[Boid]):
        """
        Surcharge de la méthode flee_predator pour que le predaboid ne se fuie pas lui-même.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            np.ndarray: vecteur nul (le predaboid ne fuit pas)
        """
        # Le predaboid ne fuit pas les autres predaboids
        return np.zeros(2)
        
    def separation(self, population: list[Boid]):
        """
        Surcharge de la méthode separation pour que le predaboid n'utilise pas la force de séparation.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            np.ndarray: vecteur nul (pas de séparation)
        """
        # Le predaboid n'utilise pas la force de séparation
        return np.zeros(2)
        
    def move(self: Boid) -> None:
        """
        Déplace le predaboid en fonction de sa vitesse.
        Le predaboid ne peut pas boost mais a une vitesse de base plus élevée.
        """
        # Le Predaboid ne peut pas boost mais a une vitesse de base plus élevée
        self.x += self.dx * self.boostValue
