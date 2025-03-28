# -*- coding: utf-8 -*-
"""R4_12_boids_2024_0_soluce.py

# R4.12 : Boids
---

BUT 1 Info : parcours A

BUT INFO Calais

auteur : Rémi Cozot (remi.cozot@univ-littoral.fr), date : août 2024


---
L'installation de ffmpeg est nécessaire pour la sauvegarde :
https://www.gyan.dev/ffmpeg/builds/

"""


from __future__ import annotations
from typing import TypeAlias, Callable

import numpy as np
import pygame
from matplotlib import path

# a adapter en fonction de votre installation de ffmpeg

# boids shape using path.Path
boid_shape = path.Path(
    # coordonnées du schéma ci-dessous, orienté vers la droite
    vertices=np.array([[0, 0], [-100, 100], [200, 0], [-100, -100], [0, 0]]),
    # 1: moveto, 2: lineto, 79: closepoly
    # https://matplotlib.org/stable/api/path_api.html#matplotlib.path.Path
    codes=np.array([1, 2, 2, 2, 79], dtype=np.uint8),
)
# ------------------------------------------------------------------------------
# fonctions
# ------------------------------------------------------------------------------
def pathRotate(p: path.Path, angle: float) -> path.Path:
    """
      rotate path.Path by angle$

      Args:
        p: path.Path
        angle: radians

      Returns:

        path.Path : return new path.Path
    """
    cos, sin = np.cos(angle), np.sin(angle)
    newpath = p.vertices @ (np.array([[cos, sin], [-sin, cos]]))
    return path.Path(newpath, p.codes)

