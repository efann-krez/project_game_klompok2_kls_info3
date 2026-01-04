import pygame
import random
import sys
import urllib.request
import os
import math

# ===========================
# Download gambar
# ===========================
def download_image(url, filename):
    if not os.path.exists(filename):
        urllib.request.urlretrieve(url, filename)

download_image("https://i.ibb.co/vs3fG0F/road.png", "background.png")
download_image("https://i.ibb.co/0F7ZVYQ/player_car.png", "player_car.png")
download_image("https://i.ibb.co/1zM5P6N/enemy_car.png", "enemy_car.png")

# ===========================
# Init pygame
# ===========================
pygame.init()
WIDTH, HEIGHT = 480, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game Mobil Balap 2D - Enhanced")

clock = pygame.time.Clock()
FPS = 60

# ===========================
# Load gambar
# ===========================
try:
    background_img = pygame.image.load("background.png").convert()
    # Scale background to full screen to avoid gaps
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except:
    # Fallback: create custom road background
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill((40, 40, 40))  # Dark gray road
    # Draw road markings
    pygame.draw.rect(background_img, (255, 255, 255), (50, 0, 10, HEIGHT))  # Left line
    pygame.draw.rect(background_img, (255, 255, 255), (WIDTH-60, 0, 10, HEIGHT))  # Right line
    # Center dashed line
    for i in range(0, HEIGHT, 60):
        pygame.draw.rect(background_img, (255, 200, 0), (WIDTH//2 - 5, i, 10, 40))

player_img_original = pygame.image.load("player_car.png").convert_alpha()
enemy_img_original = pygame.image.load("enemy_car.png").convert_alpha()

# Remove white/light backgrounds more aggressively
# Set colorkey for various shades of white/gray that might appear
for img in [player_img_original, enemy_img_original]:
    # Set multiple color keys for better transparency
    img.set_colorkey((200, 200, 200))
    img.set_colorkey((255, 255, 255))
    img.set_colorkey((240, 240, 240))
    img.set_colorkey((220, 220, 220))
    img.set_colorkey((250, 250, 250))
    
    # Convert pixels close to white to fully transparent
    for x in range(img.get_width()):
        for y in range(img.get_height()):
            r, g, b, a = img.get_at((x, y))
            # If pixel is very light (close to white), make it transparent
            if r > 200 and g > 200 and b > 200:
                img.set_at((x, y), (r, g, b, 0))

player_img = pygame.transform.scale(player_img_original, (50, 100))
enemy_img = pygame.transform.scale(enemy_img_original, (50, 100))

player_width, player_height = player_img.get_size()
enemy_width, enemy_height = enemy_img.get_size()

# ===========================
# Game States
# ===========================
MENU = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3
WINNER = 4

game_state = MENU

# ===========================
# Warna
# ===========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 150, 255)

# ===========================
# Font
# ===========================
font_large = pygame.font.SysFont(None, 64)
font_medium = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 28)

# ===========================
# Variables
# ===========================
player_x = WIDTH // 2 - 25  # Will be set properly after loading
player_y = HEIGHT - 120
player_speed = 5
player_lives = 3

enemies = []
powerups = []
particles = []

score = 0
high_score = 0
level = 1
bg_scroll = 0
bg_speed = 3

# Road line animation
line_offset = 0
line_speed = 8

# Menu animation
menu_animation_time = 0
menu_cars = []

# Winner animation
winner_animation_time = 0
confetti_particles = []

# Create menu animated cars
for i in range(3):
    menu_cars.append({
        'x': random.randint(60, WIDTH - 60),
        'y': random.randint(-200, HEIGHT),
        'speed': random.randint(2, 5)
    })

# Power-up types
POWERUP_SHIELD = 0
POWERUP_SLOW = 1
POWERUP_BOOST = 2

shield_active = False
shield_timer = 0
slow_active = False
slow_timer = 0
boost_active = False
boost_timer = 0

# ===========================
# Classes
# ===========================
class Enemy:
    def __init__(self):
        self.x = random.randint(60, WIDTH - enemy_width - 60)
        self.y = random.randint(-600, -enemy_height)
        self.speed = random.randint(3, 5) + level
        self.img = enemy_img
        
    def update(self):
        global slow_active
        speed = self.speed * 0.5 if slow_active else self.speed
        self.y += speed
        
    def draw(self):
        screen.blit(self.img, (self.x, self.y))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, enemy_width, enemy_height)

