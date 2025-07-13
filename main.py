import pygame
import random
import sys

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

# Player properties
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
PLAYER_JUMP_HEIGHT = 20
PLAYER_JUMP_DURATION = 30  # in frames
PLAYER_SLIDE_DURATION = 30 # in frames
PLAYER_SLIDE_HEIGHT = 25

# Lane properties
LANE_COUNT = 3
LANE_WIDTH = SCREEN_WIDTH // LANE_COUNT
LANE_CENTERS = [LANE_WIDTH // 2, LANE_WIDTH + LANE_WIDTH // 2, 2 * LANE_WIDTH + LANE_WIDTH // 2]

# Obstacle properties
OBSTACLE_WIDTH = 80
OBSTACLE_HEIGHT = 40
OBSTACLE_SPEED = 5

# --- Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        
        self.lane = 1  # Start in the middle lane (0, 1, 2)
        self.rect.centerx = LANE_CENTERS[self.lane]
        self.rect.bottom = SCREEN_HEIGHT - 60

        self.is_jumping = False
        self.jump_timer = 0
        self.is_sliding = False
        self.slide_timer = 0
        
        self.original_height = PLAYER_HEIGHT
        self.original_y = self.rect.y

    def update(self):
        # Jump logic
        if self.is_jumping:
            self.jump_timer += 1
            # Simple up and down motion for jump
            if self.jump_timer <= PLAYER_JUMP_DURATION / 2:
                self.rect.y -= 4
            else:
                self.rect.y += 4
            
            if self.jump_timer >= PLAYER_JUMP_DURATION:
                self.is_jumping = False
                self.rect.y = self.original_y

        # Slide logic
        if self.is_sliding:
            self.slide_timer += 1
            if self.slide_timer >= PLAYER_SLIDE_DURATION:
                self.is_sliding = False
                self.rect.height = self.original_height
                self.rect.y = self.original_y
                self.image = pygame.Surface([PLAYER_WIDTH, self.original_height])
                self.image.fill(BLUE)


    def move(self, direction):
        if not self.is_jumping and not self.is_sliding:
            if direction == "LEFT" and self.lane > 0:
                self.lane -= 1
            elif direction == "RIGHT" and self.lane < LANE_COUNT - 1:
                self.lane += 1
            self.rect.centerx = LANE_CENTERS[self.lane]

    def jump(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_jumping = True
            self.jump_timer = 0
            self.original_y = self.rect.y

    def slide(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_sliding = True
            self.slide_timer = 0
            self.original_y = self.rect.y
            self.rect.height = PLAYER_SLIDE_HEIGHT
            self.rect.y += (self.original_height - PLAYER_SLIDE_HEIGHT)
            self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_SLIDE_HEIGHT])
            self.image.fill(BLUE)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface([OBSTACLE_WIDTH, OBSTACLE_HEIGHT])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        
        self.lane = random.randint(0, LANE_COUNT - 1)
        self.rect.centerx = LANE_CENTERS[self.lane]
        self.rect.y = -self.rect.height
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# --- Game Functions ---

def draw_lanes(screen):
    for i in range(1, LANE_COUNT):
        pygame.draw.line(screen, GRAY, (i * LANE_WIDTH, 0), (i * LANE_WIDTH, SCREEN_HEIGHT), 2)

def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Endless Runner")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 50)

    player = Player()
    obstacles = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    score = 0
    game_speed = OBSTACLE_SPEED
    obstacle_spawn_timer = 0
    
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        player.move("LEFT")
                    if event.key == pygame.K_RIGHT:
                        player.move("RIGHT")
                    if event.key == pygame.K_UP:
                        player.jump()
                    if event.key == pygame.K_DOWN:
                        player.slide()
                else:
                    if event.key == pygame.K_r:
                        game_loop() # Restart the game

        if not game_over:
            # --- Update ---
            player.update()
            obstacles.update()
            
            # Increase score and speed
            score += 1
            if score % 500 == 0:
                game_speed += 0.5
                for obstacle in obstacles:
                    obstacle.speed = game_speed

            # Spawn obstacles
            obstacle_spawn_timer += 1
            if obstacle_spawn_timer > max(30, 100 - game_speed * 5):
                new_obstacle = Obstacle(game_speed)
                # Ensure new obstacle doesn't spawn in the same lane as the previous one too often
                if len(obstacles) > 0:
                    last_obstacle = obstacles.sprites()[-1]
                    if new_obstacle.lane == last_obstacle.lane:
                        new_obstacle.lane = (new_obstacle.lane + random.choice([-1, 1])) % LANE_COUNT
                        new_obstacle.rect.centerx = LANE_CENTERS[new_obstacle.lane]

                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)
                obstacle_spawn_timer = 0

            # Collision check
            if pygame.sprite.spritecollide(player, obstacles, False):
                game_over = True

        # --- Draw ---
        screen.fill(BLACK)
        draw_lanes(screen)
        all_sprites.draw(screen)

        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            game_over_text = font.render("GAME OVER", True, WHITE)
            restart_text = font.render("Press 'R' to Restart", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    game_loop()
