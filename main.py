# 导入pygame库
import pygame
import random

# 初始化pygame
pygame.init()

# 设置窗口大小
size = (700, 500)
screen = pygame.display.set_mode(size)

# 设置窗口标题
pygame.display.set_caption("打字游戏")

# 设置颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# 设置字体
font = pygame.font.Font(None, 36)

# 设置计分牌
score = 0

# 设置游戏结束标志
game_over = False

# 设置入侵者
invader_list = []
for i in range(10):
    invader = {
        "x": random.randint(0, size[0] - 50),
        "y": random.randint(-500, -50),
        "letters": [chr(random.randint(65, 90)) for _ in range(random.randint(1, 3))],
        "speed": random.randint(1, 2) # 减慢入侵者下降速度
    }
    invader_list.append(invader)

# 设置大炮
cannon = {
    "x": size[0] // 2 - 25,
    "y": size[1] - 50,
    "letter": "",
    "cooldown": 0
}

# 游戏循环
while not game_over:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        elif event.type == pygame.KEYDOWN:
            if event.unicode.isalpha():
                cannon["letter"] += event.unicode
                if len(cannon["letter"]) > 3:
                    cannon["letter"] = cannon["letter"][-3:]
            elif event.key == pygame.K_BACKSPACE:
                cannon["letter"] = cannon["letter"][:-1]
            elif event.key == pygame.K_RETURN:
                for invader in invader_list:
                    if "".join(invader["letters"]) == cannon["letter"]:
                        invader_list.remove(invader)
                        score += 1
                        cannon["letter"] = ""
                        break
                else:
                    cannon["letter"] = ""

    # 更新入侵者位置
    for invader in invader_list:
        invader["y"] += invader["speed"]
        invader["x"] += random.randint(-1, 1) # 增加入侵者下降角度的随机性
        if invader["y"] > size[1]:
            invader["y"] = random.randint(-500, -50)
            invader["x"] = random.randint(0, size[0] - 50)
            invader["letters"] = [chr(random.randint(65, 90)) for _ in range(random.randint(1, 3))]
            invader["speed"] = random.randint(1, 2) # 减慢入侵者下降速度
        if invader["x"] < 0:
            invader["x"] = 0
        elif invader["x"] > size[0] - 50:
            invader["x"] = size[0] - 50

    # 更新大炮冷却时间
    if cannon["cooldown"] > 0:
        cannon["cooldown"] -= 1

    # 绘制背景
    screen.fill(WHITE)
    pygame.draw.rect(screen, (135, 206, 235), (0, 0, size[0], size[1] // 2))
    pygame.draw.rect(screen, (210, 105, 30), (0, size[1] // 2, size[0], size[1] // 2))

    # 绘制入侵者
    for invader in invader_list:
        invader_size = random.randint(30, 50) # 增加入侵者大小的随机性
        text = font.render("".join(invader["letters"]), True, BLACK)
        screen.blit(text, (invader["x"], invader["y"], invader_size, invader_size))

    # 绘制大炮
    pygame.draw.rect(screen, RED, (cannon["x"], cannon["y"], 50, 50))
    text = font.render(cannon["letter"], True, BLACK)
    screen.blit(text, (cannon["x"] + 10, cannon["y"] + 10))

    # 绘制计分牌
    text = font.render("Score: {}".format(score), True, BLACK)
    screen.blit(text, (size[0] - 150, 10))

    # 判断游戏是否结束
    if score >= 3:
        game_over = True
        text = font.render("Game Over", True, BLACK)
        screen.blit(text, (size[0] // 2 - 50, size[1] // 2 - 20))
        text = font.render("Press R to restart", True, BLACK)
        screen.blit(text, (size[0] // 2 - 80, size[1] // 2 + 20))

    # 刷新屏幕
    pygame.display.flip()

# 退出pygame
pygame.quit()