class PowerUp:
    def __init__(self, powerup_type):
        self.x = random.randint(60, WIDTH - 30 - 60)
        self.y = random.randint(-400, -30)
        self.speed = 2
        self.type = powerup_type
        self.size = 30
        
        if powerup_type == POWERUP_SHIELD:
            self.color = BLUE
        elif powerup_type == POWERUP_SLOW:
            self.color = YELLOW
        else:
            self.color = GREEN
            
    def update(self):
        self.y += self.speed
        
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x + self.size//2), int(self.y + self.size//2)), self.size//2)
        
        if self.type == POWERUP_SHIELD:
            text = font_small.render("S", True, WHITE)
        elif self.type == POWERUP_SLOW:
            text = font_small.render("T", True, BLACK)
        else:
            text = font_small.render("B", True, WHITE)
            
        screen.blit(text, (self.x + 8, self.y + 5))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.randint(-5, 5)
        self.vy = random.randint(-5, 5)
        self.life = 30
        self.color = color
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
    def draw(self):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)

class Confetti:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.randint(-3, 3)
        self.vy = random.randint(-8, -3)
        self.gravity = 0.3
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.randint(-10, 10)
        self.size = random.randint(4, 8)
        self.color = random.choice([RED, GREEN, BLUE, YELLOW, (255, 0, 255), (0, 255, 255)])
        
    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        
    def draw(self):
        # Draw rotating rectangle confetti
        points = []
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            px = self.x + math.cos(angle) * self.size
            py = self.y + math.sin(angle) * self.size
            points.append((px, py))
        if len(points) >= 3:
            pygame.draw.polygon(screen, self.color, points)

# ===========================
# Functions
# ===========================
def reset_game():
    global player_x, player_y, enemies, powerups, particles
    global score, level, player_lives, bg_scroll, line_offset
    global shield_active, shield_timer, slow_active, slow_timer, boost_active, boost_timer
    global winner_animation_time, confetti_particles
    
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    player_lives = 3
    enemies = []
    powerups = []
    particles = []
    confetti_particles = []
    score = 0
    level = 1
    bg_scroll = 0
    line_offset = 0
    winner_animation_time = 0
    shield_active = False
    shield_timer = 0
    slow_active = False
    slow_timer = 0
    boost_active = False
    boost_timer = 0
    
    for i in range(3):
        enemies.append(Enemy())

def spawn_enemy():
    if len(enemies) < 5 + level:
        if random.random() < 0.02 + level * 0.005:
            enemies.append(Enemy())

def spawn_powerup():
    if len(powerups) < 2:
        if random.random() < 0.005:
            powerups.append(PowerUp(random.randint(0, 2)))

def create_explosion(x, y, color):
    for _ in range(15):
        particles.append(Particle(x, y, color))

