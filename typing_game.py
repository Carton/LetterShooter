import pygame
import random
import sys
import os
import math
import re
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# Configuration
HEALTH = 6
MAX_LEVEL = 4  # Maximum number of levels
SCORES_PER_LEVEL = 50  # The score required to pass each level
SPEED_MOD = 1 / 3

ASSET_DIR = "assets"
IMAGE_DIR = os.path.join(ASSET_DIR, "image")
SOUND_DIR = os.path.join(ASSET_DIR, "sound")
FONT_DIR = os.path.join(ASSET_DIR, "font")
DATA_DIR = os.path.join(ASSET_DIR, "data")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Some utility functions
def scale_x(x):
    return x * SCALE_X

def scale_y(y):
    return y * SCALE_Y

def scale_min_xy(v):
    return int(v * min(SCALE_X, SCALE_Y))

# TODO: Use more colors for the laser
# TODO: Settings interface, can set the number of lives, difficulty (speed, number of letters), sound effect switch, background music switch

# Create game window
BASE_WIDTH, BASE_HEIGHT = 800, 600

screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))

SCALE_X = WIDTH / BASE_WIDTH
SCALE_Y = HEIGHT / BASE_HEIGHT

pygame.display.set_caption('Typing Game for Kids')

# Load resources
background_image = pygame.image.load(os.path.join(IMAGE_DIR, "saturn_scifi_background.jpg"))
background = pygame.transform.scale(background_image, (WIDTH, HEIGHT))


explosion_image = pygame.image.load(os.path.join(IMAGE_DIR, "explosion.png"))
explosion_image = pygame.transform.scale(explosion_image, (scale_x(100), scale_y(100)))

cannon_image = pygame.image.load(os.path.join(IMAGE_DIR, "cannon_icon.png"))
cannon_image = pygame.transform.scale(cannon_image, (scale_x(40), scale_y(40)))

shoot_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "shoot.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "explosion.wav"))
wrong_key_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "wrong_key.mp3"))   # Add wrong key sound effect

# Set font
font = pygame.font.Font(os.path.join(FONT_DIR, "Orbitron-VariableFont_wght.ttf"), scale_min_xy(36))

def load_words(directory):
    """
    Load all top word files in the specified directory.
    Returns a dictionary with the number of letters as the key and the list of words as the value
    """
    words = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:
            # If the file name matches the specified file name, process this file
            match = re.match(r'top_(\d+)_letter.*\.txt', filename)
            if match:
                letters = int(match.group(1))
                words[letters] = [line.split(':')[0] for line in f.readlines()]
    return words

class Invader:
    real_words = load_words(os.path.join(DATA_DIR, "words"))  # Load word library

    def __init__(self, level):
        # Generate different numbers of letters based on the level
        letter_count = random.randint(1, level)
        if letter_count == 1:
            self.text = random.choice(list('abcdefghijklmnopqrstuvwxyz'))
        else:
            self.text = random.choice(Invader.real_words[letter_count])

        self.speed = scale_y(random.uniform(1, level) * SPEED_MOD)
        self.angle = random.uniform(-45, 45)
        self.pos = [random.randint(scale_x(100), WIDTH - scale_x(180)), 0]

        # TODO: Consider using some special effects, such as bold text, faster falling speed, but higher scores
        invader_font = pygame.font.Font(os.path.join(FONT_DIR, "Orbitron-VariableFont_wght.ttf"), scale_min_xy(random.uniform(30, 36)))
        self.text_render = invader_font.render(self.text, True, BLACK)
        self.size = self.text_render.get_rect().size

        self.explosion = False
        self.explosion_timer = None
        self.exploded = False
        self.laser_hit = False

    def update(self):
        if not self.explosion:
            new_x = self.pos[0] + self.speed * math.sin(math.radians(self.angle))
            self.pos[0] = max(scale_x(50), min(new_x, WIDTH - scale_x(50)))
            self.pos[1] += self.speed
            return self.pos[1] > HEIGHT * 4/5
        else:
            if self.explosion_timer is not None and pygame.time.get_ticks() - self.explosion_timer > 500:
                self.exploded = True
                self.explosion_timer = None
            return False

    def draw(self):
        if self.explosion:
            if self.explosion_timer:
                screen.blit(explosion_image, self.pos)
        else:
            screen.blit(self.text_render, self.pos)

    def explode(self):
        self.explosion = True
        self.explosion_timer = pygame.time.get_ticks()
        explosion_sound.play()