# ------------------------------------------------------------------------------
# classes
# ------------------------------------------------------------------------------
class Boid:

    # attributs de classe
    # taille du cadre
    taille : int = 300
    # nombre de voisins à considérer
    max_voisins :int = 10

    # attributs des boids
    maXVitesse : int = 10
    maxBoostValue : float = 3

    # constructeur
    def __init__(self: Boid, position=None, vitesse=None) -> None:
        self.x = (
            position
            if position is not None
            else np.random.uniform(-Boid.taille, Boid.taille, 2)
        )
        self.dx = (
            vitesse if vitesse is not None else np.random.uniform(-5, 5, 2)
        )
        # liste des fonctions d'interaction non incluse dans la classe et le poid associé
        self.interactions : list[tuple[funInteraction, float]] = []

        # Permet de savoir si le boid est sous l'effet d'un boost
        self.boost : bool = False
        # Initialise la puissance du boost
        self.boostValue : float = Boid.maxBoostValue
        
        # Cache pour stocker les voisins calculés
        self._voisins_cache = {}
        # Cache pour stocker les distances calculées
        self._distances_cache = {}

    # methodes

    def add_interaction(self: Boid, fun: funInteraction, poids: float) -> None:
        "Ajoute une fonction d'interaction à la liste des interactions."
        self.interactions.append((fun, poids))

    def __repr__(self: Boid) -> str:
        return f"<Boid({self.x.round(2)}, {self.dx.round(2)})>"

    # getter et setter
    @property
    def vitesse(self: Boid) -> float:
        return np.linalg.norm(self.dx)

    @vitesse.setter
    def vitesse(self: Boid, value: float) -> None:
        self.dx = self.dx * value / self.vitesse

    @property
    def direction(self: Boid) -> float:
        return np.arctan2(self.dx[1], self.dx[0])

    # autres methodes
    def distance(self: Boid, other: Boid) -> float:
        "Renvoie la distance entre deux Boids."
        # Utiliser un cache pour éviter de recalculer les distances
        cache_key = (id(self), id(other))
        if cache_key not in self._distances_cache:
            self._distances_cache[cache_key] = np.linalg.norm(self.x - other.x)
        return self._distances_cache[cache_key]

    def angle_mort(self: Boid, other: Boid) -> bool:
        "Renvoie True si le Boid `other` est dans l'angle mort du Boid courant."
        # Optimisation: éviter de recalculer les vecteurs
        v1 = self.dx  # Pas besoin de soustraire self.x car dx est déjà un vecteur
        v2 = other.x - self.x  # Vecteur de self vers other
        
        # Éviter de calculer les normes si possible
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return False
            
        cos_angle = np.dot(v1, v2) / (norm_v1 * norm_v2)
        # Assurer que cos_angle est dans [-1, 1] pour éviter des erreurs numériques
        cos_angle = max(-1.0, min(1.0, cos_angle))
        return np.arccos(cos_angle) > 0.75 * np.pi

    def voisins(
        self: Boid, population: list[Boid], seuil: float
    ) -> list[Boid]:
        "Renvoie la liste des voisins visibles, triés par ordre croissant de distance."
        # Utiliser un cache pour éviter de recalculer les voisins
        cache_key = (id(population), seuil)
        if cache_key in self._voisins_cache:
            return self._voisins_cache[cache_key]
            
        # Réinitialiser le cache des distances pour ce nouveau calcul
        self._distances_cache = {}
        
        # Calculer les voisins
        result = sorted(
            (
                other
                for other in population
                if self is not other
                and self.distance(other) < seuil
                and not self.angle_mort(other)
            ),
            key=self.distance,
        )
        
        # Stocker dans le cache
        self._voisins_cache[cache_key] = result
        return result

    def separation(self, population: list[Boid]):
        "La composante de la force qui éloigne les Boids les uns des autres."
        voisins_proches = self.voisins(population, 50)[: Boid.max_voisins]
        if not voisins_proches:
            return np.zeros(2)
            
        return sum(
            self.x - other.x
            for other in voisins_proches
        )

    def align(self, population: list[Boid]):
        "La composante de la force qui aligne les Boids les uns avec les autres"
        voisins = self.voisins(population, 200)[: Boid.max_voisins]
        if not voisins:
            return np.zeros(2)
            
        vitesses = sum(other.dx for other in voisins)
        return vitesses / len(voisins) - self.dx

    def cohere(self: Boid, population: list[Boid]):
        "La composante de la force qui rapproche les Boids les uns des autres."
        voisins = self.voisins(population, 200)[: Boid.max_voisins]
        if not voisins:
            return np.zeros(2)
            
        positions = sum(other.x for other in voisins)
        return positions / len(voisins) - self.x

    def detect_predator(self: Boid, population: list[Boid]) -> bool:
        """Détecte si un predaboid est à proximité.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            bool: True si un predaboid est détecté, False sinon
        """
        # Vérifier si un Predaboid est dans la population
        for other in population:
            # Utiliser le nom de la classe au lieu de isinstance pour éviter la référence circulaire
            if other.__class__.__name__ == "Predaboid" and self.distance(other) < 150 and not self.angle_mort(other):
                return True
        return False
        
    def flee_predator(self: Boid, population: list[Boid]):
        """Calcule une force de répulsion par rapport au predaboid.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            np.ndarray: vecteur de répulsion
        """
        # Chercher le predaboid dans la population
        for other in population:
            if other.__class__.__name__ == "Predaboid" and not self.angle_mort(other):
                # Calculer la distance au predaboid
                dist = self.distance(other)
                if dist < 250:  # Distance de détection du prédateur augmentée
                    # Force de répulsion inversement proportionnelle à la distance
                    # Plus le prédateur est proche, plus la force est grande
                    force = 400 / max(dist, 10)  # Force augmentée et éviter division par zéro
                    # Vecteur de direction opposée au prédateur
                    direction = self.x - other.x
                    # Normaliser le vecteur direction
                    norm = np.linalg.norm(direction)
                    if norm > 0:
                        direction = direction / norm
                    return direction * force
        return np.zeros(2)

    def interaction(self: Boid, population: list[Boid]) -> "Boid":
        "On déplace le Boid en fonction de toutes les forces qui s'y appliquent"
        # Réinitialiser les caches à chaque itération
        self._voisins_cache = {}
        
        # Calculer les forces
        self.dx += (  # avec des pondérations respectives
            self.separation(population) / 10
            + self.align(population) / 8
            + self.cohere(population) / 100
            + self.flee_predator(population) / 2  # Augmenter l'importance de la fuite du prédateur
        )

        # active ou non le boost uniquement si un predaboid est détecté
        if self.detect_predator(population) and self.boostValue > 1:
            self.boost = True
        else:
            self.boost = False

        # prise en compte des fonctions externes
        for fun, poids in self.interactions:
            self.dx += fun(self, population) / poids

        # limite de la vitesse
        vitesse_actuelle = self.vitesse
        if vitesse_actuelle > Boid.maXVitesse:
            self.dx = self.dx * Boid.maXVitesse / vitesse_actuelle

        # On avance
        self.move()

        # On veille à rester dans le cadre par effet rebond
        if (np.abs(self.x) > Boid.taille).any():
            for i, coord in enumerate(self.x):
                if (diff := coord + Boid.taille) < 10:
                    self.x[i] = -Boid.taille + 10 + diff
                    self.dx[i] *= -1
                if (diff := Boid.taille - coord) < 10:
                    self.x[i] = Boid.taille - 10 - diff
                    self.dx[i] *= -1

        return self
    
    def move(self : Boid) -> None:
        if self.boost: 
            self.x += self.dx * self.boostValue

            self.boostValue -= 0.5

            if self.boostValue <= 1:
                self.boostValue = 0
                self.boost = False

        else: 
            self.x += self.dx * self.boostValue

            if self.boostValue <= Boid.maxBoostValue: 
                self.boostValue += 0.05

                if self.boostValue >= Boid.maxBoostValue: 
                    self.boostValue = Boid.maxBoostValue

