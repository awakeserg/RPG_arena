import pygame


WIDTH, HEIGHT = 1800, 900
_screen = None


def init_display(caption="RPG Arena"):
    global _screen
    if not pygame.get_init():
        pygame.init()
    if _screen is None:
        _screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(caption)
    return _screen


def get_screen(caption=None):
    global _screen
    if _screen is None:
        _screen = init_display(caption or "RPG Arena")
    elif caption is not None:
        pygame.display.set_caption(caption)
    return _screen