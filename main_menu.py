import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RPG Arena")

font = pygame.font.SysFont("arial", 36)

WHITE = (255,255,255)
BLACK = (0,0,0)
GRAY = (100,100,100)
GREEN = (0,200,0)
DARK = (40,40,40)

# звук (можно позже заменить на свой)
pygame.mixer.init()
click_sound = pygame.mixer.Sound("computer-alert-sound.wav")  # заглушка (чтобы не падало)


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x,y,w,h)

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

        # подсветка при наведении
        if self.rect.collidepoint(mouse_pos):
            color = GREEN
        else:
            color = GRAY

        pygame.draw.rect(screen, color, self.rect)

        txt = font.render(self.text, True, WHITE)
        screen.blit(txt, (self.rect.x+20, self.rect.y+10))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# 🎮 кнопки (теперь 1-4 игрока)
btn_1 = Button("1 игрок", 300, 150, 200, 50)
btn_2 = Button("2 игрока", 300, 220, 200, 50)
btn_3 = Button("3 игрока", 300, 290, 200, 50)
btn_4 = Button("4 игрока", 300, 360, 200, 50)
btn_exit = Button("Выход", 300, 430, 200, 50)


def main_menu():

    while True:

        # фон (просто цвет, можно заменить на картинку)
        screen.fill(DARK)

        title = font.render("RPG ARENA", True, WHITE)
        screen.blit(title, (300,70))

        btn_1.draw()
        btn_2.draw()
        btn_3.draw()
        btn_4.draw()
        btn_exit.draw()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if btn_1.is_clicked(event):
                return 1

            if btn_2.is_clicked(event):
                return 2

            if btn_3.is_clicked(event):
                return 3

            if btn_4.is_clicked(event):
                return 4

            if btn_exit.is_clicked(event):
                pygame.quit()
                sys.exit()

        pygame.display.flip()