def draw_menu():
    global menu_animation_time, menu_cars
    
    # Animated road background
    screen.fill((40, 40, 40))
    
    # Draw white side lines
    pygame.draw.rect(screen, (255, 255, 255), (50, 0, 8, HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 58, 0, 8, HEIGHT))
    
    # Animated center lines
    menu_animation_time += 1
    offset = (menu_animation_time * 3) % 80
    for i in range(-80, HEIGHT + 80, 80):
        y_pos = i + offset
        pygame.draw.rect(screen, (255, 200, 0), (WIDTH//2 - 4, y_pos, 8, 50))
    
    # Update and draw animated cars in background
    for car in menu_cars:
        car['y'] += car['speed']
        if car['y'] > HEIGHT:
            car['y'] = -100
            car['x'] = random.randint(60, WIDTH - 60)
        
        # Draw semi-transparent cars
        temp_surf = enemy_img.copy()
        temp_surf.set_alpha(100)
        screen.blit(temp_surf, (car['x'], car['y']))
    
    # Draw dark overlay for text readability
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Animated title with glow effect
    pulse = abs((menu_animation_time % 60) - 30) / 30
    title_color = (255, int(255 * pulse), 0)
    
    # Title shadow/glow
    for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        title_shadow = font_large.render("MOBIL BALAP", True, (100, 50, 0))
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + offset[0], 100 + offset[1]))
    
    title = font_large.render("MOBIL BALAP", True, title_color)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    # Animated subtitle
    subtitle = font_small.render("~ Racing Adventure ~", True, WHITE)
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 165))
    
    # Pulsing start button
    pulse_start = 1 + 0.2 * math.sin(menu_animation_time * 0.1)
    start_size = int(40 * pulse_start)
    start_font = pygame.font.SysFont(None, start_size)
    start_text = start_font.render(">> ENTER - Mulai <<", True, GREEN)
    
    # Start button background
    start_rect = pygame.Rect(WIDTH//2 - 140, 270, 280, 60)
    pygame.draw.rect(screen, (0, 80, 0), start_rect, border_radius=10)
    pygame.draw.rect(screen, GREEN, start_rect, 3, border_radius=10)
    
    screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 280))
    
    # Controls section with icons
    controls_y = 370
    pygame.draw.rect(screen, (30, 30, 30), (60, controls_y - 10, WIDTH - 120, 80), border_radius=8)
    pygame.draw.rect(screen, WHITE, (60, controls_y - 10, WIDTH - 120, 80), 2, border_radius=8)
    
    controls_title = font_small.render("KONTROL:", True, YELLOW)
    screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, controls_y))
    
    # Draw arrow keys
    arrow_y = controls_y + 35
    # Left arrow
    pygame.draw.polygon(screen, WHITE, [(120, arrow_y), (140, arrow_y - 10), (140, arrow_y + 10)])
    # Right arrow  
    pygame.draw.polygon(screen, WHITE, [(360, arrow_y), (340, arrow_y - 10), (340, arrow_y + 10)])
    
    controls_text = font_small.render("Gerakkan Mobil", True, WHITE)
    screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, arrow_y - 8))
    
    # Power-ups section with colored boxes
    powerup_y = 480
    powerup_title = font_small.render("POWER-UPS:", True, YELLOW)
    screen.blit(powerup_title, (WIDTH//2 - powerup_title.get_width()//2, powerup_y))
    
    # Shield
    pygame.draw.circle(screen, BLUE, (100, powerup_y + 40), 18)
    shield_text = font_small.render("S", True, WHITE)
    screen.blit(shield_text, (94, powerup_y + 28))
    shield_label = font_small.render("Shield", True, WHITE)
    screen.blit(shield_label, (75, powerup_y + 60))
    
    # Slow
    pygame.draw.circle(screen, YELLOW, (WIDTH//2, powerup_y + 40), 18)
    slow_text = font_small.render("T", True, BLACK)
    screen.blit(slow_text, (WIDTH//2 - 6, powerup_y + 28))
    slow_label = font_small.render("Slow", True, WHITE)
    screen.blit(slow_label, (WIDTH//2 - 25, powerup_y + 60))
    
    # Boost
    pygame.draw.circle(screen, GREEN, (380, powerup_y + 40), 18)
    boost_text = font_small.render("B", True, WHITE)
    screen.blit(boost_text, (374, powerup_y + 28))
    boost_label = font_small.render("Boost", True, WHITE)
    screen.blit(boost_label, (355, powerup_y + 60))
    
    # High score with trophy
    if high_score > 0:
        hs_y = 590
        pygame.draw.rect(screen, (60, 40, 0), (WIDTH//2 - 100, hs_y - 5, 200, 35), border_radius=5)
        pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 100, hs_y - 5, 200, 35), 2, border_radius=5)
        
        trophy = font_medium.render("🏆", True, YELLOW)
        screen.blit(trophy, (WIDTH//2 - 80, hs_y - 5))
        
        hs_text = font_small.render(f"High Score: {high_score}", True, YELLOW)
        screen.blit(hs_text, (WIDTH//2 - 35, hs_y))

def draw_game_over():
    # Animated road background  
    screen.fill((40, 40, 40))
    
    pygame.draw.rect(screen, (255, 255, 255), (50, 0, 8, HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 58, 0, 8, HEIGHT))
    
    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Game Over text with red glow
    for offset in [(3, 3), (-3, -3), (3, -3), (-3, 3)]:
        shadow = font_large.render("GAME OVER", True, (80, 0, 0))
        screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + offset[0], 150 + offset[1]))
    
    game_over_text = font_large.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, 150))
    
    # Score panel
    score_panel = pygame.Rect(WIDTH//2 - 150, 250, 300, 100)
    pygame.draw.rect(screen, (20, 20, 20), score_panel, border_radius=15)
    pygame.draw.rect(screen, YELLOW, score_panel, 3, border_radius=15)
    
    score_label = font_small.render("SKOR AKHIR", True, WHITE)
    screen.blit(score_label, (WIDTH//2 - score_label.get_width()//2, 265))
    
    score_text = font_large.render(str(score), True, YELLOW)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 295))
    
    # New high score celebration
    if score == high_score and score > 0:
        for i in range(5):
            star_x = WIDTH//2 - 100 + i * 50
            star_text = font_medium.render("★", True, YELLOW)
            screen.blit(star_text, (star_x, 370))
        
        new_hs = font_medium.render("REKOR BARU!", True, YELLOW)
        screen.blit(new_hs, (WIDTH//2 - new_hs.get_width()//2, 410))
    
    # Restart button
    restart_rect = pygame.Rect(WIDTH//2 - 130, 470, 260, 50)
    pygame.draw.rect(screen, (0, 80, 0), restart_rect, border_radius=10)
    pygame.draw.rect(screen, GREEN, restart_rect, 3, border_radius=10)
    
    restart_text = font_medium.render("ENTER - Main Lagi", True, WHITE)
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 480))
    
    # Menu button
    menu_rect = pygame.Rect(WIDTH//2 - 100, 540, 200, 45)
    pygame.draw.rect(screen, (40, 40, 40), menu_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, menu_rect, 2, border_radius=10)
    
    menu_text = font_small.render("ESC - Menu Utama", True, WHITE)
    screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, 550))

def draw_hud():
    score_text = font_small.render(f"Skor: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    level_text = font_small.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (10, 40))
    
    lives_text = font_small.render(f"Nyawa: {player_lives}", True, RED)
    screen.blit(lives_text, (WIDTH - 120, 10))
    
    if shield_active:
        shield_text = font_small.render(f"Shield: {shield_timer//60}s", True, BLUE)
        screen.blit(shield_text, (WIDTH - 150, 40))
    
    if slow_active:
        slow_text = font_small.render(f"Slow: {slow_timer//60}s", True, YELLOW)
        screen.blit(slow_text, (WIDTH - 150, 70))
        
    if boost_active:
        boost_text = font_small.render(f"Boost: {boost_timer//60}s", True, GREEN)
        screen.blit(boost_text, (WIDTH - 150, 100))

def draw_pause():
    # Draw semi-transparent overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    
    # Pause panel
    panel = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 100, 300, 200)
    pygame.draw.rect(screen, (30, 30, 30), panel, border_radius=15)
    pygame.draw.rect(screen, YELLOW, panel, 4, border_radius=15)
    
    # Pause icon (two bars)
    pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 30, HEIGHT//2 - 60, 20, 50), border_radius=3)
    pygame.draw.rect(screen, YELLOW, (WIDTH//2 + 10, HEIGHT//2 - 60, 20, 50), border_radius=3)
    
    pause_text = font_large.render("PAUSE", True, YELLOW)
    screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 + 10))
    
    continue_text = font_small.render("P - Lanjutkan", True, WHITE)
    screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 65))
    
    menu_text = font_small.render("ESC - Menu", True, WHITE)
    screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 95))

def draw_winner():
    global winner_animation_time, confetti_particles
    
    # Animated background
    screen.fill((20, 20, 50))
    
    # Gradient effect
    for i in range(HEIGHT):
        alpha = int(100 * (i / HEIGHT))
        color = (20 + alpha, 20 + alpha, 50 + alpha)
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))
    
    winner_animation_time += 1
    
    # Spawn confetti
    if winner_animation_time % 3 == 0 and len(confetti_particles) < 200:
        for _ in range(5):
            confetti_particles.append(Confetti(random.randint(0, WIDTH), -10))
    
    # Update and draw confetti
    for confetti in confetti_particles[:]:
        confetti.update()
        if confetti.y > HEIGHT:
            confetti_particles.remove(confetti)
        else:
            confetti.draw()
    
    # Draw giant trophy
    trophy_y = 120 + math.sin(winner_animation_time * 0.05) * 10
    
    # Trophy base
    pygame.draw.rect(screen, (184, 134, 11), (WIDTH//2 - 60, trophy_y + 100, 120, 20), border_radius=5)
    pygame.draw.rect(screen, (218, 165, 32), (WIDTH//2 - 50, trophy_y + 110, 100, 15))
    
    # Trophy stem
    pygame.draw.rect(screen, (184, 134, 11), (WIDTH//2 - 20, trophy_y + 60, 40, 50))
    
    # Trophy cup
    points = [
        (WIDTH//2 - 50, trophy_y + 60),
        (WIDTH//2 - 60, trophy_y),
        (WIDTH//2 - 40, trophy_y - 20),
        (WIDTH//2 + 40, trophy_y - 20),
        (WIDTH//2 + 60, trophy_y),
        (WIDTH//2 + 50, trophy_y + 60)
    ]
    pygame.draw.polygon(screen, (255, 215, 0), points)
    pygame.draw.polygon(screen, (218, 165, 32), points, 4)
    
    # Trophy handles
    pygame.draw.circle(screen, (255, 215, 0), (WIDTH//2 - 70, trophy_y + 20), 15, 5)
    pygame.draw.circle(screen, (255, 215, 0), (WIDTH//2 + 70, trophy_y + 20), 15, 5)
    
    # Trophy shine
    pygame.draw.circle(screen, (255, 255, 200), (WIDTH//2 - 20, trophy_y - 5), 8)
    pygame.draw.circle(screen, (255, 255, 200), (WIDTH//2 + 10, trophy_y + 10), 5)
    
    # Winner text with animation
    pulse = 1 + 0.15 * math.sin(winner_animation_time * 0.1)
    winner_size = int(72 * pulse)
    winner_font = pygame.font.SysFont(None, winner_size)
    
    # Shadow
    for offset in [(4, 4), (-4, -4), (4, -4), (-4, 4)]:
        shadow = winner_font.render("WINNER!", True, (100, 50, 0))
        screen.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + offset[0], 35 + offset[1]))
    
    winner_text = winner_font.render("WINNER!", True, YELLOW)
    screen.blit(winner_text, (WIDTH//2 - winner_text.get_width()//2, 35))
    
    # Congratulations message
    congrats = font_medium.render("Selamat! Anda Menyelesaikan", True, WHITE)
    screen.blit(congrats, (WIDTH//2 - congrats.get_width()//2, 290))
    
    level_text = font_medium.render("Semua 5 Level!", True, GREEN)
    screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 330))
    
    # Stars animation
    for i in range(5):
        star_x = WIDTH//2 - 100 + i * 50
        star_y = 380 + math.sin(winner_animation_time * 0.1 + i * 0.5) * 10
        star_size = 30 + math.sin(winner_animation_time * 0.15 + i) * 5
        
        # Draw star
        star_points = []
        for j in range(10):
            angle = math.radians(j * 36 - 90)
            radius = star_size if j % 2 == 0 else star_size / 2
            px = star_x + math.cos(angle) * radius
            py = star_y + math.sin(angle) * radius
            star_points.append((px, py))
        
        pygame.draw.polygon(screen, YELLOW, star_points)
        pygame.draw.polygon(screen, (218, 165, 32), star_points, 2)
    
    # Final score panel
    score_panel = pygame.Rect(WIDTH//2 - 140, 460, 280, 80)
    pygame.draw.rect(screen, (30, 30, 60), score_panel, border_radius=15)
    pygame.draw.rect(screen, YELLOW, score_panel, 3, border_radius=15)
    
    final_label = font_small.render("SKOR AKHIR", True, WHITE)
    screen.blit(final_label, (WIDTH//2 - final_label.get_width()//2, 475))
    
    final_score = font_medium.render(str(score), True, YELLOW)
    screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, 505))
    
    # Buttons
    play_again_rect = pygame.Rect(WIDTH//2 - 120, 565, 240, 45)
    pygame.draw.rect(screen, (0, 100, 0), play_again_rect, border_radius=10)
    pygame.draw.rect(screen, GREEN, play_again_rect, 3, border_radius=10)
    
    play_text = font_small.render("ENTER - Main Lagi", True, WHITE)
    screen.blit(play_text, (WIDTH//2 - play_text.get_width()//2, 573))
    
    menu_rect = pygame.Rect(WIDTH//2 - 90, 620, 180, 35)
    pygame.draw.rect(screen, (40, 40, 40), menu_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, menu_rect, 2, border_radius=10)
    
    menu_text = font_small.render("ESC - Menu", True, WHITE)
    screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, 625))

# ===========================
# Game loop
# ===========================
running = True
reset_game()

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = PLAYING
                    
            elif game_state == PLAYING:
                if event.key == pygame.K_p:
                    game_state = PAUSED
                    
            elif game_state == PAUSED:
                if event.key == pygame.K_p:
                    game_state = PLAYING
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    
            elif game_state == GAME_OVER:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = PLAYING
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    
            elif game_state == WINNER:
                if event.key == pygame.K_RETURN:
                    reset_game()
                    game_state = PLAYING
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
    
    if game_state == MENU:
        draw_menu()
        
    elif game_state == PLAYING:
        # Draw continuous road background
        screen.fill((40, 40, 40))  # Dark gray asphalt
        
        # Draw white side lines (road edges)
        pygame.draw.rect(screen, (255, 255, 255), (50, 0, 8, HEIGHT))
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 58, 0, 8, HEIGHT))
        
        # Animated center dashed lines
        line_offset += line_speed
        if line_offset >= 80:
            line_offset = 0
        
        # Draw yellow center dashed lines
        for i in range(-80, HEIGHT + 80, 80):
            y_pos = i + line_offset
            pygame.draw.rect(screen, (255, 200, 0), (WIDTH//2 - 4, y_pos, 8, 50))
        
        # Input player
        keys = pygame.key.get_pressed()
        speed = player_speed * 1.5 if boost_active else player_speed
        
        if keys[pygame.K_LEFT] and player_x > 60:
            player_x -= speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width - 60:
            player_x += speed
        
        # Spawn
        spawn_enemy()
        spawn_powerup()
        
        # Update enemies
        for enemy in enemies[:]:
            enemy.update()
            if enemy.y > HEIGHT:
                enemies.remove(enemy)
                score += 10
                
                # Check for level up (max level 5)
                if score % 100 == 0 and level < 5:
                    level += 1
                
                # Check for winner (completed level 5)
                if level >= 5 and score >= 500:
                    if score > high_score:
                        high_score = score
                    game_state = WINNER
        
        # Update powerups
        for powerup in powerups[:]:
            powerup.update()
            if powerup.y > HEIGHT:
                powerups.remove(powerup)
        
        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
        
        # Update timers
        if shield_active:
            shield_timer -= 1
            if shield_timer <= 0:
                shield_active = False
                
        if slow_active:
            slow_timer -= 1
            if slow_timer <= 0:
                slow_active = False
                
        if boost_active:
            boost_timer -= 1
            if boost_timer <= 0:
                boost_active = False
        
        # Collision with enemies
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        
        for enemy in enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                if shield_active:
                    enemies.remove(enemy)
                    create_explosion(enemy.x + enemy_width//2, enemy.y + enemy_height//2, BLUE)
                    score += 20
                else:
                    enemies.remove(enemy)
                    create_explosion(player_x + player_width//2, player_y + player_height//2, RED)
                    player_lives -= 1
                    
                    if player_lives <= 0:
                        if score > high_score:
                            high_score = score
                        game_state = GAME_OVER
        
        # Collision with powerups
        for powerup in powerups[:]:
            if player_rect.colliderect(powerup.get_rect()):
                powerups.remove(powerup)
                create_explosion(powerup.x + powerup.size//2, powerup.y + powerup.size//2, powerup.color)
                
                if powerup.type == POWERUP_SHIELD:
                    shield_active = True
                    shield_timer = 300
                elif powerup.type == POWERUP_SLOW:
                    slow_active = True
                    slow_timer = 300
                else:
                    boost_active = True
                    boost_timer = 180
        
        # Draw everything
        for enemy in enemies:
            enemy.draw()
        
        for powerup in powerups:
            powerup.draw()
        
        for particle in particles:
            particle.draw()
        
        # Draw player with shield
        if shield_active:
            pygame.draw.circle(screen, BLUE, (player_x + player_width//2, player_y + player_height//2), 50, 3)
        
        screen.blit(player_img, (player_x, player_y))
        
        draw_hud()
        
    elif game_state == PAUSED:
        draw_pause()
        
    elif game_state == GAME_OVER:
        draw_game_over()
        
    elif game_state == WINNER:
        draw_winner()
    
    pygame.display.update()

pygame.quit()
sys.exit()