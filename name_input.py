import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Имя игрока")

font = pygame.font.SysFont("arial", 32)
big_font = pygame.font.SysFont("arial", 40)

WHITE = (255,255,255)
GRAY = (100,100,100)
GREEN = (0,200,0)
DARK = (30,30,30)


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x,y,w,h)

    def draw(self):
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


confirm_btn = Button("Продолжить", 300, 400, 200, 60)


def name_input(player_number=1):

    name = ""
    active = True

    while True:

        screen.fill(DARK)

        # заголовок
        title = big_font.render(f"Игрок {player_number}: введи имя", True, WHITE)
        screen.blit(title, (180, 100))

        # поле ввода
        pygame.draw.rect(screen, GRAY, (250, 250, 300, 50))

        txt_surface = font.render(name, True, WHITE)
        screen.blit(txt_surface, (260, 260))

        # кнопка (только если есть имя)
        if name:
            confirm_btn.draw()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN and name:
                    return name

                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]

                else:
                    if len(name) < 12:
                        name += event.unicode

            if confirm_btn.clicked(event) and name:
                return name

        pygame.display.flip()