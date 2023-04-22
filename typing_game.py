import pygame
import random
import sys
import os
import math
import re
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# 配置项
HEALTH = 6
MAX_LEVEL = 4  # 最大关卡数
SCORES_PER_LEVEL = 50  # 每过一关需要的分数
SPEED_MOD = 1 / 3

ASSET_DIR = "assets"
IMAGE_DIR = os.path.join(ASSET_DIR, "image")
SOUND_DIR = os.path.join(ASSET_DIR, "sound")
FONT_DIR = os.path.join(ASSET_DIR, "font")
DATA_DIR = os.path.join(ASSET_DIR, "data")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 一些工具函数
def scale_x(x):
    return x * SCALE_X

def scale_y(y):
    return y * SCALE_Y

def scale_min_xy(v):
    return int(v * min(SCALE_X, SCALE_Y))

# TODO: 使用更多颜色的激光
# TODO：设置界面，可以设置命数，难度（速度，字母数量），音效开关，背景音乐开关

# 创建游戏窗口
BASE_WIDTH, BASE_HEIGHT = 800, 600

screen_info = pygame.display.Info()
WIDTH, HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))

SCALE_X = WIDTH / BASE_WIDTH
SCALE_Y = HEIGHT / BASE_HEIGHT

pygame.display.set_caption('Typing Game for Kids')

# 加载资源
background_image = pygame.image.load(os.path.join(IMAGE_DIR, "saturn_scifi_background.jpg"))
background = pygame.transform.scale(background_image, (WIDTH, HEIGHT))


explosion_image = pygame.image.load(os.path.join(IMAGE_DIR, "explosion.png"))
explosion_image = pygame.transform.scale(explosion_image, (scale_x(100), scale_y(100)))

cannon_image = pygame.image.load(os.path.join(IMAGE_DIR, "cannon_icon.png"))
cannon_image = pygame.transform.scale(cannon_image, (scale_x(40), scale_y(40)))

shoot_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "shoot.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "explosion.wav"))
wrong_key_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "wrong_key.mp3"))   # 添加错误按键音效

# 设置字体
font = pygame.font.Font(os.path.join(FONT_DIR, "Orbitron-VariableFont_wght.ttf"), scale_min_xy(36))

def load_words(directory):
    """
    加载指定目录下的所有top单词文件，返回一个以文件中的单词数为key，单词列表为value的字典
    """
    words = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:
            # 如果文件名匹配指定文件名, 则处理这个文件
            match = re.match(r'top_(\d+)_letter.*\.txt', filename)
            if match:
                letters = int(match.group(1))
                words[letters] = [line.split(':')[0] for line in f.readlines()]
                print(words[letters][:10])
    return words

class Invader:
    # 标记这个为static 变量
    real_words = load_words(os.path.join(DATA_DIR, "words"))  # 加载单词库

    def __init__(self, level):
        # 根据关卡生成不同数量的字母
        letter_count = random.randint(1, level)
        if letter_count == 1:
            self.text = random.choice(list('abcdefghijklmnopqrstuvwxyz'))
        else:
            self.text = random.choice(Invader.real_words[letter_count])

        self.speed = scale_y(random.uniform(1, level) * SPEED_MOD)
        self.angle = random.uniform(-45, 45)
        self.pos = [random.randint(scale_x(100), WIDTH - scale_x(180)), 0]
        self.size = scale_min_xy(random.uniform(50, 70))
        # TODO: 考虑使用一些特效，比如粗体字，下落速度更快，但是得分更高
        self.text_render = font.render(self.text, True, BLACK)
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
        """
        """
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
    def __init__(self, target_pos):
        self.target_pos = target_pos
        self.pos = [WIDTH / 2, HEIGHT * 4 / 5]
        self.speed = scale_y(10)
        self.image = pygame.image.load(os.path.join(IMAGE_DIR, "laser_beam.png"))
        self.image = pygame.transform.scale(self.image, (scale_x(50), scale_y(50)))
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
        # 注意：这里需要使用负角度，因为pygame的坐标系是从上到下的
        rotated_image = pygame.transform.rotate(self.image, -angle)
        screen.blit(rotated_image, self.pos)

def game_over(score, invaders):
    """
    游戏结束函数，显示游戏结束画面和得分，等待用户按下R键重新开始游戏。
    :param score: 当前游戏得分
    :param invaders: 当前游戏中的入侵者列表
    """

    # 清空入侵者列表
    invaders.clear()

    # 在原来背景上显示
    screen.blit(background, (0, 0))

    # 清除 health 显示
    #for i in range(HEALTH):
    #    pygame.draw.rect(screen, (0, 0, 0), (scale_x(10) + i * scale_x(50), scale_y(10), scale_x(40), scale_y(40)))

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
    暂停函数，显示暂停画面，等待用户按下R键继续游戏。
    """
    pause_text = font.render('Game Paused', True, BLACK)
    restart_text = font.render('Press Q to quit, other keys to resume', True, BLACK)
    # 在原来背景上显示
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
    level = 1  # 添加关卡变量

    typed_text = ''

    # 加载并循环播放背景音乐
    pygame.mixer.music.load(os.path.join(SOUND_DIR, 'neon-gaming-128925.mp3'))
    pygame.mixer.music.play(-1)

    while not gameover:
        screen.blit(background, (0, 0))

        # 更新计分牌
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, ((WIDTH - scale_x(180)), scale_y(10)))

        # 更新当前几条命的数目
        for i in range(HEALTH - invaders_reached_ground):
            screen.blit(cannon_image, (scale_x(10) + i * scale_x(50), scale_y(10)))

        # 添加入侵者
        if len(invaders) < max_invaders and random.random() < 0.5:
            invaders.append(Invader(level))

        # 去掉已经爆炸后的入侵者
        _invaders = invaders.copy()
        for invader in _invaders:
            if invader.exploded:
                invaders.remove(invader)

        # 更新入侵者的状态，如果有入侵者到达地面则游戏结束
        for invader in invaders:
            invader.draw()
            if invader.update():
                invaders_reached_ground += 1
                invader.explode()
                if invaders_reached_ground >= HEALTH:
                    gameover = True
                    break

        # 更新激光束的状态，并在击中目标时播放爆炸效果
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
                                laser_beams.append(LaserBeam(invader.pos))
                                typed_text = ''
                                break

                    if not found_match:
                        if i == 0:   # 第一遍没有匹配上，还要以它为首字母再匹配一次
                            wrong_key_sound.play()   # 播放错误按键音效
                            typed_text = event.unicode   # 重新开始输入
                        else:
                            typed_text = ''
                    else:
                        break


        # 在屏幕上显示用户当前输入的按键内容
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
