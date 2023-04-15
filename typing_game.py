import pygame
import random
import sys
import math
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# TODO: 把所有尺寸改为相对值
# 定义屏幕尺寸
WIDTH, HEIGHT = 800, 600

# 创建游戏窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Typing Game for Kids')

# 加载资源
background_image = pygame.image.load("sky_background.jpg")
background = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
#cannon = pygame.image.load("cannon.png")
#cannon = pygame.transform.scale(cannon, (100, 100))

explosion_image = pygame.image.load("explosion.png")
explosion_image = pygame.transform.scale(explosion_image, (80, 80))

shoot_sound = pygame.mixer.Sound("shoot.wav")
explosion_sound = pygame.mixer.Sound("explosion.wav")

# 设置字体
# TODO: Use a comic like font
font = pygame.font.Font(None, 36)

class Invader:
    def __init__(self):
        # TODO: Try to generate normal word here
        self.text = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(random.randint(1, 3)))
        self.speed = random.uniform(1, 4)
        self.angle = random.uniform(-45, 45)
        self.pos = [random.randint(50, WIDTH - 150), 0]
        self.size = random.uniform(50,70)
        # TODO: randomize color
        self.text_render = font.render(self.text, True, BLACK)
        self.explosion = False
        self.explosion_timer = None
        self.exploded = False

    def update(self):
        if not self.explosion:
            new_x = self.pos[0] + self.speed * math.sin(math.radians(self.angle))
            self.pos[0] = max(50, min(new_x, WIDTH - 150))
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
    game_over_text = font.render(f'Game Over! Your score: {score}', True, BLACK)
    restart_text = font.render('Press R to restart the game', True, BLACK)
    # 这里修改为清除所有Invaders，然后在原来背景上显示
    screen.fill(WHITE)
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

    typed_text = ''

    while not gameover:
        screen.blit(background, (0, 0))
        #screen.blit(cannon, (WIDTH / 2 - 50, HEIGHT * 4/5))

        # 更新计分牌
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, (WIDTH - 200, 10))

        # 添加入侵者
        #if len(invaders) < max_invaders and random.random() < 0.01:
        if len(invaders) < max_invaders:
            invaders.append(Invader())

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
                if invaders_reached_ground > 3:
                    gameover = True
                    break

        # TODO: 这里按键也需要修改一下
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                typed_text += event.unicode
                if typed_text == event.unicode:
                    shoot_sound.play()

                for invader in invaders:
                    if invader.text == typed_text:
                        invaders.remove(invader)
                        score += len(invader.text)
                        typed_text = ''
                        break
            elif event.type == KEYUP:
                typed_text = ''

        clock.tick(30)
        pygame.display.update()

    game_over(score)

if __name__ == '__main__':
    while True:
        main()