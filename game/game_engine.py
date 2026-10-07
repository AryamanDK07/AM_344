import pygame
from .player import Player
from .platform import Platform
from .hazard import Hazard

# Game Engine

WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.gravity = 0.6

        self.start_x, self.start_y = 40, height - 120
        self.player = Player(self.start_x, self.start_y)

        # A simple hand-built level: platforms with gaps between them
        # (falling into a gap means falling off the bottom of the
        # screen), one hazard, and a goal near the right edge.
        ground_y = height - 40
        self.platforms = [
            Platform(0, ground_y, 160),
            Platform(220, ground_y, 140),
            Platform(420, ground_y - 60, 120),
            Platform(600, ground_y, 180),
        ]
        self.hazards = [Hazard(240, ground_y - 14, 100)]
        self.goal_x = 740

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.game_over_text_font = pygame.font.SysFont("Arial", 24)
        self.game_over = False
        self.replay_requested = False
        self.exit_requested = False

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.replay_requested = True
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.exit_requested = True
            return

        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            self.player.jump()

    def handle_input(self):
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def update(self):
        if self.game_over:
            return

        previous_y = self.player.y
        self.player.vy += self.gravity
        self.player.x = max(0, self.player.x + self.player.vx)
        self.player.y += self.player.vy
        self.player.on_ground = False
        if self.player.vy > 0:
            previous_bottom = previous_y + self.player.height
            current_bottom = self.player.y + self.player.height
            landing_platform = None
            for platform in self.platforms:
                horizontal_overlap = (
                    self.player.x < platform.x + platform.width
                    and self.player.x + self.player.width > platform.x
                )
                crossed_platform_top = (
                    previous_bottom <= platform.y <= current_bottom
                )
                if horizontal_overlap and crossed_platform_top:
                    if landing_platform is None or platform.y < landing_platform.y:
                        landing_platform = platform

            if landing_platform is not None:
                self.player.y = landing_platform.y - self.player.height
                self.player.vy = 0
                self.player.on_ground = True

        for hazard in self.hazards:
            if self.player.rect().colliderect(hazard.rect()):
                self.game_over = True
                return

        if self.player.y > self.height:
            self.game_over = True
            return

        if self.player.x >= self.goal_x:
            self.score += 1
            self.player.x, self.player.y = self.start_x, self.start_y
            self.player.vy = 0

    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())
        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)
        pygame.draw.rect(screen, GREEN, goal_rect)

        pygame.draw.rect(screen, WHITE, self.player.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            title = self.game_over_font.render("GAME OVER", True, WHITE)
            final_score = self.game_over_text_font.render(
                f"Final Score: {self.score}", True, WHITE
            )
            replay_hint = self.game_over_text_font.render(
                "Press R to continue to replay / difficulty selection",
                True,
                WHITE,
            )
            exit_hint = self.game_over_text_font.render(
                "Press Esc or Q to exit", True, WHITE
            )

            center_x = self.width // 2
            center_y = self.height // 2
            screen.blit(title, title.get_rect(center=(center_x, center_y - 85)))
            screen.blit(final_score, final_score.get_rect(center=(center_x, center_y - 25)))
            screen.blit(replay_hint, replay_hint.get_rect(center=(center_x, center_y + 30)))
            screen.blit(exit_hint, exit_hint.get_rect(center=(center_x, center_y + 70)))
