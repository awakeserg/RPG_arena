import pygame
import sys
from ui import get_screen

pygame.init()

font = pygame.font.SysFont("arial", 42)
big_font = pygame.font.SysFont("arial", 60)

WHITE = (255,255,255)
GRAY = (100,100,100)
GREEN = (0,200,0)
DARK = (30,30,30)

BACK = "__back__"


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x,y,w,h)

    def draw(self):
        screen = get_screen()
        mouse = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse):
            color = GREEN
        else:
            color = GRAY

        pygame.draw.rect(screen, color, self.rect)

        txt = font.render(self.text, True, WHITE)
        screen.blit(txt, (self.rect.x+10, self.rect.y+10))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


confirm_btn = Button("Продолжить", 760, 560, 280, 70)
back_btn = Button("Назад", 500, 560, 180, 70)


def name_input(player_number=1, initial_name=""):
    screen = get_screen("Имя игрока")
    clock = pygame.time.Clock()
    pygame.key.start_text_input()

    name = initial_name

    try:
        while True:

            screen.fill(DARK)

            # заголовок
            panel = pygame.Rect(450, 180, 900, 520)
            pygame.draw.rect(screen, (45,45,45), panel, border_radius=24)
            pygame.draw.rect(screen, WHITE, panel, 3, border_radius=24)

            title = big_font.render(f"Игрок {player_number}: введи имя", True, WHITE)
            screen.blit(title, (600, 250))

            hint = font.render("Имя до 12 символов", True, (200, 200, 200))
            screen.blit(hint, (690, 330))

            # поле ввода
            pygame.draw.rect(screen, GRAY, (590, 390, 620, 80), border_radius=12)

            txt_surface = font.render(name, True, WHITE)
            screen.blit(txt_surface, (610, 410))

            # кнопка (только если есть имя)
            if name:
                confirm_btn.draw()
            back_btn.draw()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        return BACK

                    if event.key == pygame.K_RETURN and name:
                        return name

                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]

                if event.type == pygame.TEXTINPUT:
                    if len(name) < 12:
                        name += event.text

                if confirm_btn.clicked(event) and name:
                    return name

                if back_btn.clicked(event):
                    return BACK

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.key.stop_text_input()