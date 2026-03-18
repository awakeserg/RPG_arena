import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Выбор стиля")

font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 36)

WHITE = (255,255,255)
GRAY = (100,100,100)
GREEN = (0,200,0)
DARK = (30,30,30)


# 📊 стили
STATS = {
    "Сильный": "Урон значительно выше",
    "Выносливый": "Много HP",
    "Ловкий": "Высокий шанс уклонения",
    "Удачливый": "Частые криты",
    "Инициативный": "Ходишь раньше врагов"
}


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x,y,w,h)
        self.active = False

    def draw(self):
        mouse = pygame.mouse.get_pos()

        if self.active:
            color = (0,180,0)
        elif self.rect.collidepoint(mouse):
            color = GREEN
        else:
            color = GRAY

        pygame.draw.rect(screen, color, self.rect)

        txt = font.render(self.text, True, WHITE)
        screen.blit(txt, (self.rect.x+10, self.rect.y+10))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


# создаём кнопки


confirm_btn = Button("Продолжить", 100, 500, 220, 50)


def stat_select(player_name="Игрок"):

    selected = []

    # 👉 СОЗДАЁМ КНОПКИ ЗАНОВО
    buttons = []
    y = 150

    for name in STATS:
        buttons.append(Button(name, 100, y, 220, 50))
        y += 70

    while True:

        screen.fill(DARK)

        title = big_font.render(f"Какой ты воин, {player_name}?", True, WHITE)
        screen.blit(title, (180, 50))

        # кнопки
        for btn in buttons:
            btn.draw()

        # описания справа
        y_text = 160
        for name, desc in STATS.items():
            txt = font.render(f"{name} — {desc}", True, WHITE)
            screen.blit(txt, (350, y_text))
            y_text += 40

        # кнопка продолжить (только если выбрано 2)
        if len(selected) == 2:
            confirm_btn.draw()

        # события
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for btn in buttons:
                if btn.clicked(event):

                    if btn.text in selected:
                        selected.remove(btn.text)
                        btn.active = False
                    else:
                        if len(selected) < 2:
                            selected.append(btn.text)
                            btn.active = True

            if confirm_btn.clicked(event) and len(selected) == 2:
                return selected

        pygame.display.flip()