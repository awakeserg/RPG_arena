import pygame
import sys
from ui import get_screen

pygame.init()

# 🎨 экран
# 🖋️ шрифты
font = pygame.font.SysFont("arial", 30)
big_font = pygame.font.SysFont("arial", 54)

# 🎨 цвета
WHITE = (255,255,255)
GRAY = (100,100,100)
GREEN = (0,200,0)
DARK = (30,30,30)

BACK = "__back__"


# 🖼️ загрузка картинки
import os

def load_image(path):
    try:
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, path)

        img = pygame.image.load(full_path)
        return pygame.transform.scale(img, (220, 220))
    except Exception as e:
        print("Ошибка загрузки:", e)
        return None


# 🎭 классы
CLASSES = {
    "Воин": {
        "desc": "Баланс урона и защиты",
        "skill": "Удар щитом (стан)",
        "strength": 15,
        "stamina": 15,
        "agility": 10,
        "luck": 10,
        "image": "assets/images/warrior.png"
    },

    "Варвар": {
        "desc": "Огромный урон, но риск",
        "skill": "Берсерк (двойной урон)",
        "strength": 20,
        "stamina": 12,
        "agility": 8,
        "luck": 8,
        "image": "assets/images/barbarian.png"
    },

    "Ассасин": {
        "desc": "Быстрый и опасный",
        "skill": "Кровотечение (урон со временем)",
        "strength": 12,
        "stamina": 10,
        "agility": 18,
        "luck": 14,
        "image": "assets/images/assassin.png"
    },

    "Копейщик": {
        "desc": "Контроль и крит",
        "skill": "Пронзание (игнор брони)",
        "strength": 14,
        "stamina": 14,
        "agility": 12,
        "luck": 12,
        "image": "assets/images/spearman.png"
    }
}


# 🔘 кнопка
class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x,y,w,h)
        self.active = False

    def draw(self):
        screen = get_screen()
        mouse = pygame.mouse.get_pos()
        if self.active or self.rect.collidepoint(mouse):
            color = GREEN
        else:
            color = GRAY
        pygame.draw.rect(screen, color, self.rect)
        txt = font.render(self.text, True, WHITE)
        screen.blit(txt, (self.rect.x+10, self.rect.y+10))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


# 🎯 создаём кнопки классов
buttons = []
y = 220

for name in CLASSES:
    buttons.append(Button(name, 120, y, 280, 65))
    y += 95

# кнопка подтверждения
confirm_btn = Button("Выбрать", 120, 700, 280, 65)
back_btn = Button("Назад", 120, 615, 280, 65)


# 🎮 главный экран выбора
def class_select(player_name="Игрок"):
    screen = get_screen("Выбор класса")
    clock = pygame.time.Clock()

    selected = None

    while True:
        screen.fill(DARK)
        # заголовок
        left_panel = pygame.Rect(70, 120, 400, 690)
        right_panel = pygame.Rect(520, 120, 1210, 690)
        pygame.draw.rect(screen, (45,45,45), left_panel, border_radius=20)
        pygame.draw.rect(screen, (45,45,45), right_panel, border_radius=20)
        pygame.draw.rect(screen, WHITE, left_panel, 3, border_radius=20)
        pygame.draw.rect(screen, WHITE, right_panel, 3, border_radius=20)

        title = big_font.render(f"Выбор класса: {player_name}", True, WHITE)
        screen.blit(title, (610,50))

        # кнопки классов
        for btn in buttons:
            btn.active = (btn.text == selected)
            btn.draw()

        # если выбран класс — показываем инфо
        if selected:
            data = CLASSES[selected]
            # 🖼️ картинка
            img = load_image(data["image"])
            if img:
                screen.blit(img, (1320, 170))
            # 📊 характеристики
            y_text = 190
            lines = [
                selected,
                f"Сила: {data['strength']}",
                f"Выносливость: {data['stamina']}",
                f"Ловкость: {data['agility']}",
                f"Удача: {data['luck']}",
                f"Инициатива: {data.get('initiative', 10)}",
                "",
                f"Способность: {data['skill']}",
                "",
                data["desc"]
            ]
            for line in lines:
                txt = font.render(line, True, WHITE)
                screen.blit(txt, (620, y_text))
                y_text += 48

        # кнопка подтверждения
        back_btn.draw()
        confirm_btn.draw()

        # 🎮 события
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return BACK
            # выбор класса
            for btn in buttons:
                if btn.clicked(event):
                    selected = btn.text
            if back_btn.clicked(event):
                return BACK
            # подтверждение
            if confirm_btn.clicked(event) and selected:
                return selected
        pygame.display.flip()
        clock.tick(60)