
import pygame
import random
import json
from pathlib import Path

pygame.init()

# Game window
WIDTH = 420
HEIGHT = 620
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
CLOCK = pygame.time.Clock()

# Colors
SKY = (115, 195, 235)
GREEN = (65, 180, 75)
DARK_GREEN = (35, 135, 55)
YELLOW = (255, 220, 55)
ORANGE = (245, 145, 35)
WHITE = (255, 255, 255)
BLACK = (35, 35, 35)
GROUND = (220, 190, 125)

FONT = pygame.font.SysFont("arial", 28, bold=True)
SMALL_FONT = pygame.font.SysFont("arial", 18)
BIG_FONT = pygame.font.SysFont("arial", 42, bold=True)

# Save highest score
HIGHSCORE_FILE = Path(__file__).with_name("flappy_highscore.json")


def load_high_score():
    try:
        data = json.loads(HIGHSCORE_FILE.read_text())
        return int(data.get("high_score", 0))
    except (OSError, ValueError, TypeError):
        return 0


def save_high_score(score):
    try:
        HIGHSCORE_FILE.write_text(
            json.dumps({"high_score": score}, indent=2)
        )
    except OSError:
        pass


high_score = load_high_score()


# Bird class
class Bird:
    def __init__(self):
        self.x = 90
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 15

    def flap(self):
        self.velocity = -7.2

    def update(self):
        self.velocity += 0.38
        self.y += self.velocity

    def draw(self):
        pygame.draw.circle(
            SCREEN, YELLOW,
            (int(self.x), int(self.y)), self.radius
        )

        pygame.draw.circle(
            SCREEN, ORANGE,
            (int(self.x + 12), int(self.y + 3)), 7
        )

        pygame.draw.circle(
            SCREEN, WHITE,
            (int(self.x + 5), int(self.y - 5)), 5
        )

        pygame.draw.circle(
            SCREEN, BLACK,
            (int(self.x + 7), int(self.y - 5)), 2
        )


# Pipe class
class Pipe:
    WIDTH = 66
    GAP = 165
    SPEED = 3

    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(190, HEIGHT - 180)
        self.passed = False

    def update(self):
        self.x -= self.SPEED

    def draw(self):
        top_height = self.gap_y - self.GAP // 2
        bottom_y = self.gap_y + self.GAP // 2

        pygame.draw.rect(
            SCREEN, GREEN,
            (self.x, 0, self.WIDTH, top_height)
        )

        pygame.draw.rect(
            SCREEN, DARK_GREEN,
            (self.x, top_height - 12, self.WIDTH, 12)
        )

        pygame.draw.rect(
            SCREEN, GREEN,
            (self.x, bottom_y, self.WIDTH,
             HEIGHT - bottom_y - 55)
        )

        pygame.draw.rect(
            SCREEN, DARK_GREEN,
            (self.x, bottom_y, self.WIDTH, 12)
        )

    def collides(self, bird):
        bird_rect = pygame.Rect(
            bird.x - bird.radius,
            bird.y - bird.radius,
            bird.radius * 2,
            bird.radius * 2
        )

        top_rect = pygame.Rect(
            self.x, 0,
            self.WIDTH,
            self.gap_y - self.GAP // 2
        )

        bottom_y = self.gap_y + self.GAP // 2

        bottom_rect = pygame.Rect(
            self.x, bottom_y,
            self.WIDTH,
            HEIGHT - bottom_y - 55
        )

        return (
            bird_rect.colliderect(top_rect)
            or bird_rect.colliderect(bottom_rect)
        )


# Display text
def draw_text(text, font, colour, center):
    surface = font.render(text, True, colour)
    SCREEN.blit(surface, surface.get_rect(center=center))


# Reset game
def reset_game():
    return Bird(), [Pipe(WIDTH + 80)], 0, False


bird, pipes, score, game_over = reset_game()

started = False
pipe_timer = 0
running = True


# Main game loop
while running:

    CLOCK.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_SPACE, pygame.K_UP):

                if game_over:
                    bird, pipes, score, game_over = reset_game()
                    started = True

                else:
                    started = True
                    bird.flap()

            elif event.key == pygame.K_r and game_over:
                bird, pipes, score, game_over = reset_game()
                started = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if game_over:
                bird, pipes, score, game_over = reset_game()
                started = True

            else:
                started = True
                bird.flap()

    SCREEN.fill(SKY)

    # Clouds
    pygame.draw.circle(SCREEN, WHITE, (75, 105), 20)
    pygame.draw.circle(SCREEN, WHITE, (98, 100), 25)
    pygame.draw.circle(SCREEN, WHITE, (122, 107), 18)

    pygame.draw.circle(SCREEN, WHITE, (285, 165), 17)
    pygame.draw.circle(SCREEN, WHITE, (307, 158), 23)
    pygame.draw.circle(SCREEN, WHITE, (330, 166), 16)

    # Game updates
    if started and not game_over:

        bird.update()

        pipe_timer += 1

        if pipe_timer >= 95:
            pipes.append(Pipe(WIDTH + 10))
            pipe_timer = 0

        for pipe in pipes:

            pipe.update()

            # Increase score
            if not pipe.passed and pipe.x + pipe.WIDTH < bird.x:
                pipe.passed = True
                score += 1

            # Check collision
            if pipe.collides(bird):
                game_over = True

        pipes = [
            pipe for pipe in pipes
            if pipe.x + pipe.WIDTH > 0
        ]

        # Ground and ceiling collision
        if bird.y - bird.radius < 0:
            game_over = True

        if bird.y + bird.radius > HEIGHT - 55:
            game_over = True

        # Save highest score
        if score > high_score:
            high_score = score
            save_high_score(high_score)

    # Draw pipes
    for pipe in pipes:
        pipe.draw()

    # Draw bird
    bird.draw()

    # Ground
    pygame.draw.rect(
        SCREEN, GROUND,
        (0, HEIGHT - 55, WIDTH, 55)
    )

    pygame.draw.line(
        SCREEN, DARK_GREEN,
        (0, HEIGHT - 55),
        (WIDTH, HEIGHT - 55), 5
    )

    # Current score
    draw_text(
        str(score), BIG_FONT, WHITE,
        (WIDTH // 2, 55)
    )

    # Highest score
    draw_text(
        f"Best: {high_score}",
        SMALL_FONT, WHITE,
        (WIDTH - 65, 25)
    )

    # Starting screen
    if not started and not game_over:

        draw_text(
            "FLAPPY BIRD", BIG_FONT,
            WHITE, (WIDTH // 2, 245)
        )

        draw_text(
            "Press SPACE or click to flap",
            SMALL_FONT, WHITE,
            (WIDTH // 2, 295)
        )

        draw_text(
            "Avoid the pipes!",
            SMALL_FONT, WHITE,
            (WIDTH // 2, 325)
        )

    # Game over screen
    if game_over:

        pygame.draw.rect(
            SCREEN, WHITE,
            (45, 220, WIDTH - 90, 190),
            border_radius=16
        )

        draw_text(
            "GAME OVER", BIG_FONT,
            BLACK, (WIDTH // 2, 265)
        )

        draw_text(
            f"Score: {score}", FONT,
            BLACK, (WIDTH // 2, 315)
        )

        draw_text(
            f"Highest score: {high_score}",
            SMALL_FONT, BLACK,
            (WIDTH // 2, 350)
        )

        draw_text(
            "Click or press SPACE to play again",
            SMALL_FONT, BLACK,
            (WIDTH // 2, 385)
        )

    pygame.display.flip()

pygame.quit()
