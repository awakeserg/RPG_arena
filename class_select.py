import pygame
import sys

pygame.init()

# 🎨 экран
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Выбор класса")

# 🖋️ шрифты
font = pygame.font.SysFont("arial", 24)
big_font = pygame.font.SysFont("arial", 36)

# 🎨 цвета
WHITE = (255,255,255)
GRAY = (100,100,100)
GREEN = (0,200,0)
DARK = (30,30,30)


# 🖼️ загрузка картинки
import os

def load_image(path):
    try:
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, path)

        print("Загружаю:", full_path)  # 👈 добавь это

        img = pygame.image.load(full_path)
        return pygame.transform.scale(img, (120, 120))
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


# 🎯 создаём кнопки классов
buttons = []
y = 150

for name in CLASSES:
    buttons.append(Button(name, 100, y, 200, 50))
    y += 70

# кнопка подтверждения
confirm_btn = Button("Выбрать", 100, 500, 200, 50)


# 🎮 главный экран выбора
def class_select(player_name="Игрок"):

    selected = None

    while True:

        screen.fill(DARK)

        # заголовок
        title = big_font.render(f"Выбор класса: {player_name}", True, WHITE)
        screen.blit(title, (200,50))

        # кнопки классов
        for btn in buttons:
            btn.draw()

        # если выбран класс — показываем инфо
        if selected:
            data = CLASSES[selected]

            # 🖼️ картинка
            img = load_image(data["image"])
            if img:
                screen.blit(img, (500, 120))

            # 📊 характеристики
            y_text = 250

            lines = [
                selected,
                f"Сила: {data['strength']}",
                f"Выносливость: {data['stamina']}",
                f"Ловкость: {data['agility']}",
                f"Удача: {data['luck']}",
                "",
                f"Способность: {data['skill']}",
                "",
                data["desc"]
            ]

            for line in lines:
                txt = font.render(line, True, WHITE)
                screen.blit(txt, (450, y_text))
                y_text += 30

        # кнопка подтверждения
        confirm_btn.draw()

        # 🎮 события
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # выбор класса
            for btn in buttons:
                if btn.clicked(event):
                    selected = btn.text

            # подтверждение
            if confirm_btn.clicked(event) and selected:
                return selected

        pygame.display.flip()