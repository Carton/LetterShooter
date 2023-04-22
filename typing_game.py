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

ASSET_DIR = "assets"
IMAGE_DIR = os.path.join(ASSET_DIR, "image")
SOUND_DIR = os.path.join(ASSET_DIR, "sound")
FONT_DIR = os.path.join(ASSET_DIR, "font")
DATA_DIR = os.path.join(ASSET_DIR, "data")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# TODO: 把所有尺寸改为相对值
# TODO: 考虑发射激光特效来集中入侵者
# 定义屏幕尺寸
WIDTH, HEIGHT = 800, 600

# 创建游戏窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Typing Game for Kids')

# 加载资源
background_image = pygame.image.load(os.path.join(IMAGE_DIR, "saturn_scifi_background.jpg"))
background = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
#cannon = pygame.image.load("cannon.png")
#cannon = pygame.transform.scale(cannon, (100, 100))

explosion_image = pygame.image.load(os.path.join(IMAGE_DIR, "explosion.png"))
explosion_image = pygame.transform.scale(explosion_image, (100, 100))

cannon_image = pygame.image.load(os.path.join(IMAGE_DIR, "cannon_icon.png"))
cannon_image = pygame.transform.scale(cannon_image, (40, 40))

shoot_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "shoot.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "explosion.wav"))
wrong_key_sound = pygame.mixer.Sound(os.path.join(SOUND_DIR, "wrong_key.mp3"))  # 添加错误按键音效

# 设置字体
font = pygame.font.Font(os.path.join(FONT_DIR, "Orbitron-VariableFont_wght.ttf"), 36)

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

        self.speed = random.uniform(1, level)
        self.angle = random.uniform(-45, 45)
        self.pos = [random.randint(100, WIDTH - 180), 0]
        self.size = random.uniform(50, 70)
        # TODO: 考虑使用一些特效，比如粗体字，下落速度更快，但是得分更高
        self.text_render = font.render(self.text, True, BLACK)
        self.explosion = False
        self.explosion_timer = None
        self.exploded = False

    def update(self):
        if not self.explosion:
            new_x = self.pos[0] + self.speed * math.sin(math.radians(self.angle))
            self.pos[0] = max(50, min(new_x, WIDTH - 50))
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

def game_over(score):
    """
    游戏结束函数，显示游戏结束画面和得分，等待用户按下R键重新开始游戏。
    :param score: 当前游戏得分
    """
    game_over_text = font.render(f'Game Over! Your score: {score}', True, BLACK)
    restart_text = font.render('Press R to restart the game', True, BLACK)
    # 在原来背景上显示

    screen.blit(game_over_text, (WIDTH / 2 - 100, HEIGHT / 2 - 50))
    screen.blit(restart_text, (WIDTH / 2 - 100, HEIGHT / 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_r:
                return


def main():
    clock = pygame.time.Clock()

    invaders = []
    score = 0
    max_invaders = 3
    gameover = False
    invaders_reached_ground = 0
    level = 1  # 添加关卡变量

    typed_text = ''

    while not gameover:
        screen.blit(background, (0, 0))
        #screen.blit(cannon, (WIDTH / 2 - 50, HEIGHT * 4/5))

        # 更新计分牌
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, (WIDTH - 180, 10))

        # 更新当前几条命的数目
        for i in range(HEALTH - invaders_reached_ground):
            screen.blit(cannon_image, (10 + i * 50, 10))

        # 添加入侵者
        if len(invaders) < max_invaders and random.random() < 0.5:
            invaders.append(Invader(level))

        # 去掉已经爆炸后的入侵者
        invaders1 = invaders.copy()
        for invader in invaders1:
            if invader.exploded:
                invaders.remove(invader)

        for invader in invaders:
            invader.draw()
            if invader.update():
                invaders_reached_ground += 1
                invader.explode()
                if invaders_reached_ground >= HEALTH:
                    gameover = True
                    break

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                typed_text += event.unicode
                found_match = False

                for i in range(2):
                    for invader in invaders:
                        if invader.text.startswith(typed_text):
                            found_match = True
                            if invader.text == typed_text:
                                shoot_sound.play()
                                invaders.remove(invader)
                                score += len(invader.text)
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
        screen.blit(typed_text_render, (WIDTH / 2 - 50, HEIGHT * 4/5 + 50))

        if score // SCORES_PER_LEVEL >= level:
            level += 1
        level = min(level, MAX_LEVEL)

        clock.tick(40)
        pygame.display.update()

    game_over(score)


if __name__ == '__main__':
    while True:
        main()
