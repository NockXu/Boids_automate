"""
Module contenant la classe Boid pour la simulation de boids.
"""

from __future__ import annotations
from typing import TypeAlias, Callable
import numpy as np

# Type pour les fonctions d'interaction
funInteraction: TypeAlias = Callable[["Boid", list["Boid"]], float]

class Boid:
    """
    Classe représentant un boid dans la simulation.
    Un boid est une entité qui se déplace selon des règles simples
    d'interaction avec les autres boids.
    """

    # Attributs de classe
    taille: int = 300  # taille du cadre
    max_voisins: int = 10  # nombre de voisins à considérer
    maXVitesse: int = 10  # vitesse maximale
    maxBoostValue: float = 3  # valeur maximale du boost

    def __init__(self: Boid, position=None, vitesse=None) -> None:
        """
        Initialise un nouveau boid.
        
        Args:
            position: position initiale (aléatoire si None)
            vitesse: vitesse initiale (aléatoire si None)
        """
        self.x = (
            position
            if position is not None
            else np.random.uniform(-Boid.taille, Boid.taille, 2)
        )
        self.dx = (
            vitesse if vitesse is not None else np.random.uniform(-5, 5, 2)
        )
        # Liste des fonctions d'interaction non incluse dans la classe et le poids associé
        self.interactions: list[tuple[funInteraction, float]] = []

        # Permet de savoir si le boid est sous l'effet d'un boost
        self.boost: bool = False
        # Initialise la puissance du boost
        self.boostValue: float = Boid.maxBoostValue
        
        # Cache pour stocker les voisins calculés
        self._voisins_cache = {}
        # Cache pour stocker les distances calculées
        self._distances_cache = {}

    def add_interaction(self: Boid, fun: funInteraction, poids: float) -> None:
        """
        Ajoute une fonction d'interaction à la liste des interactions.
        
        Args:
            fun: fonction d'interaction
            poids: poids associé à cette interaction
        """
        self.interactions.append((fun, poids))

    def __repr__(self: Boid) -> str:
        """Représentation textuelle du boid."""
        return f"<Boid({self.x.round(2)}, {self.dx.round(2)})>"

    # Getters et setters
    @property
    def vitesse(self: Boid) -> float:
        """Calcule la norme du vecteur vitesse."""
        return np.linalg.norm(self.dx)

    @vitesse.setter
    def vitesse(self: Boid, value: float) -> None:
        """Modifie la norme du vecteur vitesse en conservant sa direction."""
        self.dx = self.dx * value / self.vitesse

    @property
    def direction(self: Boid) -> float:
        """Calcule la direction du boid en radians."""
        return np.arctan2(self.dx[1], self.dx[0])

    def distance(self: Boid, other: Boid) -> float:
        """
        Calcule la distance entre deux boids.
        
        Args:
            other: l'autre boid
            
        Returns:
            float: distance entre les deux boids
        """
        # Utiliser un cache pour éviter de recalculer les distances
        cache_key = (id(self), id(other))
        if cache_key not in self._distances_cache:
            self._distances_cache[cache_key] = np.linalg.norm(self.x - other.x)
        return self._distances_cache[cache_key]

    def angle_mort(self: Boid, other: Boid) -> bool:
        """
        Vérifie si l'autre boid est dans l'angle mort du boid courant.
        
        Args:
            other: l'autre boid
            
        Returns:
            bool: True si l'autre boid est dans l'angle mort
        """
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

    def voisins(self: Boid, population: list[Boid], seuil: float) -> list[Boid]:
        """
        Renvoie la liste des voisins visibles, triés par ordre croissant de distance.
        
        Args:
            population: liste de tous les boids
            seuil: distance maximale pour considérer un boid comme voisin
            
        Returns:
            list[Boid]: liste des voisins triés par distance
        """
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
        """
        Calcule la composante de la force qui éloigne les boids les uns des autres.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            np.ndarray: vecteur de séparation
        """
        voisins_proches = self.voisins(population, 50)[: Boid.max_voisins]
        if not voisins_proches:
            return np.zeros(2)
            
        return sum(
            self.x - other.x
            for other in voisins_proches
        )

    def align(self, population: list[Boid]):
        """
        Calcule la composante de la force qui aligne les boids les uns avec les autres.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            np.ndarray: vecteur d'alignement
        """
        voisins = self.voisins(population, 200)[: Boid.max_voisins]
        if not voisins:
            return np.zeros(2)
            
        vitesses = sum(other.dx for other in voisins)
        return vitesses / len(voisins) - self.dx

    def cohere(self: Boid, population: list[Boid]):
        """
        Calcule la composante de la force qui rapproche les boids les uns des autres.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            np.ndarray: vecteur de cohésion
        """
        voisins = self.voisins(population, 200)[: Boid.max_voisins]
        if not voisins:
            return np.zeros(2)
            
        positions = sum(other.x for other in voisins)
        return positions / len(voisins) - self.x

    def detect_predator(self: Boid, population: list[Boid]) -> bool:
        """
        Détecte si un predaboid est à proximité.
        
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
        """
        Calcule une force de répulsion par rapport au predaboid.
        
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
        """
        Déplace le boid en fonction de toutes les forces qui s'y appliquent.
        
        Args:
            population: liste de tous les boids
            
        Returns:
            Boid: le boid lui-même après déplacement
        """
        # Réinitialiser les caches à chaque itération
        self._voisins_cache = {}
        
        # Optimisation: calculer les voisins une seule fois pour les différentes distances
        voisins_proches = len(self.voisins(population, 25))
        
        # Calculer les forces
        self.dx += (  # avec des pondérations respectives
            self.separation(population) / 50
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
        """
        Déplace le boid en fonction de sa vitesse et de son boost.
        """
        if self.boost: 
            self.x += self.dx * self.boostValue

            self.boostValue -= 0.5

            if self.boostValue <= 1:
                self.boostValue = 0
                self.boost = False

        else: 
            self.x += self.dx * self.boostValue

            if self.boostValue <= Boid.maxBoostValue: 
                self.boostValue += 0.01

                if self.boostValue >= Boid.maxBoostValue: 
                    self.boostValue = Boid.maxBoostValue


# Fonctions d'interaction externes
def centripete(self: Boid, population: list[Boid]):
    """Une composante de force centripète (va vers centre)."""
    return -self.x

def centrifuge(self: Boid, population: list[Boid]):
    """Une composante de force centrifuge (s'éloigne du centre)."""
    return +self.x

def noise(self: Boid, population: list[Boid]):
    """Un peu de comportement aléatoire."""
    return np.random.uniform(-5, 5, 2)

def buildBoidCentripete() -> Boid:
    """
    Crée un boid avec une force centripète.
    
    Returns:
        Boid: un nouveau boid avec force centripète
    """
    boid = Boid()
    boid.add_interaction(centripete, 200)
    return boid