class LaserBeam:
    size = (scale_x(50), scale_x(50))
    images = [pygame.image.load(os.path.join(IMAGE_DIR, 'laser_beam', f"{i}.png")) for i in range(5)]
    # FIXME: Why can't we use size here?
    images = [pygame.transform.scale(image, (scale_x(50), scale_x(50))) for image in images]

    def __init__(self, target):
        target_center_x = target.pos[0] + target.size[0] / 2 - LaserBeam.size[0] / 2
        target_center_y = target.pos[1] + target.size[1] / 2 - LaserBeam.size[1] / 2
        self.target_pos = [target_center_x, target_center_y]
        print(target.pos, target.size, self.target_pos)

        self.pos = [WIDTH / 2 + scale_x(50), (HEIGHT * 4 / 5) + scale_x(50)]
        self.speed = scale_y(10)
        # choose random laser beam image
        self.image = random.choice(LaserBeam.images)
        self.active = True

    def update(self):
        direction = [self.target_pos[0] - self.pos[0], self.target_pos[1] - self.pos[1]]
        distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2)
        if distance <= self.speed:
            self.active = False
            return True
        direction_normalized = [direction[0] / distance, direction[1] / distance]
        self.pos[0] += direction_normalized[0] * self.speed
        self.pos[1] += direction_normalized[1] * self.speed
        return False

    def calculate_angle(self, target_pos):
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        return angle

    def draw(self):
        angle = self.calculate_angle(self.target_pos)
        # Note: Use a negative angle here because pygame's coordinate system is from top to bottom
        rotated_image = pygame.transform.rotate(self.image, -angle)
        screen.blit(rotated_image, self.pos)

def game_over(score, invaders):
    """
    Game over function. Display the game over screen and score and
    wait for the user to press the R key to restart the game.

    :param score: current game score
    :param invaders: list of invaders in the current game
    """

    # Clear the list of invaders
    invaders.clear()

    # Display on the original background
    screen.blit(background, (0, 0))

    # Clear health display

    game_over_text = font.render(f'Game Over! Your score: {score}', True, BLACK)
    restart_text = font.render('Press R to restart the game', True, BLACK)

    screen.blit(game_over_text, (WIDTH / 2 - scale_x(200), HEIGHT / 2 - scale_y(50)))
    screen.blit(restart_text, (WIDTH / 2 - scale_x(200), HEIGHT / 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_r:
                return


def pause():
    """
    Pause function. Display the pause screen, and wait for
    the user to press the R key to continue the game.
    """
    pause_text = font.render('Game Paused', True, BLACK)
    restart_text = font.render('Press Q to quit, other keys to resume', True, BLACK)
    # Display on the original background
    screen.blit(pause_text, (WIDTH / 2 - scale_x(90), HEIGHT / 2 - scale_y(50)))
    screen.blit(restart_text, (WIDTH / 2 - scale_x(250), HEIGHT / 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                return


def main():
    clock = pygame.time.Clock()

    invaders = []
    laser_beams = []
    score = 0
    max_invaders = 3
    gameover = False
    invaders_reached_ground = 0
    level = 1  # Add level variable

    typed_text = ''

    # Load and loop background music
    pygame.mixer.music.load(os.path.join(SOUND_DIR, 'neon-gaming-128925.mp3'))
    pygame.mixer.music.play(-1)

    while not gameover:
        screen.blit(background, (0, 0))

        # Update scoreboard
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, ((WIDTH - scale_x(180)), scale_y(10)))

        # Update the number of current lives
        for i in range(HEALTH - invaders_reached_ground):
            screen.blit(cannon_image, (scale_x(10) + i * scale_x(50), scale_y(10)))

        # Add invaders
        if len(invaders) < max_invaders and random.random() < 0.5:
            invaders.append(Invader(level))

        # Remove invaders that have already exploded
        _invaders = invaders.copy()
        for invader in _invaders:
            if invader.exploded:
                invaders.remove(invader)

        # Update the status of the invaders, if an invader reaches the ground, the game is over
        for invader in invaders:
            invader.draw()
            if invader.update():
                invaders_reached_ground += 1
                invader.explode()
                if invaders_reached_ground >= HEALTH:
                    gameover = True
                    break

        # Update the status of laser beams and play explosion effect when hitting targets
        for beam in laser_beams:
            beam.draw()
            if beam.update():
                for invader in invaders:
                    if invader.laser_hit:
                        invader.explode()
                        score += len(invader.text)
                        invaders.remove(invader)
                laser_beams.remove(beam)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pause()
            elif event.type == KEYDOWN:
                typed_text += event.unicode
                found_match = False

                for i in range(2):
                    for invader in invaders:
                        if invader.text.startswith(typed_text):
                            found_match = True
                            if invader.text == typed_text:
                                shoot_sound.play()
                                invader.laser_hit = True
                                laser_beams.append(LaserBeam(invader))
                                typed_text = ''
                                break

                    if not found_match:
                        if i == 0:   # If not matched in the first round, match again with it as the first letter
                            wrong_key_sound.play()   # Play the sound effect of pressing the wrong key
                            typed_text = event.unicode   # Start typing again
                        else:
                            typed_text = ''
                    else:
                        break


        # Display the current keystrokes entered by the user on the screen
        typed_text_render = font.render(typed_text, True, BLACK)
        screen.blit(typed_text_render, (WIDTH / 2 - scale_x(30), HEIGHT * 4/5 + scale_y(30)))

        if score // SCORES_PER_LEVEL >= level:
            level += 1
        level = min(level, MAX_LEVEL)

        clock.tick(120)
        pygame.display.update()

    game_over(score, invaders)


if __name__ == '__main__':
    while True:
        main()
