import pygame
import sys
from ui import get_screen

pygame.init()

font = pygame.font.SysFont("arial", 30)
big_font = pygame.font.SysFont("arial", 54)

WHITE = (255,255,255)
GRAY = (100,100,100)
GREEN = (0,200,0)
DARK = (30,30,30)

BACK = "__back__"


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
        screen = get_screen()
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


confirm_btn = Button("Продолжить", 120, 730, 280, 65)
back_btn = Button("Назад", 120, 645, 280, 65)


def stat_select(player_name="Игрок"):
    screen = get_screen("Выбор стиля")
    clock = pygame.time.Clock()

    selected = []

    # 👉 СОЗДАЁМ КНОПКИ ЗАНОВО
    buttons = []
    y = 220

    for name in STATS:
        buttons.append(Button(name, 120, y, 280, 65))
        y += 95

    while True:

        screen.fill(DARK)

        left_panel = pygame.Rect(70, 120, 420, 720)
        right_panel = pygame.Rect(540, 120, 1190, 720)
        pygame.draw.rect(screen, (45,45,45), left_panel, border_radius=20)
        pygame.draw.rect(screen, (45,45,45), right_panel, border_radius=20)
        pygame.draw.rect(screen, WHITE, left_panel, 3, border_radius=20)
        pygame.draw.rect(screen, WHITE, right_panel, 3, border_radius=20)

        title = big_font.render(f"Какой ты воин, {player_name}?", True, WHITE)
        screen.blit(title, (560, 50))

        # кнопки
        for btn in buttons:
            btn.draw()

        # описания справа
        y_text = 220
        for name, desc in STATS.items():
            txt = font.render(f"{name} — {desc}", True, WHITE)
            screen.blit(txt, (610, y_text))
            y_text += 74

        # кнопка продолжить (только если выбрано 2)
        if len(selected) == 2:
            confirm_btn.draw()
        back_btn.draw()

        # события
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return BACK

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

            if back_btn.clicked(event):
                return BACK

        pygame.display.flip()
        clock.tick(60)