class Predaboid(Boid):
    def __init__(self, position=None, vitesse=None):
        super().__init__(position, vitesse)
        self.eating_range = 20  # Range within which the predator can eat other boids
        self.boostValue : float = 1.2  # Vitesse de base plus élevée

    def eat(self, population: list[Boid]) -> list[Boid]:
        """Eat boids within the eating range."""
        new_population = []
        for boid in population:
            if self.distance(boid) > self.eating_range:
                new_population.append(boid)
        return new_population
        
    def flee_predator(self, population: list[Boid]):
        """Surcharge de la méthode flee_predator pour que le predaboid ne se fuie pas lui-même."""
        # Le predaboid ne fuit pas les autres predaboids
        return np.zeros(2)
        
    def separation(self, population: list[Boid]):
        """Surcharge de la méthode separation pour que le predaboid n'utilise pas la force de séparation."""
        # Le predaboid n'utilise pas la force de séparation
        return np.zeros(2)
        
    def move(self : Boid) -> None:
        # Le Predaboid ne peut pas boost mais a une vitesse de base plus élevée
        self.x += self.dx * self.boostValue

# ------------------------------------------------------------------------------
# fonctions d'interaction
# ------------------------------------------------------------------------------
funInteraction : TypeAlias = Callable[[Boid, list[Boid]], float]

# ------------------------------------------------------------------------------
def centripete(self: Boid, population: list[Boid]):
    "Une composante de force centripète (va vers centre)."
    return -self.x

# ------------------------------------------------------------------------------
def centrifuge(self: Boid, population: list[Boid]):
    "Une composante de force centripète (va vers centre)."
    return +self.x

# ------------------------------------------------------------------------------
def noise(self: Boid, population: list[Boid]):
    "Un peu de comportement aléatoire."
    return np.random.uniform(-5, 5, 2)

# ------------------------------------------------------------------------------
# builder de boid avec centripete
# ------------------------------------------------------------------------------
def buildBoidCentripete() -> Boid:
    boid = Boid()
    boid.add_interaction(centripete, 200)
    return boid

# ------------------------------------------------------------------------------
# simulation (avec pygame)
# ------------------------------------------------------------------------------
class Simulation:
    def __init__(self: Simulation, n: int, seed: int = 2042) -> None:
      """
        Args:
          n: int = nombre de boids
          seed: int
      """

      np.random.seed(seed)

      self.boids = list(buildBoidCentripete() for _ in range(n))
      self.predator = Predaboid()  # Add a predator boid

    def iteration(self: Simulation):
        
        # Optimisation: éviter de créer une nouvelle liste à chaque itération
        for boid in self.boids:
            boid.interaction(self.boids + [self.predator])
        
        # Predator eats boids
        self.boids = self.predator.eat(self.boids)
        
        # Le predaboid n'interagit qu'avec les boids normaux, pas avec lui-même
        self.predator.interaction(self.boids)

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------

# Initialize Pygame
pygame.init()

# Define colors
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Set up display
screen_size = (Boid.taille * 2, Boid.taille * 2)
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Boid Simulation')

# Main loop
running = True
clock = pygame.time.Clock()

# Create simulation
simulation = Simulation(n=30)

# Police pour le message de fin
font = pygame.font.Font(None, 74)
game_over_text = font.render("GAME OVER", True, (255, 0, 0))
game_over_rect = game_over_text.get_rect(center=(Boid.taille, Boid.taille))

# Variable pour suivre si le jeu est terminé
game_over = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill((255, 255, 255))

    # Vérifier s'il reste des boids
    if len(simulation.boids) == 0 and not game_over:
        game_over = True
        print("GAME OVER - Le prédateur a mangé tous les boids!")

    # Update boids seulement si le jeu n'est pas terminé
    if not game_over:
        simulation.iteration()

    # Draw boids
    for boid in simulation.boids:
        pygame.draw.circle(screen, BLUE, (int(boid.x[0] + Boid.taille), int(boid.x[1] + Boid.taille)), 5)

    # Draw predator
    pygame.draw.circle(screen, RED, (int(simulation.predator.x[0] + Boid.taille), int(simulation.predator.x[1] + Boid.taille)), 8)

    # Afficher le message de fin si le jeu est terminé
    if game_over:
        screen.blit(game_over_text, game_over_rect)

    # Refresh screen
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

pygame.quit()
