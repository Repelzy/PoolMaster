import math
import pygame
import pymunk
import pymunk.pygame_util

pygame.init()

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 720
PANEL_HEIGHT = 50

# Game Window
game_window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + PANEL_HEIGHT))
pygame.display.set_caption("Ultimate Pool")

# Physics Space
physics_space = pymunk.Space()
static_body = physics_space.static_body
draw_options = pymunk.pygame_util.DrawOptions(game_window)

# Clock
main_clock = pygame.time.Clock()
FPS = 120

# Game Variables
player_lives = 3
ball_radius = 36
shot_force = 0
pocket_radius = 66
max_shot_force = 10000
shot_force_direction = 1
game_active = True
cue_ball_pocketed = False
taking_shot = True
powering_up_shot = False
pocketed_balls = []

# Colors
BACKGROUND_COLOR = (50, 50, 50)
POWER_BAR_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)

# Fonts
regular_font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

# Load Images
cue_image = pygame.image.load("Assets/images/cue.png").convert_alpha()
table_image = pygame.image.load("Assets/images/table.png").convert_alpha()
ball_images = []
for i in range(1, 17):
    ball_image = pygame.image.load(f"Assets/images/ball_{i}.png").convert_alpha()
    ball_images.append(ball_image)


# Function for Outputting Text
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    game_window.blit(text_surface, (x, y))


# Function for Creating Balls
def create_ball(radius, position):
    body = pymunk.Body()
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.mass = 3
    shape.elasticity = 0.8
    pivot_joint = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
    pivot_joint.max_bias = 0
    pivot_joint.max_force = 1000
    physics_space.add(body, shape, pivot_joint)
    return shape


# Set Up Game Balls
balls = []
rows = 5

# Place Balls on Table
for col in range(5):
    for row in range(rows):
        position = (250 + (col * (ball_radius + 1)), 267 + (row * (ball_radius + 1)) + (col * ball_radius / 2))
        new_ball = create_ball(ball_radius / 2, position)
        balls.append(new_ball)
    rows -= 1

# Add Cue Ball
position = (888, WINDOW_HEIGHT / 2)
cue_ball = create_ball(ball_radius / 2, position)
balls.append(cue_ball)

# Define Pocket Positions
pockets = [
    (55, 63),
    (592, 48),
    (1134, 64),
    (55, 616),
    (592, 629),
    (1134, 616)
]

# Define Cushions
cushions = [
    [(88, 56), (109, 77), (555, 77), (564, 56)],
    [(621, 56), (630, 77), (1081, 77), (1102, 56)],
    [(89, 621), (110, 600), (556, 600), (564, 621)],
    [(622, 621), (630, 600), (1081, 600), (1102, 621)],
    [(56, 96), (77, 117), (77, 560), (56, 581)],
    [(1143, 96), (1122, 117), (1122, 560), (1143, 581)],
]


# Create Cushions
def create_cushion(poly_dims):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = ((0, 0))
    shape = pymunk.Poly(body, poly_dims)
    shape.elasticity = 0.8
    physics_space.add(body, shape)


for c in cushions:
    create_cushion(c)


# Create Pool Cue
class Cue():
    def __init__(self, position):
        self.original_image = cue_image
        self.angle = 0
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self, angle):
        self.angle = angle

    def draw(self, surface):
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        surface.blit(self.image,
                     (self.rect.centerx - self.image.get_width() / 2,
                      self.rect.centery - self.image.get_height() / 2))


cue = Cue(balls[-1].body.position)

# Create Power Bar
power_bar = pygame.Surface((10, 20))
power_bar.fill(POWER_BAR_COLOR)

# Main Game Loop
running = True
while running:

    main_clock.tick(FPS)
    physics_space.step(1 / FPS)

    # Fill Background
    game_window.fill(BACKGROUND_COLOR)

    # Draw Pool Table
    game_window.blit(table_image, (0, 0))

    # Check for Pocketed Balls
    for i, ball in enumerate(balls):
        for pocket in pockets:
            ball_x_dist = abs(ball.body.position[0] - pocket[0])
            ball_y_dist = abs(ball.body.position[1] - pocket[1])
            ball_dist = math.sqrt((ball_x_dist ** 2) + (ball_y_dist ** 2))
            if ball_dist <= pocket_radius / 2:
                if i == len(balls) - 1:
                    player_lives -= 1
                    cue_ball_pocketed = True
                    ball.body.position = (-100, -100)
                    ball.body.velocity = (0.0, 0.0)
                else:
                    physics_space.remove(ball.body)
                    balls.remove(ball)
                    pocketed_balls.append(ball_images[i])
                    ball_images.pop(i)

    # Draw Pool Balls
    for i, ball in enumerate(balls):
        game_window.blit(ball_images[i], (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius))

    # Check if All Balls Have Stopped Moving
    taking_shot = True
    for ball in balls:
        if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
            taking_shot = False

    # Draw Pool Cue
    if taking_shot == True and game_active == True:
        if cue_ball_pocketed == True:
            balls[-1].body.position = (888, WINDOW_HEIGHT / 2)
            cue_ball_pocketed = False

        mouse_pos = pygame.mouse.get_pos()
        cue.rect.center = balls[-1].body.position
        x_dist = balls[-1].body.position[0] - mouse_pos[0]
        y_dist = -(balls[-1].body.position[1] - mouse_pos[1])
        cue_angle = math.degrees(math.atan2(y_dist, x_dist))
        cue.update(cue_angle)
        cue.draw(game_window)

    # Power Up Pool Cue
    if powering_up_shot == True and game_active == True:
        shot_force += 100 * shot_force_direction
        if shot_force >= max_shot_force or shot_force <= 0:
            shot_force_direction *= -1

        for b in range(math.ceil(shot_force / 2000)):
            game_window.blit(power_bar,
                             (balls[-1].body.position[0] - 30 + (b * 15),
                              balls[-1].body.position[1] + 30))

    elif powering_up_shot == False and taking_shot == True:
        x_impulse = math.cos(math.radians(cue_angle))
        y_impulse = math.sin(math.radians(cue_angle))
        balls[-1].body.apply_impulse_at_local_point((shot_force * -x_impulse, shot_force * y_impulse), (0, 0))
        shot_force = 0
        shot_force_direction = 1

    # Draw Bottom Panel
    pygame.draw.rect(game_window, BACKGROUND_COLOR, (0, WINDOW_HEIGHT, WINDOW_WIDTH, PANEL_HEIGHT))
    draw_text("LIVES: " + str(player_lives), regular_font, TEXT_COLOR, WINDOW_WIDTH - 200, WINDOW_HEIGHT + 10)

    # Draw Potted Balls in Bottom Panel
    for i, ball in enumerate(pocketed_balls):
        game_window.blit(ball, (10 + (i * 50), WINDOW_HEIGHT + 10))

    # Check for Game Over
    if player_lives <= 0:
        draw_text("GAME OVER", large_font, TEXT_COLOR, WINDOW_WIDTH / 2 - 160, WINDOW_HEIGHT / 2 - 100)
        game_active = False

    # Check if Player Wins
    if len(balls) == 1:
        draw_text("VICTORY!", large_font, TEXT_COLOR, WINDOW_WIDTH / 2 - 160, WINDOW_HEIGHT / 2 - 100)
        game_active = False

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and taking_shot == True:
            powering_up_shot = True

        if event.type == pygame.MOUSEBUTTONUP and taking_shot == True:
            powering_up_shot = False

        if event.type == pygame.QUIT:
            running = False

    # physics_space.debug_draw(draw_options)
    pygame.display.update()

pygame.quit()
