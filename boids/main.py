"""
Module principal pour lancer la simulation de boids.
"""

import pygame
from boid import Boid
from simulation import Simulation

def run_simulation():
    """
    Lance la simulation de boids avec interface graphique pygame.
    """
    # Initialiser Pygame
    pygame.init()

    # Définir les couleurs
    BLUE = (0, 0, 255)
    RED = (255, 0, 0)

    # Configurer l'affichage
    screen_size = (Boid.taille * 2, Boid.taille * 2)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Boid Simulation')

    # Boucle principale
    running = True
    clock = pygame.time.Clock()

    # Créer la simulation
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

        # Effacer l'écran
        screen.fill((255, 255, 255))

        # Vérifier s'il reste des boids
        if len(simulation.boids) == 0 and not game_over:
            game_over = True
            print("GAME OVER - Le prédateur a mangé tous les boids!")

        # Mettre à jour les boids seulement si le jeu n'est pas terminé
        if not game_over:
            simulation.iteration()

        # Dessiner les boids
        for boid in simulation.boids:
            pygame.draw.circle(screen, BLUE, (int(boid.x[0] + Boid.taille), int(boid.x[1] + Boid.taille)), 5)

        # Dessiner le prédateur
        pygame.draw.circle(screen, RED, (int(simulation.predator.x[0] + Boid.taille), int(simulation.predator.x[1] + Boid.taille)), 8)

        # Afficher le message de fin si le jeu est terminé
        if game_over:
            screen.blit(game_over_text, game_over_rect)

        # Rafraîchir l'écran
        pygame.display.flip()

        # Limiter la fréquence d'images
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    run_simulation()
