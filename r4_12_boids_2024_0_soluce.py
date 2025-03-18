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

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation, path
# a adapter en fonction de votre installation de ffmpeg
plt.rcParams['animation.ffmpeg_path'] = "/usr/bin/ffmpeg"
radians :  TypeAlias= float

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
def pathRotate(p: path.Path, angle: radians) -> path.Path:
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
    def direction(self: Boid) -> radians:
        return np.arctan2(self.dx[1], self.dx[0])

    # autres methodes
    def distance(self: Boid, other: Boid) -> float:
        "Renvoie la distance entre deux Boids."
        return np.linalg.norm(self.x - other.x)

    def angle_mort(self: Boid, other: Boid) -> bool:
        "Renvoie True si le Boid `other` est dans l'angle mort du Boid courant."
        v1 = self.dx - self.x
        v2 = other.dx - other.x
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.arccos(cos_angle) > 0.75 * np.pi

    def voisins(
        self: Boid, population: list[Boid], seuil: float
    ) -> list[Boid]:
        "Renvoie la liste des voisins visibles, triés par ordre croissant de distance."
        return sorted(
            (
                other
                for other in population
                if self is not other
                and not self.angle_mort(other)
                and self.distance(other) < seuil
            ),
            key=self.distance,
        )

    def separation(self, population: list[Boid]):
        "La composante de la force qui éloigne les Boids les uns des autres."
        return sum(
            self.x - other.x
            for other in self.voisins(population, 50)[: Boid.max_voisins]
        )

    def align(self, population: list[Boid]):
        "La composante de la force qui aligne les Boids les uns avec les autres"
        voisins = self.voisins(population, 200)[: Boid.max_voisins]
        vitesses = sum(other.dx for other in voisins)
        return vitesses / len(voisins) - self.dx if len(voisins) else 0

    def cohere(self: Boid, population: list[Boid]):
        "La composante de la force qui rapproche les Boids les uns des autres."
        voisins = self.voisins(population, 200)[: Boid.max_voisins]
        vitesses = sum(other.x for other in voisins)
        return vitesses / len(voisins) - self.x if len(voisins) else 0

    def interaction(self: Boid, population: list[Boid]) -> "Boid":
        "On déplace le Boid en fonction de toutes les forces qui s'y appliquent"

        self.dx += (  # avec des pondérations respectives
            self.separation(population) / 10
            + self.align(population) / 8
            + self.cohere(population) / 100
        )

        # active ou non le boost
        if len(self.voisins(population, 100)) > 5 and self.boostValue > 1 :
            self.boost = True
        else:
            self.boost = False

        # prise en compte des fonctions externes
        for fun, poids in self.interactions:
            self.dx += fun(self, population) / poids

        # limite de la vitesse
        if self.vitesse > Boid.maXVitesse:
            self.vitesse = Boid.maXVitesse

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

            self.boostValue -= 0.1

            if self.boostValue <= 1:
                self.boostValue = 0
                self.boost = False

        else: 
            self.x += self.dx * self.boostValue

            if self.boostValue <= Boid.maxBoostValue: 
                self.boostValue += 0.2

                if self.boostValue >= Boid.maxBoostValue: 
                    self.boostValue = Boid.maxBoostValue


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
# simulation (avec matplotlib)
# ------------------------------------------------------------------------------
class Simulation:
    def __init__(self: Simulation, n: int, ax, seed: int = 2042) -> None:
      """
        Args:
          n: int = nombre de boids
          ax: matplotlib.axes.Axes = where to plot the boids
          seed: int
      """

      np.random.seed(seed)

      self.boids = list(buildBoidCentripete() for _ in range(n))
      self.artists = list()
      self.plot(ax)

    def plot(self: Simulation, ax) -> None:

        for boid in self.boids:
            p, *_ = ax.plot(
                *boid.x,
                color=".1",
                markersize=15,
                marker=pathRotate(boid_shape, boid.direction),
            )
            self.artists.append(p)

        ax.set_xlim((-Boid.taille, Boid.taille))
        ax.set_ylim((-Boid.taille, Boid.taille))
        ax.set_aspect(1)
        ax.xaxis.set_visible(False)
        ax.yaxis.set_visible(False)

    def iteration(self: Simulation, frame: int):
        """
          Args:
            frame: int = frame number
        """
        print(f"iteration {frame}/400")
        self.boids = list(boid.interaction(self.boids) for boid in self.boids)

        for p, boid in zip(self.artists, self.boids):
            p.set_data([boid.x[0]], [boid.x[1]])
            p.set_marker(pathRotate(boid_shape, boid.direction))

        return self.artists

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(7, 7))
simulation = Simulation(n=30, ax=ax)

anim = animation.FuncAnimation(
    fig,
    simulation.iteration,
    frames=range(0, 400),
    interval=150,
    blit=True,
    repeat=True,
)

# saving to m4 using ffmpeg writer 
anim.save('boidsLongCentipete.mp4') 


