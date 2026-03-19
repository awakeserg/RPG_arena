import os
import random
import sys

import pygame

from engine.combat import attack
from engine.items import loot
from engine.player import Player


WIDTH, HEIGHT = 1800, 900

WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
DARK = (30, 30, 30)
PANEL = (45, 45, 55)
GOLD = (255, 215, 0)
SILVER = (210, 210, 220)
BRONZE = (205, 140, 90)
SKY = (80, 180, 255)
LIGHT_BLUE = (170, 225, 255)
LIGHT_PINK = (255, 190, 220)
TURQUOISE = (80, 220, 215)
BRIGHT_TURQUOISE = (120, 255, 245)


class UIButton:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, font, enabled=True, active=False):
        mouse = pygame.mouse.get_pos()
        if not enabled:
            color = (85, 85, 85)
            text_color = (170, 170, 170)
        elif active:
            color = (0, 180, 0)
            text_color = WHITE
        elif self.rect.collidepoint(mouse):
            color = GREEN
            text_color = WHITE
        else:
            color = GRAY
            text_color = WHITE

        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        txt = font.render(self.text, True, text_color)
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)

    def clicked(self, event, enabled=True):
        return enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


class ArenaGame:
    MENU = "menu"
    NAME_INPUT = "name_input"
    CLASS_SELECT = "class_select"
    MAGIC_SELECT = "magic_select"
    STAT_SELECT = "stat_select"
    BATTLE = "battle"
    POST_BATTLE = "post_battle"

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("RPG Arena")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = self.MENU

        self.font = pygame.font.SysFont("arial", 30)
        self.medium_font = pygame.font.SysFont("arial", 42)
        self.big_font = pygame.font.SysFont("arial", 60)
        self.title_font = pygame.font.SysFont("arial", 72, bold=True)
        self.hero_font = pygame.font.SysFont("arial", 88, bold=True)
        self.small_font = pygame.font.SysFont("arial", 24)
        self.log_font = pygame.font.SysFont("arial", 22)
        self.class_name_font = pygame.font.SysFont("arial", 38, bold=True)

        # Шрифт для emoji/Unicode-символов (Segoe UI Emoji на Win11, Segoe UI Symbol на Win10)
        _emoji_candidates = [
            os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "seguiemj.ttf"),
            "C:/Windows/Fonts/seguiemj.ttf",
            os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "seguisym.ttf"),
            "C:/Windows/Fonts/seguisym.ttf",
        ]
        _color_emoji_names = {"seguiemj.ttf"}  # только этот файл умеет рендерить SMP emoji
        self.emoji_font = None
        self.has_color_emoji = False
        for _ep in _emoji_candidates:
            if os.path.exists(_ep):
                try:
                    self.emoji_font = pygame.font.Font(_ep, 20)
                    self.has_color_emoji = os.path.basename(_ep).lower() in _color_emoji_names
                    break
                except Exception:
                    pass
        if self.emoji_font is None:
            self.emoji_font = pygame.font.SysFont("Segoe UI Symbol", 20)
        self.log_icon_chars = set("◎★⚡▲❄◆⚠✶⚔♥○⊕☠↻⚒↺•▸✨☀◼✦🪨☽※")

        self.class_data = {
            "Воин": {
                "desc": "Баланс урона и защиты",
                "skill": "Удар щитом — 50% урона и 30% шанс оглушить врага на 1 ход",
                "passive": "Пассивно: Обезоруживание — 40% шанс при любом успешном ударе. На следующий ход цель не может использовать активку, её урон снижен вдвое, пассивка отключена, шанс лута ниже на 20%.",
                "active": "Активно: Удар щитом наносит 50% от текущего урона и с шансом 30% оглушает цель на 1 ход.",
                "strength": 15,
                "stamina": 15,
                "agility": 10,
                "luck": 10,
                "initiative": 10,
                "intellect": 10,
                "image": "assets/images/warrior.png",
            },
            "Варвар": {
                "desc": "Огромный урон, но риск",
                "skill": "Берсерк — 200% урона, но 30% шанс ранить себя тем же ударом",
                "passive": "Пассивно: 25% шанс искалечить цель при любом успешном ударе: 10% отрубить руку (урон жертвы x0.5 до конца боя), 10% отрубить ногу (инициатива жертвы = 1), 3% отрубить голову (мгновенная смерть).",
                "active": "Активно: Берсерк наносит 200% урона, но с шансом 30% варвар бьёт только себя на тот же урон. На самоудар пассивка тоже может сработать.",
                "strength": 20,
                "stamina": 12,
                "agility": 8,
                "luck": 8,
                "initiative": 10,
                "intellect": 10,
                "image": "assets/images/barbarian.png",
            },
            "Ассасин": {
                "desc": "Смертельно быстрый охотник",
                "skill": "Кровопускание — атака и 60% шанс наложить кровотечение",
                "passive": "Пассивно: 30% шанс сразу получить ещё 1 ход. На бонусный ход пассивка уже не срабатывает.",
                "active": "Активно: выполняет обычную атаку и с шансом 60% накладывает кровотечение на 3 хода по 40% от текущего урона за тик.",
                "strength": 12,
                "stamina": 10,
                "agility": 18,
                "luck": 14,
                "initiative": 10,
                "intellect": 10,
                "image": "assets/images/assassin.png",
            },
            "Копейщик": {
                "desc": "Контроль дистанции и крит",
                "skill": "Подсечка — 30% урона и 50% шанс опрокинуть врага на 1 ход",
                "passive": "Пассивно: Точный удар — 60% шанс при любом ударе полностью игнорировать уклонение врага, словно его ловкость равна 0.",
                "active": "Активно: Подсечка наносит 30% от текущего урона и с шансом 50% опрокидывает цель на 1 ход.",
                "strength": 14,
                "stamina": 14,
                "agility": 12,
                "luck": 12,
                "initiative": 10,
                "intellect": 10,
                "image": "assets/images/spearman.png",
            },
            "\u0411\u043e\u0435\u0432\u043e\u0439 \u043c\u0430\u0433": {
                "desc": "\u0412\u043e\u0438\u043d, \u043e\u0432\u043b\u0430\u0434\u0435\u0432\u0448\u0438\u0439 \u0442\u0430\u0439\u043d\u043e\u0439 \u043c\u0430\u0433\u0438\u0438",
                "skill": "\u0417\u0430\u0440\u044f\u0434 \u043e\u0440\u0443\u0436\u0438\u044f \u2014 2 \u0445\u043e\u0434\u0430 +50% \u0448\u0430\u043d\u0441 \u043c\u0430\u0433\u0438\u0447\u0435\u0441\u043a\u043e\u0433\u043e \u0434\u043e\u0431\u0438\u0432\u0430\u043d\u0438\u044f",
                "passive": "\u041f\u0430\u0441\u0441\u0438\u0432\u043d\u043e: \u041c\u0430\u0433\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043a\u0440\u0438\u0442 \u2014 \u0437\u0430\u043a\u043b\u0438\u043d\u0430\u043d\u0438\u044f \u0411\u043e\u0435\u0432\u043e\u0433\u043e \u043c\u0430\u0433\u0430 \u043c\u043e\u0433\u0443\u0442 \u043d\u0430\u043d\u0435\u0441\u0442\u0438 \u043a\u0440\u0438\u0442\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u0443\u0434\u0430\u0440 (\u0445\u2032-\u0434\u0432\u043e\u0439\u043d\u043e\u0439 \u0443\u0440\u043e\u043d). \u0423 \u043e\u0441\u0442\u0430\u043b\u044c\u043d\u044b\u0445 \u043a\u043b\u0430\u0441\u0441\u043e\u0432 \u043c\u0430\u0433\u0438\u044f \u043d\u0435 \u043a\u0440\u0438\u0442\u0443\u0435\u0442. \u0428\u0430\u043d\u0441 \u0440\u0430\u0441\u0441\u0447\u0438\u0442\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0442\u0430\u043a \u0436\u0435, \u043a\u0430\u043a \u0444\u0438\u0437 \u043a\u0440\u0438\u0442, \u0447\u0435\u0440\u0435\u0437 \u0443\u0434\u0430\u0447\u0443.",
                "active": "\u0410\u043a\u0442\u0438\u0432\u043d\u043e: \u0417\u0430\u0440\u044f\u0434 \u043e\u0440\u0443\u0436\u0438\u044f \u2014 \u043d\u0430 2 \u0445\u043e\u0434\u0430 \u043a\u0430\u0436\u0434\u0430\u044f \u0443\u0441\u043f\u0435\u0448\u043d\u0430\u044f \u0444\u0438\u0437. \u0430\u0442\u0430\u043a\u0430 \u0441 50% \u0448\u0430\u043d\u0441\u043e\u043c \u0434\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e \u043f\u043e\u0440\u0430\u0436\u0430\u0435\u0442 \u0446\u0435\u043b\u044c \u043c\u0430\u0433\u0438\u0435\u0439 \u043f\u0443\u0442\u0438 (\u0441\u0442\u0440\u0435\u043b\u0430 \u043e\u0433\u043d\u044f / \u043b\u0435\u0434\u044f\u043d\u0430\u044f \u0441\u0442\u0440\u0435\u043b\u0430). \u041e\u0442 \u0434\u043e\u043f. \u0443\u0434\u0430\u0440\u0430 \u0442\u043e\u0436\u0435 \u043c\u043e\u0436\u043d\u043e \u0443\u043a\u043b\u043e\u043d\u0438\u0442\u044c\u0441\u044f.",
                "strength": 14,
                "stamina": 13,
                "agility": 10,
                "luck": 12,
                "initiative": 10,
                "intellect": 16,
                "image": "assets/images/battle_mage.png",
            },
            "\u0428\u0430\u043c\u0430\u043d": {
                "desc": "\u041c\u0438\u0441\u0442\u0438\u043a, \u0447\u0435\u0440\u043f\u0430\u044e\u0449\u0438\u0439 \u0441\u0438\u043b\u0443 \u0438\u0437 \u043f\u0440\u0438\u0440\u043e\u0434\u044b",
                "skill": "\u041a\u0430\u043c\u043b\u0430\u043d\u0438\u0435 \u2014 \u0442\u0440\u0430\u0442\u0438\u0442 \u0445\u043e\u0434, \u0443\u0432\u0435\u043b\u0438\u0447\u0438\u0432\u0430\u0435\u0442 \u0438\u043d\u0442\u0435\u043b\u043b\u0435\u043a\u0442 \u0432 1.5 \u0440\u0430\u0437\u0430 \u043d\u0430 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0438\u0439 \u0445\u043e\u0434",
                "passive": "\u041f\u0430\u0441\u0441\u0438\u0432\u043d\u043e: \u0422\u043e\u0442\u0435\u043c \u0437\u0432\u0435\u0440\u044f \u2014 \u0432 \u043a\u043e\u043d\u0446\u0435 \u043a\u0430\u0436\u0434\u043e\u0433\u043e \u0445\u043e\u0434\u0430 \u0435\u0441\u0442\u044c 50% \u0448\u0430\u043d\u0441, \u0447\u0442\u043e \u0432 \u043d\u0430\u0447\u0430\u043b\u0435 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u0433\u043e \u0445\u043e\u0434\u0430 \u0441\u0438\u043b\u0430 \u0438 \u043b\u043e\u0432\u043a\u043e\u0441\u0442\u044c \u0428\u0430\u043c\u0430\u043d\u0430 \u0443\u0432\u0435\u043b\u0438\u0447\u0430\u0442\u0441\u044f \u0432 1.5 \u0440\u0430\u0437\u0430.",
                "active": "\u0410\u043a\u0442\u0438\u0432\u043d\u043e: \u041a\u0430\u043c\u043b\u0430\u043d\u0438\u0435 \u2014 \u0448\u0430\u043c\u0430\u043d \u0432\u0445\u043e\u0434\u0438\u0442 \u0432 \u0442\u0440\u0430\u043d\u0441, \u0442\u0440\u0430\u0442\u044f \u0442\u0435\u043a\u0443\u0449\u0438\u0439 \u0445\u043e\u0434. \u041d\u0430 \u0441\u043b\u0435\u0434\u0443\u044e\u0449\u0435\u043c \u0445\u043e\u0434\u0443 \u0438\u043d\u0442\u0435\u043b\u043b\u0435\u043a\u0442 \u0443\u0432\u0435\u043b\u0438\u0447\u0438\u0432\u0430\u0435\u0442\u0441\u044f \u0432 1.5 \u0440\u0430\u0437\u0430.",
                "strength": 16,
                "stamina": 12,
                "agility": 10,
                "luck": 10,
                "initiative": 10,
                "intellect": 14,
                "image": "assets/images/shaman.png",
            },
        }
        self.stat_data = {
            "Сильный": "Урон значительно выше",
            "Выносливый": "Много HP",
            "Ловкий": "Высокий шанс уклонения",
            "Удачливый": "Частые криты",
            "Инициативный": "Ходишь раньше врагов",
            "Интеллектуальный": "Больше шанс прозрения и сильнее магия",
        }
        self.class_groups = {
            "Боец": ["Воин", "Боевой маг"],
            "Дикарь": ["Варвар", "Шаман"],
            "Ассасин": ["Ассасин"],
            "Копейщик": ["Копейщик"],
        }
        self.magic_data = {
            "Путь огня": {
                "desc": "Идущий по Пути огня стремится слиться с самой разрушительной стихией, чтобы сжечь этот мир или сгореть изнутри, перейдя в иную форму существования.",
                "normal": [
                    {
                        "id": "fire_arrow",
                        "name": "Стрела огня",
                        "target": "enemy",
                        "desc": "Наносит урон, равный интеллекту. 50% шанс поджечь цель: ещё 2 её хода она получает половину урона заклинания.",
                    },
                    {
                        "id": "fire_wall",
                        "name": "Стена огня",
                        "target": "self",
                        "desc": "На 2 своих хода окружает мага пламенем. Враги в ближнем бою наносят на 20% меньше урона и с шансом 30% загораются. Магия через стену бьёт в 1.5 раза сильнее.",
                    },
                ],
                "exalted": [
                    {
                        "id": "supernova",
                        "name": "Сверхновая",
                        "target": "enemy",
                        "desc": "Взрыв наносит 150% от интеллекта основной цели. Каждого прочего бойца, включая мага, может задеть с шансом 50% на тот же урон.",
                    },
                    {
                        "id": "phoenix",
                        "name": "Феникс",
                        "target": "self",
                        "desc": "70% шанс полностью восстановить HP, 15% шанс сгореть дотла и проиграть, 15% — ничего не происходит.",
                    },
                ],
            },
            "Путь воды": {
                "desc": "Идущие по Пути воды познали тайны тихих вод и обрели гармонию с миром, но им также ведомы сокрушительные штормы и беспощадный холод глубин.",
                "normal": [
                    {
                        "id": "heal",
                        "name": "Исцеление",
                        "target": "self",
                        "desc": "Восстанавливает HP, равное интеллекту. 25% шанс исцелиться полностью.",
                    },
                    {
                        "id": "ice_arrow",
                        "name": "Ледяная стрела",
                        "target": "enemy",
                        "desc": "Наносит урон, равный интеллекту. 20% шанс заморозить цель на 1 ход.",
                    },
                ],
                "exalted": [
                    {
                        "id": "water_essence",
                        "name": "Суть воды",
                        "target": "self",
                        "desc": "80% шанс полностью исцелить мага. Если удалось, то ещё 60% шанс полностью исцелить всех вокруг.",
                    },
                    {
                        "id": "ice_spear",
                        "name": "Ледяное копьё",
                        "target": "enemy",
                        "desc": "Наносит двойной урон от интеллекта. 20% шанс заморозить. Если цель уже заморожена, повторная заморозка раскалывает её насмерть.",
                    },
                ],
            },
            "Путь земли": {
                "desc": "Адепты Пути земли ищут покой, крепость и молчаливую мудрость камня. Они кажутся безучастными, словно древние статуи, потому что слышат тайны недр.",
                "normal": [
                    {
                        "id": "stone_skin",
                        "name": "Каменная кожа",
                        "target": "self",
                        "desc": "На 2 своих хода снижает весь входящий урон на 50% и защищает от всех дополнительных эффектов. Пока держится, нельзя колдовать и использовать активную способность.",
                    },
                    {
                        "id": "stone_spikes",
                        "name": "Каменные шипы",
                        "target": "enemy",
                        "desc": "Шипы из земли наносят урон, равный интеллекту. 30% шанс дополнительно вызвать кровотечение на 3 хода по 40% урона или ошеломить цель на 1 ход.",
                    },
                ],
                "exalted": [
                    {
                        "id": "earth_blast",
                        "name": "Взрыв земли",
                        "target": "enemy",
                        "desc": "Основная цель получает 150% от интеллекта. 50% шанс оглушить. С вероятностью 65% остальные тоже получают тот же урон, но без оглушения.",
                    },
                    {
                        "id": "earthquake",
                        "name": "Землетрясение",
                        "target": "enemy",
                        "desc": "Все, кроме адептов Пути земли, получают 70% от интеллекта. Основная цель оглушается с шансом 50%, остальные — с шансом 30%.",
                    },
                ],
            },
            "Путь воздуха": {
                "desc": "Идущие по Пути воздуха учатся слышать шёпот высоты, читать знаки в бурях и двигаться раньше собственной тени. Их стихия кажется невесомой, но именно она первой срывает крыши, ломает строй и приносит небесную кару.",
                "normal": [
                    {
                        "id": "wind_blades",
                        "name": "Лезвия ветра",
                        "target": "enemy",
                        "desc": "Режущие потоки наносят урон, равный интеллекту. 30% шанс оставить кровоточащие порезы на 3 хода по 40% урона заклинания.",
                    },
                    {
                        "id": "tailwind",
                        "name": "Попутный ветер",
                        "target": "self",
                        "desc": "Действует в текущем и ещё в 2 следующих своих ходах. Повышает шанс уклонения на 30% и делает мага трудноуловимым для врагов.",
                    },
                ],
                "exalted": [
                    {
                        "id": "sky_thunder",
                        "name": "Небесная молния",
                        "target": "enemy",
                        "desc": "Наносит 220% от интеллекта основной цели. 35% шанс оглушить. С вероятностью 50% молния перескакивает на ещё одного врага и наносит 110% от интеллекта.",
                    },
                    {
                        "id": "storm_front",
                        "name": "Ураганный фронт",
                        "target": "enemy",
                        "desc": "Все остальные бойцы получают 90% от интеллекта мага. Главная цель обезоруживается с шансом 80%, остальные пострадавшие — с шансом 40%.",
                    },
                ],
            },
            "Тёмный путь": {
                "desc": "Идущие Тёмным путём не поклоняются ночи — они принимают её как честную правду. Там, где другие видят ужас, они находят власть, голод бездны и обещание победы любой ценой.",
                "normal": [
                    {
                        "id": "shadow_shroud",
                        "name": "Покров мрака",
                        "target": "self",
                        "desc": "На 2 своих хода окутывает мага тьмой: входящий урон снижается на 40%, а уклонение возрастает на 25%.",
                    },
                    {
                        "id": "soul_reap",
                        "name": "Жатва души",
                        "target": "enemy",
                        "desc": "Наносит 110% от интеллекта, исцеляет мага на половину нанесённого урона. 35% шанс проклясть цель: её урон и интеллект падают на 25% на 2 хода.",
                    },
                ],
                "exalted": [
                    {
                        "id": "black_sun",
                        "name": "Чёрное солнце",
                        "target": "enemy",
                        "desc": "Главная цель получает 220% от интеллекта и с шансом 50% оглушается. Остальные бойцы с вероятностью 75% получают ещё 110% от интеллекта.",
                    },
                    {
                        "id": "abyss_name",
                        "name": "Имя Бездны",
                        "target": "enemy",
                        "desc": "Наносит 160% от интеллекта. Если после удара цель опускается до 35% HP или ниже, Бездна мгновенно забирает её. Иначе накладывается тяжёлое кровотечение.",
                    },
                ],
            },
            "Путь непознаваемого": {
                "desc": "Это запредельный путь тех, кто смотрел за край реальности и вернулся не совсем прежним. Его адепты зовут силы, которым нет имени, и ломают саму логику мира ради краткого мига невозможного превосходства.",
                "normal": [
                    {
                        "id": "impossible_angle",
                        "name": "Невозможный угол",
                        "target": "enemy",
                        "desc": "Наносит 50% от интеллекта и всегда искажает жертву случайным эффектом: оглушение, заморозка, обезоруживание, кровотечение или возгорание.",
                    },
                    {
                        "id": "outer_whisper",
                        "name": "Шёпот извне",
                        "target": "self",
                        "desc": "С шансом 65% немедленно открывает возвышенную магию в этот же ход. Следующее заклинание мага усиливается в 1.5 раза.",
                    },
                ],
                "exalted": [
                    {
                        "id": "doorless_gate",
                        "name": "Врата без двери",
                        "target": "enemy",
                        "desc": "Главная цель получает 230% от интеллекта. Остальные бойцы с шансом 65% получают по 90%, а каждый такой удар с шансом 30% вешает случайный эффект.",
                    },
                    {
                        "id": "unknowable_touch",
                        "name": "Касание непознаваемого",
                        "target": "enemy",
                        "desc": "Наносит 160% от интеллекта плюс ещё по 100% за каждый эффект на цели, затем снимает их. Если эффектов нет, заклинание навешивает сразу два случайных искажения.",
                    },
                ],
            },
        }
        self.arena_data = [
            ("Колизей", "hp"),
            ("Лес", "dodge"),
            ("Вулкан", "damage"),
            ("Ледяная пустошь", "crit"),
        ]

        self.menu_buttons = [
            UIButton("1 игрок", 760, 240, 280, 70),
            UIButton("2 игрока", 760, 330, 280, 70),
            UIButton("3 игрока", 760, 420, 280, 70),
            UIButton("4 игрока", 760, 510, 280, 70),
        ]
        self.menu_exit_button = UIButton("Выход", 760, 620, 280, 70)

        self.name_confirm_button = UIButton("Продолжить", 760, 560, 280, 70)
        self.name_back_button = UIButton("Назад", 500, 560, 180, 70)
        self.name_clear_button = UIButton("Очистить", 1080, 560, 180, 70)
        self.name_space_button = UIButton("Пробел", 640, 760, 220, 60)
        self.name_delete_button = UIButton("Стереть", 890, 760, 220, 60)
        self.name_space_button.rect = pygame.Rect(520, 648, 220, 56)
        self.name_delete_button.rect = pygame.Rect(790, 648, 220, 56)
        self.name_clear_button.rect = pygame.Rect(1060, 648, 220, 56)
        self.name_confirm_button.rect = pygame.Rect(610, 730, 260, 64)
        self.name_back_button.rect = pygame.Rect(930, 730, 260, 64)

        self.name_key_buttons = []
        self.rebuild_name_key_buttons()

        self.class_buttons = []
        y = 220
        for name in self.class_groups:
            self.class_buttons.append(UIButton(name, 120, y, 280, 65))
            y += 95
        self.class_confirm_button = UIButton("Выбрать", 120, 700, 280, 65)
        self.class_back_button = UIButton("Назад", 120, 615, 280, 65)

        self.magic_buttons = []
        y = 220
        for name in self.magic_data:
            self.magic_buttons.append(UIButton(name, 120, y, 280, 56))
            y += 68
        self.magic_confirm_button = UIButton("Продолжить", 120, 730, 280, 65)
        self.magic_back_button = UIButton("←", 420, 730, 65, 65)

        self.stat_buttons = []
        y = 170
        for name in self.stat_data:
            self.stat_buttons.append(UIButton(name, 120, y, 280, 65))
            y += 72
        self.stat_confirm_button = UIButton("Продолжить", 120, 730, 280, 65)
        self.stat_back_button = UIButton("←", 420, 730, 65, 65)

        self.battle_buttons = [
            UIButton("Атака", 70, 600, 220, 100),
            UIButton("Осторожно", 320, 600, 220, 100),
            UIButton("Спец", 570, 600, 220, 100),
            UIButton("Лут", 820, 600, 220, 100),
            UIButton("Колдовать", 1070, 600, 220, 100),
        ]
        self.spell_buttons = [
            UIButton("", 1360, 590, 330, 70),
            UIButton("", 1360, 675, 330, 70),
        ]

        self.post_rematch_button = UIButton("Реванш", 420, 720, 260, 75)
        self.post_restart_button = UIButton("Начать заново", 770, 720, 320, 75)
        self.post_quit_button = UIButton("Закрыть игру", 1180, 720, 300, 75)

        self.icons = self.load_class_icons()
        self.subclass_showcase_art = self.create_subclass_showcase_art()

        self.player_count = 0
        self.human_names = []
        self.player_builds = []
        self.scores = {}
        self.rematch_mode = False

        self.name_index = 0
        self.name_buffer = ""

        self.setup_index = 0
        self.selected_class = None
        self.selected_group = None
        self.selected_magic_path = None
        self.selected_stats = []
        self.allow_back_to_names = True

        self.players = []
        self.current_turn = 0
        self.bonus_turn_player = None
        self.selected_target = None
        self.hit_target = None
        self.hit_timer = 0
        self.log = []
        self.info_rects = []
        self.show_info_idx = None
        self.close_popup_rect = None
        self.arena_name = ""
        self.ai_action_due = 0
        self.spell_menu_open = False
        self.spell_tier = "normal"

        self.winner_name = ""
        self.champion = False

    def _create_fallback_icon(self, class_name, size=220):
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        color = self.get_class_color(class_name)
        center = size // 2
        pygame.draw.circle(surface, color, (center, center), center - 5)
        pygame.draw.circle(surface, WHITE, (center, center), center - 5, 3)
        letter = class_name[0].upper()
        letter_font = pygame.font.SysFont("arial", size // 2, bold=True)
        txt = letter_font.render(letter, True, WHITE)
        surface.blit(txt, txt.get_rect(center=(center, center)))
        return surface

    def load_class_icons(self):
        icons = {}
        base_dir = os.path.dirname(__file__)
        for name, data in self.class_data.items():
            path = os.path.join(base_dir, data["image"])
            try:
                image = pygame.image.load(path)
                scaled = pygame.transform.scale(image, (220, 220))
                if name == "Шаман":
                    scaled = self._tint_surface(scaled, (255, 196, 68), 18)
                    scaled = self._tint_surface(scaled, (64, 168, 150), 10)
                icons[name] = scaled
            except Exception:
                icons[name] = self._create_fallback_icon(name)
        return icons

    def _tint_surface(self, surface, color, alpha=40):
        tinted = surface.copy()
        overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        overlay.fill((*color, alpha))
        tinted.blit(overlay, (0, 0))
        return tinted

    def _make_circle_portrait(self, surface, size):
        scaled = pygame.transform.smoothscale(surface, (size, size))
        mask = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
        result = pygame.Surface((size, size), pygame.SRCALPHA)
        result.blit(scaled, (0, 0))
        result.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return result

    def _create_barbarian_showcase_art(self):
        surface = pygame.Surface((220, 280), pygame.SRCALPHA)
        skin = (206, 160, 122)
        fur = (126, 82, 44)
        metal = (180, 190, 200)
        axe_wood = (110, 72, 46)
        red_cloth = (170, 42, 42)

        pygame.draw.line(surface, axe_wood, (170, 18), (94, 252), 13)
        pygame.draw.polygon(surface, metal, [(126, 52), (186, 14), (208, 58), (152, 94)])
        pygame.draw.polygon(surface, metal, [(168, 70), (214, 104), (176, 134), (140, 88)])

        pygame.draw.ellipse(surface, red_cloth, (58, 68, 98, 122))
        pygame.draw.ellipse(surface, fur, (42, 74, 132, 102))
        pygame.draw.circle(surface, skin, (102, 54), 28)
        pygame.draw.polygon(surface, fur, [(72, 48), (86, 10), (118, 10), (136, 48), (122, 32), (84, 32)])
        pygame.draw.line(surface, fur, (92, 66), (84, 84), 5)
        pygame.draw.line(surface, fur, (112, 66), (120, 84), 5)
        pygame.draw.line(surface, red_cloth, (96, 96), (108, 128), 4)

        pygame.draw.line(surface, skin, (68, 112), (42, 188), 15)
        pygame.draw.line(surface, skin, (138, 110), (170, 178), 15)
        pygame.draw.line(surface, fur, (64, 110), (40, 190), 7)
        pygame.draw.line(surface, fur, (142, 108), (170, 178), 7)
        pygame.draw.line(surface, skin, (88, 192), (68, 260), 17)
        pygame.draw.line(surface, skin, (120, 192), (144, 260), 17)
        pygame.draw.line(surface, fur, (84, 194), (66, 260), 7)
        pygame.draw.line(surface, fur, (124, 194), (146, 260), 7)
        pygame.draw.line(surface, metal, (68, 260), (48, 276), 5)
        pygame.draw.line(surface, metal, (144, 260), (164, 276), 5)
        return surface

    def _create_warrior_showcase_art(self):
        surface = pygame.Surface((220, 280), pygame.SRCALPHA)
        skin = (212, 174, 138)
        steel = (172, 184, 204)
        steel_dark = (92, 108, 132)
        tabard = (72, 118, 186)
        leather = (106, 74, 48)
        pygame.draw.circle(surface, skin, (102, 56), 22)
        pygame.draw.ellipse(surface, steel_dark, (76, 20, 52, 46))
        pygame.draw.ellipse(surface, steel, (82, 18, 40, 22))
        pygame.draw.line(surface, steel, (102, 20), (102, 56), 2)
        pygame.draw.polygon(surface, steel, [(68, 84), (138, 84), (150, 180), (56, 180)])
        pygame.draw.polygon(surface, tabard, [(90, 84), (116, 84), (126, 188), (80, 188)])
        pygame.draw.line(surface, leather, (102, 84), (102, 180), 3)
        pygame.draw.line(surface, skin, (72, 102), (46, 170), 11)
        pygame.draw.line(surface, skin, (132, 102), (156, 168), 11)
        pygame.draw.line(surface, steel_dark, (44, 134), (34, 228), 10)
        pygame.draw.ellipse(surface, steel, (10, 118, 86, 98))
        pygame.draw.ellipse(surface, steel_dark, (10, 118, 86, 98), 5)
        pygame.draw.line(surface, steel_dark, (24, 166), (82, 166), 4)
        pygame.draw.line(surface, steel_dark, (52, 126), (52, 208), 4)
        pygame.draw.line(surface, leather, (158, 98), (178, 232), 7)
        pygame.draw.polygon(surface, steel, [(148, 92), (164, 30), (178, 30), (168, 100)])
        pygame.draw.polygon(surface, steel, [(164, 30), (172, 12), (180, 30)])
        pygame.draw.polygon(surface, steel_dark, [(160, 100), (176, 100), (172, 228), (164, 228)])
        pygame.draw.polygon(surface, steel, [(156, 228), (180, 228), (168, 250)])
        pygame.draw.line(surface, steel_dark, (154, 102), (180, 102), 2)
        pygame.draw.line(surface, skin, (86, 182), (76, 258), 13)
        pygame.draw.line(surface, skin, (118, 182), (128, 258), 13)
        pygame.draw.line(surface, steel_dark, (74, 258), (58, 274), 4)
        pygame.draw.line(surface, steel_dark, (130, 258), (146, 274), 4)
        return surface

    def _create_battle_mage_showcase_art(self):
        surface = pygame.Surface((220, 280), pygame.SRCALPHA)
        skin = (206, 166, 132)
        cloth = (118, 86, 180)
        cloth_dark = (70, 48, 118)
        glow = (116, 212, 255)
        steel = (184, 194, 214)
        steel_dark = (96, 104, 138)
        leather = (110, 74, 52)
        pygame.draw.circle(surface, skin, (102, 54), 24)
        pygame.draw.arc(surface, cloth_dark, (78, 32, 48, 40), 3.3, 6.1, 4)
        pygame.draw.polygon(surface, cloth, [(68, 84), (138, 84), (154, 208), (50, 208)])
        pygame.draw.polygon(surface, cloth_dark, [(68, 84), (102, 118), (138, 84), (154, 208), (50, 208)])
        pygame.draw.line(surface, glow, (102, 92), (102, 190), 3)
        pygame.draw.line(surface, skin, (74, 104), (54, 174), 11)
        pygame.draw.line(surface, skin, (130, 104), (154, 168), 11)
        pygame.draw.line(surface, leather, (150, 98), (172, 236), 7)
        pygame.draw.polygon(surface, steel, [(140, 92), (156, 34), (170, 34), (162, 100)])
        pygame.draw.polygon(surface, steel, [(156, 34), (163, 16), (170, 34)])
        pygame.draw.polygon(surface, steel_dark, [(154, 100), (168, 100), (166, 228), (156, 228)])
        pygame.draw.polygon(surface, steel, [(150, 228), (172, 228), (160, 248)])
        pygame.draw.circle(surface, glow, (56, 156), 10)
        pygame.draw.circle(surface, glow, (56, 156), 18, 2)
        pygame.draw.circle(surface, glow, (56, 156), 26, 1)
        pygame.draw.line(surface, glow, (56, 126), (56, 186), 2)
        pygame.draw.line(surface, glow, (26, 156), (86, 156), 2)
        pygame.draw.line(surface, glow, (36, 136), (76, 176), 2)
        pygame.draw.line(surface, glow, (76, 136), (36, 176), 2)
        pygame.draw.line(surface, skin, (86, 208), (76, 260), 13)
        pygame.draw.line(surface, skin, (118, 208), (128, 260), 13)
        pygame.draw.line(surface, cloth_dark, (74, 260), (58, 274), 4)
        pygame.draw.line(surface, cloth_dark, (130, 260), (146, 274), 4)
        return surface

    def _create_shaman_showcase_art(self):
        surface = pygame.Surface((220, 280), pygame.SRCALPHA)
        skin = (190, 150, 118)
        robe = (255, 214, 64)
        robe_dark = (164, 106, 18)
        staff = (118, 82, 54)
        glow = (82, 212, 182)
        ember = (255, 176, 54)
        bone = (215, 215, 198)

        pygame.draw.line(surface, staff, (164, 22), (170, 258), 8)
        pygame.draw.line(surface, bone, (146, 34), (182, 34), 5)
        pygame.draw.circle(surface, bone, (164, 24), 13)
        pygame.draw.circle(surface, robe_dark, (160, 22), 2)
        pygame.draw.circle(surface, robe_dark, (168, 22), 2)
        pygame.draw.arc(surface, robe_dark, (156, 24, 16, 10), 0.2, 2.9, 2)
        pygame.draw.line(surface, bone, (152, 34), (144, 48), 3)
        pygame.draw.line(surface, bone, (176, 34), (184, 48), 3)
        pygame.draw.polygon(surface, glow, [(144, 22), (134, 2), (148, 10)])
        pygame.draw.polygon(surface, ember, [(152, 18), (146, -2), (160, 10)])
        pygame.draw.polygon(surface, bone, [(176, 18), (184, -4), (190, 16)])
        pygame.draw.line(surface, glow, (164, 46), (164, 62), 3)

        pygame.draw.circle(surface, skin, (102, 54), 24)
        pygame.draw.polygon(surface, glow, [(80, 38), (90, 8), (102, 36)])
        pygame.draw.polygon(surface, ember, [(102, 34), (112, 4), (122, 34)])
        pygame.draw.polygon(surface, bone, [(118, 40), (132, 12), (138, 46)])
        pygame.draw.polygon(surface, robe_dark, [(78, 54), (90, 20), (112, 16), (128, 54), (116, 40), (88, 40)])
        pygame.draw.line(surface, robe_dark, (95, 64), (91, 78), 3)
        pygame.draw.line(surface, robe_dark, (109, 64), (113, 78), 3)
        pygame.draw.polygon(surface, robe_dark, [(86, 48), (102, 42), (118, 48), (114, 68), (90, 68)])
        pygame.draw.circle(surface, ember, (96, 54), 3)
        pygame.draw.circle(surface, ember, (108, 54), 3)
        pygame.draw.line(surface, ember, (98, 62), (106, 62), 2)
        pygame.draw.polygon(surface, robe, [(70, 86), (136, 86), (156, 212), (48, 212)])
        pygame.draw.polygon(surface, robe_dark, [(70, 86), (102, 118), (136, 86), (156, 212), (48, 212)])
        for bead_x, bead_y in ((88, 96), (96, 100), (104, 102), (112, 100), (120, 96)):
            pygame.draw.circle(surface, bone, (bead_x, bead_y), 4)
            pygame.draw.circle(surface, ember, (bead_x, bead_y), 2)
        pygame.draw.polygon(surface, robe_dark, [(92, 132), (102, 118), (112, 132), (108, 152), (96, 152)])
        pygame.draw.arc(surface, ember, (90, 128, 24, 20), 0.2, 2.9, 3)
        pygame.draw.line(surface, ember, (102, 126), (102, 148), 3)
        pygame.draw.line(surface, ember, (94, 138), (110, 138), 3)
        pygame.draw.line(surface, ember, (96, 148), (88, 156), 2)
        pygame.draw.line(surface, ember, (108, 148), (116, 156), 2)
        pygame.draw.polygon(surface, glow, [(58, 144), (70, 132), (82, 144), (70, 156)])
        pygame.draw.polygon(surface, ember, [(122, 156), (134, 144), (146, 156), (134, 168)])
        pygame.draw.line(surface, skin, (74, 104), (50, 176), 11)
        pygame.draw.line(surface, skin, (130, 104), (156, 168), 11)
        pygame.draw.line(surface, skin, (86, 210), (76, 260), 13)
        pygame.draw.line(surface, skin, (118, 210), (128, 260), 13)
        pygame.draw.line(surface, bone, (74, 260), (58, 274), 4)
        pygame.draw.line(surface, bone, (128, 260), (144, 274), 4)
        return surface

    def create_subclass_showcase_art(self):
        return {
            "Воин": self._create_warrior_showcase_art(),
            "Боевой маг": self._create_battle_mage_showcase_art(),
            "Варвар": self._create_barbarian_showcase_art(),
            "Шаман": self._create_shaman_showcase_art(),
        }

    def set_state(self, new_state):
        self.state = new_state

    def run(self):
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            if not self.running:
                break

            self.handle_events(events)
            self.update()
            self.render()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def handle_events(self, events):
        if self.state == self.MENU:
            self.handle_menu_events(events)
        elif self.state == self.NAME_INPUT:
            self.handle_name_events(events)
        elif self.state == self.CLASS_SELECT:
            self.handle_class_events(events)
        elif self.state == self.MAGIC_SELECT:
            self.handle_magic_events(events)
        elif self.state == self.STAT_SELECT:
            self.handle_stat_events(events)
        elif self.state == self.BATTLE:
            self.handle_battle_events(events)
        elif self.state == self.POST_BATTLE:
            self.handle_post_battle_events(events)

    def update(self):
        if self.state == self.BATTLE:
            if self.hit_timer > 0:
                self.hit_timer -= 1

            if self.show_info_idx is None and self.players:
                current_player = self.players[self.current_turn]
                if current_player.is_ai and pygame.time.get_ticks() >= self.ai_action_due:
                    self.perform_ai_turn(current_player)

    def render(self):
        if self.state == self.MENU:
            self.render_menu()
        elif self.state == self.NAME_INPUT:
            self.render_name_input()
        elif self.state == self.CLASS_SELECT:
            self.render_class_select()
        elif self.state == self.MAGIC_SELECT:
            self.render_magic_select()
        elif self.state == self.STAT_SELECT:
            self.render_stat_select()
        elif self.state == self.BATTLE:
            self.render_battle()
        elif self.state == self.POST_BATTLE:
            self.render_post_battle()

    def handle_menu_events(self, events):
        for event in events:
            for index, button in enumerate(self.menu_buttons, start=1):
                if button.clicked(event):
                    self.start_new_series(index)
                    return
            if self.menu_exit_button.clicked(event):
                self.running = False
                return

    def start_new_series(self, count):
        self.player_count = count
        self.human_names = [""] * count
        self.player_builds = [{"name": "", "class": None, "magic_path": None, "stats": []} for _ in range(count)]
        self.scores = {}
        self.rematch_mode = False
        self.name_index = 0
        self.name_buffer = ""
        self.rebuild_name_key_buttons()
        self.set_state(self.NAME_INPUT)

    def handle_name_events(self, events):
        for event in events:
            if self.name_confirm_button.clicked(event, enabled=bool(self.name_buffer.strip())):
                self.confirm_name_input()
                return
            if self.name_back_button.clicked(event):
                self.back_from_name_input()
                return
            if self.name_clear_button.clicked(event):
                self.name_buffer = ""
                return

            if self.name_space_button.clicked(event, enabled=len(self.name_buffer) < 12 and bool(self.name_buffer)):
                self.append_name_space()
                return
            if self.name_delete_button.clicked(event, enabled=bool(self.name_buffer)):
                self.delete_name_char()
                return

            for char, button in self.name_key_buttons:
                if button.clicked(event, enabled=len(self.name_buffer) < 12):
                    self.append_name_char(char)
                    return

    def append_name_char(self, char):
        if len(self.name_buffer) >= 12:
            return

        if char.isalpha():
            if not self.name_buffer or self.name_buffer.endswith(" "):
                char = char.upper()
            else:
                char = char.lower()

        self.name_buffer += char

    def append_name_space(self):
        if self.name_buffer and len(self.name_buffer) < 12 and not self.name_buffer.endswith(" "):
            self.name_buffer += " "

    def delete_name_char(self):
        if self.name_buffer:
            self.name_buffer = self.name_buffer[:-1]

    def rebuild_name_key_buttons(self):
        self.name_key_buttons = []
        keyboard_rows = [
            "йцукенгшщзхъ",
            "фывапролджэ",
            "ячсмитьбю.-",
        ]
        start_y = 430
        key_w = 58
        key_h = 58
        gap = 8
        for row_index, row in enumerate(keyboard_rows):
            row_width = len(row) * key_w + (len(row) - 1) * gap
            start_x = (WIDTH - row_width) // 2
            for col_index, char in enumerate(row):
                x = start_x + col_index * (key_w + gap)
                y = start_y + row_index * (key_h + gap)
                self.name_key_buttons.append((char, UIButton(char.upper(), x, y, key_w, key_h)))

    def confirm_name_input(self):
        self.human_names[self.name_index] = self.name_buffer.strip()
        if self.name_index < self.player_count - 1:
            self.name_index += 1
            self.name_buffer = self.human_names[self.name_index]
            return

        self.scores = {name: 0 for name in self.human_names}
        if self.player_count == 1:
            self.scores["AI"] = 0
        self.start_setup_flow(allow_back_to_names=True)

    def back_from_name_input(self):
        if self.name_index > 0:
            self.name_index -= 1
            self.name_buffer = self.human_names[self.name_index]
        else:
            self.set_state(self.MENU)

    def start_setup_flow(self, allow_back_to_names):
        self.allow_back_to_names = allow_back_to_names
        self.player_builds = [{"name": name, "class": None, "magic_path": None, "stats": []} for name in self.human_names]
        self.setup_index = 0
        self.selected_class = None
        self.selected_group = None
        self.selected_magic_path = None
        self.selected_stats = []
        self.set_state(self.CLASS_SELECT)

    def load_setup_state(self, index):
        build = self.player_builds[index]
        self.selected_class = build["class"]
        self.selected_group = self.get_group_for_class(self.selected_class) if self.selected_class else None
        self.selected_magic_path = build.get("magic_path")
        self.selected_stats = list(build["stats"])

    def handle_class_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.back_from_class_select()
                return

            for button in self.class_buttons:
                if button.clicked(event):
                    self.selected_group = button.text
                    subclasses = self.class_groups.get(button.text, [])
                    if len(subclasses) == 1:
                        self.selected_class = subclasses[0]
                    else:
                        self.selected_class = None
                    return

            if self.selected_group:
                subclasses = self.class_groups.get(self.selected_group, [])
                if len(subclasses) == 2 and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, sub_name in self.get_subclass_portrait_positions(self.selected_group):
                        if rect.collidepoint(event.pos):
                            self.selected_class = sub_name
                            return

            if self.class_confirm_button.clicked(event, enabled=bool(self.selected_class)):
                self.set_state(self.MAGIC_SELECT)
                return

    def get_group_for_class(self, class_name):
        for group, subclasses in self.class_groups.items():
            if class_name in subclasses:
                return group
        return None

    def get_subclass_portrait_positions(self, group_name):
        subclasses = self.class_groups.get(group_name, [])
        if len(subclasses) == 2:
            if group_name == "Боец":
                return [
                    (pygame.Rect(1270, 185, 185, 185), subclasses[0]),
                    (pygame.Rect(1518, 185, 185, 185), subclasses[1]),
                ]
            if group_name == "Дикарь":
                return [
                    (pygame.Rect(1270, 185, 185, 185), subclasses[0]),
                    (pygame.Rect(1518, 185, 185, 185), subclasses[1]),
                ]
            return [
                (pygame.Rect(1285, 185, 185, 185), subclasses[0]),
                (pygame.Rect(1498, 185, 185, 185), subclasses[1]),
            ]
        elif len(subclasses) == 1:
            return [(pygame.Rect(1320, 170, 220, 220), subclasses[0])]
        return []

    def back_from_class_select(self):
        if self.setup_index > 0:
            self.setup_index -= 1
            self.load_setup_state(self.setup_index)
            self.set_state(self.STAT_SELECT)
        elif self.allow_back_to_names:
            self.name_index = self.player_count - 1
            self.name_buffer = self.human_names[self.name_index]
            self.set_state(self.NAME_INPUT)

    def handle_magic_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.set_state(self.CLASS_SELECT)
                return

            for button in self.magic_buttons:
                if button.clicked(event):
                    self.selected_magic_path = button.text
                    return

            if self.magic_back_button.clicked(event):
                self.set_state(self.CLASS_SELECT)
                return

            if self.magic_confirm_button.clicked(event, enabled=bool(self.selected_magic_path)):
                self.set_state(self.STAT_SELECT)
                return

    def handle_stat_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.set_state(self.MAGIC_SELECT)
                return

            for button in self.stat_buttons:
                if button.clicked(event):
                    if button.text in self.selected_stats:
                        self.selected_stats.remove(button.text)
                    elif len(self.selected_stats) < 2:
                        self.selected_stats.append(button.text)
                    return

            if self.stat_back_button.clicked(event):
                self.set_state(self.MAGIC_SELECT)
                return

            if self.stat_confirm_button.clicked(event, enabled=len(self.selected_stats) == 2):
                self.confirm_player_build()
                return

    def confirm_player_build(self):
        self.player_builds[self.setup_index] = {
            "name": self.human_names[self.setup_index],
            "class": self.selected_class,
            "magic_path": self.selected_magic_path,
            "stats": list(self.selected_stats),
        }

        if self.setup_index < self.player_count - 1:
            self.setup_index += 1
            self.load_setup_state(self.setup_index)
            self.set_state(self.CLASS_SELECT)
            return

        self.start_battle()

    def start_battle(self):
        self.players = [self.build_human_player(build) for build in self.player_builds]
        if self.player_count == 1:
            self.players.append(self.create_ai_player())

        self.arena_name = self.apply_random_arena(self.players)
        self.players = self.order_players_for_battle(self.players)

        self.current_turn = 0
        self.bonus_turn_player = None
        self.selected_target = None
        self.hit_target = None
        self.hit_timer = 0
        self.log = [self.make_log_entry(f"🏟 Арена: {self.arena_name}", category="arena")]
        self.info_rects = [None] * len(self.players)
        self.show_info_idx = None
        self.close_popup_rect = None
        self.reset_spell_state()
        self.set_state(self.BATTLE)
        self.prepare_current_turn()

    def build_human_player(self, build):
        player = Player(build["name"])
        player.role = build["class"]
        player.magic_path = build.get("magic_path") or "Путь огня"
        self.apply_class_base_stats(player, build["class"])
        self.apply_stat_bonuses(player, build["stats"])
        player.calc()
        self.apply_class_bonuses(player, build["class"])
        return player

    def create_ai_player(self):
        ai_class = random.choice(list(self.class_data.keys()))
        ai_stats = random.sample(list(self.stat_data.keys()), 2)
        bot = Player("AI", True)
        bot.role = ai_class
        bot.magic_path = random.choice(list(self.magic_data.keys()))
        self.apply_class_base_stats(bot, ai_class)
        self.apply_stat_bonuses(bot, ai_stats)
        bot.calc()
        self.apply_class_bonuses(bot, ai_class)
        return bot

    def apply_class_base_stats(self, player, cls):
        class_info = self.class_data.get(cls, {})
        player.strength = class_info.get("strength", player.strength)
        player.stamina = class_info.get("stamina", player.stamina)
        player.agility = class_info.get("agility", player.agility)
        player.luck = class_info.get("luck", player.luck)
        player.initiative = class_info.get("initiative", player.initiative)
        player.intellect = class_info.get("intellect", player.intellect)

    def apply_stat_bonuses(self, player, stats):
        for stat in stats:
            if stat == "Сильный":
                player.strength += 10
            elif stat == "Выносливый":
                player.stamina += 10
            elif stat == "Ловкий":
                player.agility += 10
            elif stat == "Удачливый":
                player.luck += 10
            elif stat == "Инициативный":
                player.initiative += 10
            elif stat == "Интеллектуальный":
                player.intellect += 10

    def apply_class_bonuses(self, player, cls):
        return

    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test = (current_line + " " + word).strip()
            if font.size(test)[0] <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def get_class_color(self, class_name):
        return {
            "Воин": (90, 160, 255),
            "Варвар": (255, 165, 70),
            "Ассасин": (185, 120, 255),
            "Копейщик": (100, 220, 120),
            "Боевой маг": (180, 130, 255),
            "Шаман": (255, 186, 92),
        }.get(class_name, WHITE)

    def get_magic_path_color(self, path_name):
        return {
            "Путь огня": (255, 195, 70),
            "Путь воды": LIGHT_BLUE,
            "Путь земли": (150, 105, 60),
            "Путь воздуха": TURQUOISE,
            "Тёмный путь": (170, 100, 210),
            "Путь непознаваемого": (150, 235, 165),
        }.get(path_name, WHITE)

    def get_magic_path_key(self, path_name):
        return {
            "Путь огня": "fire",
            "Путь воды": "water",
            "Путь земли": "earth",
            "Путь воздуха": "air",
            "Тёмный путь": "dark",
            "Путь непознаваемого": "void",
        }.get(path_name, "neutral")

    def get_magic_tier_colors(self, path_name):
        return {
            "Путь огня": ((255, 195, 70), (255, 220, 70), GOLD),
            "Путь воды": (LIGHT_BLUE, LIGHT_BLUE, (70, 165, 255)),
            "Путь земли": ((150, 105, 60), (150, 105, 60), (205, 145, 80)),
            "Путь воздуха": (TURQUOISE, TURQUOISE, BRIGHT_TURQUOISE),
            "Тёмный путь": ((170, 100, 210), (170, 100, 210), (245, 105, 170)),
            "Путь непознаваемого": ((150, 235, 165), (150, 235, 165), (220, 255, 150)),
        }.get(path_name, (WHITE, WHITE, WHITE))

    def get_spell_button_colors(self, path_name, tier):
        if path_name == "Путь огня":
            return ((255, 185, 55), GOLD) if tier == "exalted" else ((255, 165, 40), (255, 225, 120))
        if path_name == "Путь воды":
            return ((100, 200, 255), (70, 165, 255)) if tier == "exalted" else (LIGHT_BLUE, (210, 245, 255))
        if path_name == "Путь земли":
            return ((165, 118, 72), (205, 145, 80)) if tier == "exalted" else ((130, 90, 55), (175, 125, 80))
        if path_name == "Путь воздуха":
            return ((70, 205, 200), BRIGHT_TURQUOISE) if tier == "exalted" else (TURQUOISE, (150, 255, 240))
        if path_name == "Тёмный путь":
            return ((185, 95, 215), (245, 105, 170)) if tier == "exalted" else ((135, 72, 162), (195, 125, 225))
        if path_name == "Путь непознаваемого":
            return ((150, 220, 130), (220, 255, 150)) if tier == "exalted" else ((112, 186, 126), (174, 244, 188))
        return (GRAY, WHITE)

    def draw_spell_button(self, button, font, path_name, tier):
        base_color, hover_color = self.get_spell_button_colors(path_name, tier)
        mouse = pygame.mouse.get_pos()
        color = hover_color if button.rect.collidepoint(mouse) else base_color
        pygame.draw.rect(self.screen, color, button.rect, border_radius=12)
        pygame.draw.rect(self.screen, WHITE, button.rect, 2, border_radius=12)
        txt = font.render(button.text, True, DARK)
        txt_rect = txt.get_rect(center=button.rect.center)
        self.screen.blit(txt, txt_rect)

    def get_info_line_color(self, line, class_name=None, magic_path=None):
        if line == "Пассивная способность:":
            return LIGHT_BLUE
        if line == "Активная способность:":
            return LIGHT_PINK
        if line.startswith("Пассивно:"):
            return LIGHT_BLUE
        if line.startswith("Активно:"):
            return LIGHT_PINK
        if line.startswith("Класс:") and class_name:
            return self.get_class_color(class_name)
        if line.startswith("Мистический путь:") and magic_path:
            return self.get_magic_path_color(magic_path)
        return WHITE

    def make_log_entry(self, text, category="normal", actor=None, verb=None, target=None, target_hit=None, indent=False):
        return {
            "text": text,
            "category": category,
            "actor": actor,
            "verb": verb,
            "target": target,
            "target_hit": target_hit,
            "indent": indent,
        }

    def append_log(self, text, category="normal", actor=None, verb=None, target=None, target_hit=None, indent=False):
        self.log.append(self.make_log_entry(text, category, actor, verb, target, target_hit, indent))

    def infer_log_color(self, text, category="normal"):
        lowered = text.lower()

        if category == "passive":
            return LIGHT_BLUE
        if category == "active":
            return LIGHT_PINK
        if category == "warning":
            return (255, 210, 120)
        if category == "arena":
            return (180, 230, 255)
        if category == "magic_fire_normal":
            return (255, 195, 70)
        if category == "magic_fire_exalted":
            return GOLD
        if category == "magic_water_normal":
            return LIGHT_BLUE
        if category == "magic_water_exalted":
            return (70, 165, 255)
        if category == "magic_earth_normal":
            return (150, 105, 60)
        if category == "magic_earth_exalted":
            return (205, 145, 80)
        if category == "magic_air_normal":
            return TURQUOISE
        if category == "magic_air_exalted":
            return BRIGHT_TURQUOISE
        if category == "magic_dark_normal":
            return (170, 100, 210)
        if category == "magic_dark_exalted":
            return (245, 105, 170)
        if category == "magic_void_normal":
            return (150, 235, 165)
        if category == "magic_void_exalted":
            return (220, 255, 150)

        if "крит" in lowered or "фатал" in lowered:
            return (255, 220, 70)
        if "кров" in lowered:
            return (255, 110, 110)
        if "оглуш" in lowered or "опрокинут" in lowered:
            return (140, 220, 255)
        if "обезоруж" in lowered or "оружие" in lowered or "подбирает" in lowered:
            return (140, 200, 255)
        if "берсерк" in lowered or "кровопускан" in lowered or "подсечк" in lowered or "щит" in lowered:
            return LIGHT_PINK

        return WHITE

    def _strip_all_smp(self, text):
        """Удаляет все SMP-символы (> U+FFFF) из текста; если есть цветной emoji-шрифт — оставляет как есть."""
        if self.has_color_emoji:
            return text
        return "".join(c for c in text if ord(c) <= 0xFFFF)

    def _uses_icon_font(self, char):
        return ord(char) > 0xFFFF or char in self.log_icon_chars

    def _split_runs(self, text):
        """Разбивает текст на [(str, is_emoji)] для символов, которые надо рисовать icon-шрифтом."""
        if not text:
            return []
        runs = []
        buf = ""
        buf_is_em = None
        for c in text:
            is_em = self._uses_icon_font(c)
            if buf_is_em is None:
                buf_is_em = is_em
            if is_em != buf_is_em:
                runs.append((buf, buf_is_em))
                buf = c
                buf_is_em = is_em
            else:
                buf += c
        if buf:
            runs.append((buf, buf_is_em))
        return runs

    def _measure_token(self, token, base_font):
        """Ширина токена с учётом emoji-шрифта."""
        if self.emoji_font is None:
            return base_font.size(token)[0]
        total = 0
        for run, is_em in self._split_runs(token):
            f = self.emoji_font if is_em else base_font
            total += f.size(run)[0]
        return total

    def _strip_leading_log_icon(self, text):
        if not text:
            return text
        trimmed = text.lstrip()
        while trimmed and (trimmed[0] in self.log_icon_chars or not trimmed[0].isalnum() and not trimmed[0].isalpha()):
            trimmed = trimmed[1:].lstrip()
        return trimmed or text.strip()

    def get_log_icon(self, text, category):
        """Иконка для строки лога. Только BMP-символы (Arial + Segoe UI Symbol)."""
        cat = str(category or "")
        low = (text or "").lower()
        if cat == "arena":                                          return "\u25ce "  # ◎
        if "magic_fire_exalted" in cat:                            return "\u2605\u26a1 "  # ★⚡
        if "magic_fire" in cat:                                    return "\u25b2 "  # ▲
        if "magic_water_exalted" in cat:                           return "\u2744\u25c6 "  # ❄◆
        if "magic_water" in cat:                                   return "\u25c6 "  # ◆
        if "magic_earth_exalted" in cat:                           return "\u25fc\u2605 "  # ◼★
        if "magic_earth" in cat:                                   return "\u25fc "  # ◼
        if "magic_air_exalted" in cat:                             return "\u2726\u2605 "  # ✦★
        if "magic_air" in cat:                                     return "\u2726 "  # ✦
        if "magic_dark_exalted" in cat:                            return "\u263d\u2605 "  # ☽★
        if "magic_dark" in cat:                                    return "\u263d "  # ☽
        if "magic_void_exalted" in cat:                            return "\u203b\u2605 "  # ※★
        if "magic_void" in cat:                                    return "\u203b "  # ※
        if cat == "warning":                                        return "\u26a0 "  # ⚠
        if cat == "passive":                                        return "\u2736 "  # ✶
        if cat == "active":                                         return "\u26a1 "  # ⚡
        if cat == "action":                                         return "\u2694 "  # ⚔
        # По содержимому текста
        if "крит" in low:                                           return "\u2605 "  # ★
        if "кров" in low:                                           return "\u2665 "  # ♥
        if "оглуш" in low or "опрокин" in low:                     return "\u25cb "  # ○
        if "замороз" in low or "заморо" in low:                    return "\u2744 "  # ❄
        if "горит" in low or "поджёг" in low or ("огн" in low and "огн" in low): return "\u25b2 "  # ▲
        if "исцел" in low or "восстанавл" in low:                  return "\u25c6 "  # ◆
        if "лут" in low or "предмет" in low:                       return "\u2295 "  # ⊕
        if "сгорает" in low or "гибел" in low or "помер" in low:  return "\u2620 "  # ☠
        if "уклон" in low:                                         return "\u21bb "  # ↻
        if "берсерк" in low or "отруб" in low:                    return "\u2692 "  # ⚒
        if "транс" in low or "камла" in low:                       return "\u21ba "  # ↺
        if "тотем" in low:                                         return "\u2665 "  # ♥
        if "камен" in low or "земл" in low:                       return "\u25fc "  # ◼
        if "ветр" in low or "воздух" in low or "молн" in low:     return "\u2726 "  # ✦
        if "мрак" in low or "тьм" in low or "бездна" in low:      return "\u263d "  # ☽
        if "непозна" in low or "извне" in low or "невозмож" in low:return "\u203b "  # ※
        if "заряд" in low or "зачаров" in low:                    return "\u26a1 "  # ⚡
        return "\u2022 "  # •

    def render_log_segments(self, segments, x, y, max_width, font):
        line_height = font.get_linesize() + 6
        current_x = x
        current_y = y
        # Вертикальное выравнивание emoji относительно обычного текста
        em_offset_y = max(0, (font.get_height() - self.emoji_font.get_height()) // 2) if self.emoji_font else 0

        for text, color in segments:
            parts = text.split(" ")
            for index, part in enumerate(parts):
                token = part if index == len(parts) - 1 else part + " "
                if not token:
                    continue
                token_width = self._measure_token(token, font)
                if current_x > x and current_x + token_width > x + max_width:
                    current_x = x
                    current_y += line_height
                if self.emoji_font is None:
                    surface = font.render(token, True, color)
                    self.screen.blit(surface, (current_x, current_y))
                    current_x += surface.get_width()
                else:
                    for run, is_em in self._split_runs(token):
                        f = self.emoji_font if is_em else font
                        oy = em_offset_y if is_em else 0
                        surface = f.render(run, True, color)
                        self.screen.blit(surface, (current_x, current_y + oy))
                        current_x += surface.get_width()

        return current_y + line_height

    def render_log_entry(self, entry, x, y, max_width):
        if isinstance(entry, dict) and (entry.get("category") == "action" or str(entry.get("category", "")).startswith("magic_")):
            segments = []
            cat = str(entry.get("category", ""))
            icon = self.get_log_icon(entry.get("text", ""), cat)
            indent_str = "   ▸ " if entry.get("indent") else ""
            segments.append((indent_str + icon, SILVER))

            actor = entry.get("actor") or ""
            verb = self._strip_all_smp(entry.get("verb") or entry.get("text", ""))
            target = entry.get("target")
            verb_color = self.infer_log_color(entry.get("text", ""), entry.get("category", "normal")) if str(entry.get("category", "")).startswith("magic_") else (WHITE if target else SILVER)

            if actor:
                segments.append((actor, (110, 255, 130)))
            if verb:
                segments.append((f" {verb}", verb_color))
            if target:
                target_color = (255, 220, 90) if entry.get("target_hit") is False else (255, 110, 110)
                segments.append((f" {target}", target_color))

            return self.render_log_segments(segments, x, y, max_width, self.log_font)

        text = entry["text"] if isinstance(entry, dict) else str(entry)
        category = entry.get("category", "normal") if isinstance(entry, dict) else "normal"
        indent_str = "   " if isinstance(entry, dict) and entry.get("indent") else ""
        color = self.infer_log_color(text, category)
        clean_text = self._strip_all_smp(text)
        display_text = self._strip_leading_log_icon(clean_text)
        icon = self.get_log_icon(display_text, category)
        return self.render_log_segments([(indent_str + icon + display_text, color)], x, y, max_width, self.log_font)

    def get_class_preview_stats(self, cls):
        data = self.class_data[cls]
        strength = data["strength"]
        stamina = data["stamina"]
        agility = data["agility"]
        luck = data["luck"]
        initiative = data.get("initiative", 10)
        intellect = data.get("intellect", 10)

        damage = strength
        dodge = agility * 2
        crit = luck * 2

        return {
            "strength": strength,
            "stamina": stamina,
            "agility": agility,
            "luck": luck,
            "initiative": initiative,
            "intellect": intellect,
            "damage": damage,
            "hp": stamina * 8,
            "dodge": dodge,
            "crit": crit,
            "insight": min(100, intellect * 2),
        }

    def get_stat_selection_preview(self, cls, selected_stats):
        preview = self.get_class_preview_stats(cls)
        for stat in selected_stats:
            if stat == "Сильный":
                preview["strength"] += 10
                preview["damage"] += 10
            elif stat == "Выносливый":
                preview["stamina"] += 10
                preview["hp"] += 80
            elif stat == "Ловкий":
                preview["agility"] += 10
                preview["dodge"] += 20
            elif stat == "Удачливый":
                preview["luck"] += 10
                preview["crit"] += 20
            elif stat == "Инициативный":
                preview["initiative"] += 10
            elif stat == "Интеллектуальный":
                preview["intellect"] += 10
                preview["insight"] = min(100, preview["insight"] + 20)
        return preview

    def get_insight_chance(self, player):
        return max(0, min(100, player.intellect * 2))

    def get_spell_damage(self, player, multiplier=1.0):
        wall_bonus = 1.5 if player.fire_wall_turns > 0 else 1.0
        unknowable_bonus = 1.5 if getattr(player, "unfathomable_next", False) else 1.0
        return max(1, int(player.intellect * multiplier * wall_bonus * unknowable_bonus))

    def get_spell_damage_and_crit(self, player, multiplier=1.0):
        """Возвращает (урон, is_crit). Крит доступен только Боевому магу."""
        base = self.get_spell_damage(player, multiplier)
        if player.role == "Боевой маг" and random.randint(1, 100) <= player.crit:
            return base * 2, True
        return base, False

    def has_stone_skin(self, player):
        return getattr(player, "stone_skin_turns", 0) > 0

    def has_shadow_shroud(self, player):
        return getattr(player, "shadow_shroud_turns", 0) > 0

    def is_secondary_effect_blocked(self, player):
        return self.has_stone_skin(player)

    def is_spellcasting_blocked(self, player):
        return self.has_stone_skin(player) and self.spell_tier != "exalted"

    def apply_damage(self, target, amount):
        amount = max(0, int(amount))
        if amount <= 0:
            return 0
        if self.has_stone_skin(target):
            amount = max(1, int(amount * 0.5))
        elif self.has_shadow_shroud(target):
            amount = max(1, int(amount * 0.6))
        target.hp = max(0, target.hp - amount)
        return amount

    def apply_soul_curse(self, target, turns=2):
        if target.soul_curse_turns <= 0:
            target.soul_curse_damage_base = target.damage
            target.soul_curse_intellect_base = target.intellect
        target.soul_curse_turns = max(target.soul_curse_turns, turns)
        target.damage = max(1, int(target.soul_curse_damage_base * 0.75))
        target.intellect = max(1, int(target.soul_curse_intellect_base * 0.75))
        return True

    def apply_bleeding(self, target, turns, bleed_damage):
        if self.is_secondary_effect_blocked(target):
            return False
        target.bleeding = max(target.bleeding, turns)
        target.bleed_damage = max(target.bleed_damage, max(1, bleed_damage))
        return True

    def apply_stun(self, target, turns=1):
        if self.is_secondary_effect_blocked(target):
            return False
        target.stunned = max(target.stunned, turns)
        return True

    def apply_disarm(self, target, turns=1):
        if self.is_secondary_effect_blocked(target):
            return False
        target.disarmed_turns = max(target.disarmed_turns, turns)
        return True

    def try_spell_dodge(self, caster, target, messages, spell_name):
        dodge_chance = max(0, target.dodge + target.temp_dodge)
        if random.randint(1, 100) <= dodge_chance:
            messages.append(self.make_log_entry(f"✨ {target.name} уклоняется от заклинания {spell_name} от {caster.name}!"))
            return True
        return False

    def reset_spell_state(self):
        self.spell_menu_open = False
        self.spell_tier = "normal"

    def get_spells_for_player(self, player, tier="normal"):
        path = self.magic_data.get(player.magic_path or "", {})
        return path.get(tier, [])

    def apply_burning(self, target, burn_damage, turns=2):
        if self.is_secondary_effect_blocked(target):
            return False
        target.burning = max(target.burning, turns)
        target.burn_damage = max(target.burn_damage, max(1, burn_damage))
        return True

    def apply_freeze(self, target, turns=1):
        if self.is_secondary_effect_blocked(target):
            return False
        target.frozen_turns = max(target.frozen_turns, turns)
        return True

    def decay_turn_effects(self, player):
        if player.fire_wall_turns > 0:
            if player.fire_wall_fresh:
                player.fire_wall_fresh = False
            else:
                player.fire_wall_turns -= 1
                if player.fire_wall_turns == 0:
                    self.append_log(f"🔥 Огненная стена вокруг {player.name} гаснет.")
        if player.shadow_shroud_turns > 0:
            if player.shadow_shroud_fresh:
                player.shadow_shroud_fresh = False
            else:
                player.shadow_shroud_turns -= 1
                if player.shadow_shroud_turns == 0:
                    player.dodge = max(0, player.dodge - 25)
                    self.append_log(f"☽ Покров мрака вокруг {player.name} рассеивается.", category="magic_dark_normal")
        if player.tailwind_turns > 0:
            if player.tailwind_fresh:
                player.tailwind_fresh = False
            else:
                player.tailwind_turns -= 1
                if player.tailwind_turns == 0:
                    player.dodge = max(0, player.dodge - 30)
                    self.append_log(f"✦ Попутный ветер вокруг {player.name} стихает.", category="magic_air_normal")
        if player.stone_skin_turns > 0:
            if player.stone_skin_fresh:
                player.stone_skin_fresh = False
            else:
                player.stone_skin_turns -= 1
                if player.stone_skin_turns == 0:
                    self.append_log(f"🪨 Каменная кожа {player.name} осыпается пылью.", category="magic_earth_normal")
        if player.weapon_enchanted_turns > 0:
            player.weapon_enchanted_turns -= 1
            if player.weapon_enchanted_turns == 0:
                self.append_log(f"⚡ Чары оружия {player.name} рассеиваются.")
        if player.totem_active:
            player.damage = player.totem_dmg_base
            player.dodge = player.totem_dodge_base
            player.totem_active = False
            self.append_log(f"🐺 Тотем зверя {player.name} затухает.")
        if player.trance_active:
            player.intellect = player.trance_intel_base
            player.trance_active = False
            self.append_log(f"🌀 {player.name} выходит из транса.")
        if player.soul_curse_turns > 0:
            player.soul_curse_turns -= 1
            if player.soul_curse_turns == 0:
                player.damage = player.soul_curse_damage_base
                player.intellect = player.soul_curse_intellect_base
                self.append_log(f"☽ Проклятие души спадает с {player.name}.", category="magic_dark_normal")

    def maybe_trigger_insight(self, player):
        if player.hp <= 0:
            return False
        if random.randint(1, 100) <= self.get_insight_chance(player):
            self.spell_menu_open = True
            self.spell_tier = "exalted"
            self.append_log(f"✨ {player.name} получает прозрение и может сотворить возвышенную магию!", category="active")
            return True
        return False

    def order_players_for_battle(self, players):
        grouped = {}
        for player in players:
            grouped.setdefault(player.initiative, []).append(player)

        ordered_players = []
        for initiative in sorted(grouped.keys(), reverse=True):
            same_initiative = grouped[initiative][:]
            while same_initiative:
                weights = [max(1, contender.luck) for contender in same_initiative]
                chosen = random.choices(same_initiative, weights=weights, k=1)[0]
                ordered_players.append(chosen)
                same_initiative.remove(chosen)

        return ordered_players

    def apply_random_arena(self, players):
        arena_name, arena_effect = random.choice(self.arena_data)
        for player in players:
            if arena_effect == "hp":
                player.max_hp += 10
                player.hp += 10
            elif arena_effect == "dodge":
                player.dodge += 10
            elif arena_effect == "damage":
                player.damage += 5
            elif arena_effect == "crit":
                player.crit += 10
        return arena_name

    def prepare_current_turn(self):
        while True:
            alive = [player for player in self.players if player.hp > 0]
            if len(alive) == 0:
                self.winner_name = "Никто"
                self.set_state(self.POST_BATTLE)
                return
            if len(alive) == 1:
                self.finish_battle(alive[0].name)
                return

            current = self.players[self.current_turn]
            if current.hp <= 0:
                self.current_turn = self.next_alive_index(self.current_turn)
                continue

            if current.temp_dodge > 0:
                current.temp_dodge = 0

            if current.stone_skin_turns > 0:
                self.append_log(f"🪨 {current.name} укрыт каменной кожей. Осталось ходов: {current.stone_skin_turns}", category="magic_earth_normal")
            if current.shadow_shroud_turns > 0:
                self.append_log(f"☽ {current.name} скрыт покровом мрака. Осталось ходов: {current.shadow_shroud_turns}", category="magic_dark_normal")
            if current.tailwind_turns > 0:
                self.append_log(f"✦ Ветер хранит {current.name}. Осталось ходов: {current.tailwind_turns}", category="magic_air_normal")

            if current.burning > 0:
                burn_damage = max(1, current.burn_damage)
                actual_burn = self.apply_damage(current, burn_damage)
                self.append_log(f"🔥 {current.name} горит и получает -{actual_burn} HP")
                current.burning -= 1
                if current.burning == 0:
                    current.burn_damage = 0
                if current.hp <= 0:
                    self.append_log(f"☠ {current.name} сгорает в пламени")
                    self.current_turn = self.next_alive_index(self.current_turn)
                    continue

            if current.bleeding > 0:
                bleed_damage = max(1, current.bleed_damage)
                actual_bleed = self.apply_damage(current, bleed_damage)
                self.append_log(f"🩸 {current.name} истекает кровью: -{actual_bleed} HP")
                current.bleeding -= 1
                if current.bleeding == 0:
                    current.bleed_damage = 0
                if current.hp <= 0:
                    self.append_log(f"☠ {current.name} пал от кровотечения")
                    self.current_turn = self.next_alive_index(self.current_turn)
                    continue

            if current.frozen_turns > 0:
                current.frozen_turns -= 1
                self.append_log(f"🧊 {current.name} заморожен и пропускает ход")
                self.current_turn = self.next_alive_index(self.current_turn)
                continue

            if current.stunned > 0:
                current.stunned -= 1
                self.append_log(f"💫 {current.name} оглушён и пропускает ход")
                if current.disarmed_turns > 0:
                    self.append_log(f"⚔ {current.name} приходит в себя и подбирает оружие")
                    current.disarmed_turns = 0
                self.current_turn = self.next_alive_index(self.current_turn)
                continue

            if current.disarmed_turns > 0:
                self.append_log(f"⚔ {current.name} обезоружен: активка заблокирована, урон вдвое меньше, лут -20%")

            if current.fire_wall_turns > 0:
                self.append_log(f"🔥 {current.name} окружён стеной огня. Осталось ходов: {current.fire_wall_turns}")

            # Тотем зверя: применяется в начале хода если был заряжен
            if current.totem_next and not current.totem_active:
                current.totem_active = True
                current.totem_next = False
                current.totem_dmg_base = current.damage
                current.totem_dodge_base = current.dodge
                current.damage = int(current.damage * 1.5)
                current.dodge = int(current.dodge * 1.5)
                self.append_log(f"🐺 {current.name}: тотем зверя усиливает! Сила и ловкость x1.5 на этот ход.", category="passive")

            # Транс шамана: применяется в начале хода
            if current.trance_next and not current.trance_active:
                current.trance_active = True
                current.trance_next = False
                current.trance_intel_base = current.intellect
                current.intellect = int(current.intellect * 1.5)
                self.append_log(f"🌀 {current.name}: транс! Интеллект x1.5 на этот ход.", category="passive")

            if current.weapon_enchanted_turns > 0:
                self.append_log(f"⚡ {current.name}: оружие заряжено магией. Осталось ходов: {current.weapon_enchanted_turns}")

            self.ai_action_due = pygame.time.get_ticks() + 700
            return

    def next_alive_index(self, start_index):
        for step in range(1, len(self.players) + 1):
            idx = (start_index + step) % len(self.players)
            if self.players[idx].hp > 0:
                return idx
        return start_index

    def advance_turn(self):
        if self.state != self.BATTLE:
            return
        current_player = self.players[self.current_turn]
        self.selected_target = None
        self.bonus_turn_player = None
        self.reset_spell_state()
        if current_player.disarmed_turns > 0:
            current_player.disarmed_turns = 0
            self.append_log(f"⚔ {current_player.name} подбирает оружие и снова готов к бою")
        # Пассивки в конце хода
        eot_messages = self.apply_end_of_turn_passives(current_player)
        if eot_messages:
            self.log.extend(eot_messages)
        self.decay_turn_effects(current_player)
        self.players = self.order_players_for_battle(self.players)
        self.current_turn = self.players.index(current_player)
        self.current_turn = self.next_alive_index(self.current_turn)
        self.prepare_current_turn()

    def try_grant_assassin_bonus_turn(self, player):
        if player.role != "Ассасин":
            return False
        if self.bonus_turn_player is player:
            return False
        if self.is_passive_blocked(player):
            return False
        if random.randint(1, 100) <= 30:
            self.bonus_turn_player = player
            self.selected_target = None
            self.append_log(f"🌫 {player.name} исчезает в тени и получает ещё 1 ход!", category="passive")
            if player.is_ai:
                self.ai_action_due = pygame.time.get_ticks() + 700
            return True
        return False

    def is_passive_blocked(self, player):
        return player.disarmed_turns > 0

    def get_attack_damage_scale(self, player):
        return 0.5 if player.disarmed_turns > 0 else 1.0

    def apply_fire_wall_melee_penalty(self, attacker, defender, messages):
        if defender.fire_wall_turns <= 0:
            return 1.0

        messages.append(self.make_log_entry(f"🔥 {attacker.name} атакует сквозь стену огня {defender.name} и теряет 20% урона."))
        if random.randint(1, 100) <= 30:
            burn_damage = max(1, int(defender.intellect * 0.5))
            if self.apply_burning(attacker, burn_damage):
                messages.append(self.make_log_entry(f"🔥 {attacker.name} загорается от пылающей стены и будет получать {burn_damage} урона ещё 2 хода."))
        return 0.8

    def execute_attack(self, attacker, defender, strong=False, cautious=False):
        messages = []
        damage_scale = self.get_attack_damage_scale(attacker) * self.apply_fire_wall_melee_penalty(attacker, defender, messages)
        damage_backup = attacker.damage
        defender_dodge_backup = defender.dodge
        defender_temp_dodge_backup = defender.temp_dodge
        ignore_dodge = False

        if attacker.role == "Копейщик" and not self.is_passive_blocked(attacker) and random.randint(1, 100) <= 60:
            ignore_dodge = True
            defender.dodge = 0
            defender.temp_dodge = 0
            messages.append(self.make_log_entry(f"🎯 {attacker.name} наносит точный удар и полностью игнорирует уклонение {defender.name}!", category="passive"))

        if damage_scale != 1.0:
            attacker.damage = max(1, int(attacker.damage * damage_scale))

        hp_before = defender.hp
        messages.extend(attack(attacker, defender, strong, cautious))

        attacker.damage = damage_backup
        defender.dodge = defender_dodge_backup
        defender.temp_dodge = defender_temp_dodge_backup

        hit_success = defender.hp < hp_before
        if hit_success:
            messages.extend(self.apply_on_hit_passives(attacker, defender))
            # Заряд оружия (Боевой маг)
            if attacker.weapon_enchanted_turns > 0 and random.randint(1, 100) <= 50:
                path_normal = self.magic_data.get(attacker.magic_path, {}).get("normal", [])
                enchant_spell = next((s for s in path_normal if s["id"] in ("fire_arrow", "ice_arrow")), None)
                if enchant_spell:
                    messages.append(self.make_log_entry(f"⚡ Заряженное оружие {attacker.name} высвобождает магию!", category="passive"))
                    if self.try_spell_dodge(attacker, defender, messages, f"заряда ({enchant_spell['name']})"):
                        pass  # Уклонился
                    else:
                        enc_dmg, enc_crit = self.get_spell_damage_and_crit(attacker, 1.0)
                        actual_enc_dmg = self.apply_damage(defender, enc_dmg)
                        crit_str = " (КРИТ)" if enc_crit else ""
                        if enchant_spell["id"] == "fire_arrow":
                            messages.append(self.make_log_entry(f"🔥 Магия огня наносит {actual_enc_dmg}{crit_str} доп. урона {defender.name}.", category="magic_fire_normal"))
                            if random.randint(1, 100) <= 25:
                                if self.apply_burning(defender, max(1, actual_enc_dmg // 3)):
                                    messages.append(self.make_log_entry(f"🔥 {defender.name} загорается!", category="magic_fire_normal"))
                        else:
                            messages.append(self.make_log_entry(f"🧊 Магия льда наносит {actual_enc_dmg}{crit_str} доп. урона {defender.name}.", category="magic_water_normal"))
                            if random.randint(1, 100) <= 15:
                                if self.apply_freeze(defender, 1):
                                    messages.append(self.make_log_entry(f"🧊 {defender.name} заморожен!", category="magic_water_normal"))

        return messages, hit_success

    def apply_on_hit_passives(self, attacker, defender):
        messages = []
        if self.is_passive_blocked(attacker):
            return messages

        if attacker.role == "Воин" and random.randint(1, 100) <= 40 and self.apply_disarm(defender, 1):
            messages.append(self.make_log_entry(f"🛡 {attacker.name} обезоруживает {defender.name}! Следующий ход жертвы будет ослаблен.", category="passive"))

        if attacker.role == "Варвар" and random.randint(1, 100) <= 25 and not self.is_secondary_effect_blocked(defender):
            roll = random.randint(1, 100)
            if roll <= 10 and not defender.arm_severed:
                defender.arm_severed = True
                defender.damage = max(1, defender.damage // 2)
                messages.append(self.make_log_entry(f"🪓 {attacker.name} отрубает руку {defender.name}! Урон жертвы навсегда снижен вдвое.", category="passive"))
            elif roll <= 20 and not defender.leg_severed:
                defender.leg_severed = True
                defender.initiative = 1
                messages.append(self.make_log_entry(f"🦿 {attacker.name} отрубает ногу {defender.name}! Инициатива жертвы падает до 1.", category="passive"))
            elif roll <= 23:
                defender.hp = 0
                messages.append(self.make_log_entry(f"💀 {attacker.name} отрубает голову {defender.name}! Мгновенная смерть.", category="passive"))

        return messages

    def apply_end_of_turn_passives(self, player):
        """Пассивки, срабатывающие в конце хода."""
        messages = []
        if player.role == "Шаман" and not self.is_passive_blocked(player):
            if random.randint(1, 100) <= 50:
                player.totem_next = True
                player.totem_dmg_base = player.damage
                player.totem_dodge_base = player.dodge
                messages.append(self.make_log_entry(f"🐺 {player.name}: тотем зверя активирован! Следующий ход: сила и ловкость ×1.5.", category="passive"))
        return messages

    def perform_special_action(self, player, target):
        messages = []
        hit_success = False

        if player.disarmed_turns > 0:
            messages.append(self.make_log_entry(f"⚔ {player.name} обезоружен и не может использовать активную способность!", category="warning"))
            return messages, hit_success, None
        if self.has_stone_skin(player):
            messages.append(self.make_log_entry(f"🪨 {player.name} скован каменной кожей и не может использовать активную способность!", category="warning"))
            return messages, hit_success, None

        melee_scale = 1.0
        if target is not None:
            melee_scale = self.apply_fire_wall_melee_penalty(player, target, messages)

        if player.role == "Воин":
            dmg = max(1, int(player.damage * 0.5 * melee_scale))
            actual_dmg = self.apply_damage(target, dmg)
            messages.append(self.make_log_entry(f"🛡 {player.name} бьёт щитом и наносит {actual_dmg} урона.", category="active"))
            if random.randint(1, 100) <= 30 and self.apply_stun(target, 1):
                messages.append(self.make_log_entry(f"💫 {target.name} оглушён на 1 ход!"))
            hit_success = True
            messages.extend(self.apply_on_hit_passives(player, target))
        elif player.role == "Варвар":
            dmg = max(1, int(player.damage * 2 * melee_scale))
            if random.randint(1, 100) <= 30:
                actual_self_dmg = self.apply_damage(player, dmg)
                messages.append(self.make_log_entry(f"🤯 {player.name} в ярости попадает по себе и получает {actual_self_dmg} урона!", category="active"))
                messages.extend(self.apply_on_hit_passives(player, player))
                hit_success = True
                return messages, hit_success, player
            actual_dmg = self.apply_damage(target, dmg)
            messages.append(self.make_log_entry(f"🪓 {player.name} впадает в берсерк и наносит {actual_dmg} урона.", category="active"))
            hit_success = True
            messages.extend(self.apply_on_hit_passives(player, target))
        elif player.role == "Ассасин":
            attack_messages, hit_success = self.execute_attack(player, target)
            messages.append(self.make_log_entry(f"🩸 {player.name} использует кровопускание против {target.name}.", category="active"))
            messages.extend(attack_messages)
            if hit_success and random.randint(1, 100) <= 60:
                bleed = max(1, int(player.damage * 0.4))
                if self.apply_bleeding(target, 3, bleed):
                    messages.append(self.make_log_entry(f"🩸 {target.name} истекает кровью: {bleed} урона ещё 3 хода."))
        elif player.role == "Копейщик":
            dmg = max(1, int(player.damage * 0.3 * melee_scale))
            actual_dmg = self.apply_damage(target, dmg)
            messages.append(self.make_log_entry(f"🦶 {player.name} проводит подсечку и наносит {actual_dmg} урона.", category="active"))
            if random.randint(1, 100) <= 50 and self.apply_stun(target, 1):
                messages.append(self.make_log_entry(f"💫 {target.name} опрокинут и пропускает 1 ход!"))
            hit_success = True
        elif player.role == "Боевой маг":
            player.weapon_enchanted_turns = 2
            messages.append(self.make_log_entry(f"⚡ {player.name} заряжает оружие магией на 2 хода! При ударе — 50% шанс дополнительного магического удара.", category="active"))
            hit_success = False
            target = None
        elif player.role == "Шаман":
            player.trance_next = True
            messages.append(self.make_log_entry(f"🌀 {player.name} входит в транс. На следующем ходу интеллект возрастёт в 1.5 раза.", category="active"))
            hit_success = False
            target = None

        return messages, hit_success, target

    def perform_spell_action(self, player, spell_id, target=None, tier="normal"):
        messages = []
        hit_success = False
        actual_target = target

        if spell_id == "fire_arrow":
            if self.try_spell_dodge(player, target, messages, "Стрела огня"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.0)
            actual_dmg = self.apply_damage(target, dmg)
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"🔥 {player.name} выпускает огненную стрелу и наносит {actual_dmg}{crit_str} урона.", category="magic_fire_normal"))
            if random.randint(1, 100) <= 50:
                burn_damage = max(1, int(actual_dmg * 0.5))
                if self.apply_burning(target, burn_damage):
                    messages.append(self.make_log_entry(f"🔥 {target.name} подожжён и будет получать по {burn_damage} урона ещё 2 хода.", category="magic_fire_normal"))
            hit_success = True
        elif spell_id == "fire_wall":
            player.fire_wall_turns = 2
            player.fire_wall_fresh = True
            actual_target = player
            hit_success = True
            messages.append(self.make_log_entry(f"🔥 {player.name} воздвигает вокруг себя стену огня на 2 хода.", category="magic_fire_normal"))
        elif spell_id == "stone_skin":
            actual_target = player
            player.stone_skin_turns = 2
            player.stone_skin_fresh = True
            hit_success = True
            messages.append(self.make_log_entry(f"🪨 {player.name} покрывает себя каменной кожей на 2 хода. Весь входящий урон снижен вдвое, а дополнительные эффекты больше не проходят.", category="magic_earth_normal"))
        elif spell_id == "stone_spikes":
            if self.try_spell_dodge(player, target, messages, "Каменные шипы"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.0)
            actual_dmg = self.apply_damage(target, dmg)
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"🪨 {player.name} поднимает каменные шипы и наносит {actual_dmg}{crit_str} урона {target.name}.", category="magic_earth_normal"))
            if random.randint(1, 100) <= 30:
                if random.randint(0, 1) == 0:
                    bleed_damage = max(1, int(actual_dmg * 0.4))
                    if self.apply_bleeding(target, 3, bleed_damage):
                        messages.append(self.make_log_entry(f"🩸 Шипы пронзают {target.name}: кровотечение на 3 хода по {bleed_damage} урона.", category="magic_earth_normal"))
                else:
                    if self.apply_stun(target, 1):
                        messages.append(self.make_log_entry(f"◼ {target.name} скован камнем и пропустит следующий ход!", category="magic_earth_normal"))
            hit_success = True
        elif spell_id == "supernova":
            if self.try_spell_dodge(player, target, messages, "Сверхновая"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.5)
            actual_dmg = self.apply_damage(target, dmg)
            hit_success = True
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"☀ {player.name} вызывает сверхновую и обрушивает {actual_dmg}{crit_str} урона на {target.name}!", category="magic_fire_exalted"))
            for other in [p for p in self.players if p.hp > 0 and p != target]:
                if random.randint(1, 100) <= 50:
                    if self.try_spell_dodge(player, other, messages, "осколков сверхновой"):
                        continue
                    splash_dmg = self.apply_damage(other, dmg)
                    messages.append(self.make_log_entry(f"💥 Взрыв задевает {other.name}: -{splash_dmg} HP", category="magic_fire_exalted"))
        elif spell_id == "phoenix":
            actual_target = player
            roll = random.randint(1, 100)
            if roll <= 70:
                restored = max(0, player.max_hp - player.hp)
                player.hp = max(player.hp, player.max_hp)
                hit_success = restored > 0
                messages.append(self.make_log_entry(f"🕊 {player.name} пробуждает Феникса и восстанавливает {restored} HP!", category="magic_fire_exalted"))
            elif roll <= 85:
                player.hp = 0
                messages.append(self.make_log_entry(f"🔥 {player.name} не удерживает пламя Феникса и сгорает дотла!", category="magic_fire_exalted"))
            else:
                messages.append(self.make_log_entry(f"✨ Пламя Феникса не отвечает {player.name}.", category="magic_fire_exalted"))
        elif spell_id == "heal":
            actual_target = player
            heal_amount = player.intellect
            if random.randint(1, 100) <= 25:
                restored = max(0, player.max_hp - player.hp)
                player.hp = max(player.hp, player.max_hp)
                messages.append(self.make_log_entry(f"💧 {player.name} применяет исцеление и восстанавливает {restored} HP!", category="magic_water_normal"))
            else:
                restored = heal_amount
                player.hp += heal_amount
                messages.append(self.make_log_entry(f"💧 {player.name} восстанавливает {restored} HP.", category="magic_water_normal"))
            hit_success = restored > 0
        elif spell_id == "ice_arrow":
            if self.try_spell_dodge(player, target, messages, "Ледяная стрела"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.0)
            actual_dmg = self.apply_damage(target, dmg)
            hit_success = True
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"🧊 {player.name} выпускает ледяную стрелу и наносит {actual_dmg}{crit_str} урона.", category="magic_water_normal"))
            if random.randint(1, 100) <= 20:
                if self.apply_freeze(target, 1):
                    messages.append(self.make_log_entry(f"🧊 {target.name} заморожен на 1 ход!", category="magic_water_normal"))
        elif spell_id == "water_essence":
            actual_target = player
            if random.randint(1, 100) <= 80:
                restored = max(0, player.max_hp - player.hp)
                player.hp = max(player.hp, player.max_hp)
                hit_success = restored > 0
                messages.append(self.make_log_entry(f"🌊 {player.name} раскрывает Суть воды и восстанавливает {restored} HP!", category="magic_water_exalted"))
                if random.randint(1, 100) <= 60:
                    healed_targets = []
                    for other in self.players:
                        if other.hp > 0:
                            other.hp = max(other.hp, other.max_hp)
                            healed_targets.append(other.name)
                    messages.append(self.make_log_entry(f"🌊 Волна гармонии исцеляет всех живых бойцов: {', '.join(healed_targets)}.", category="magic_water_exalted"))
            else:
                messages.append(self.make_log_entry(f"🌊 Поток ускользает от {player.name}, и Суть воды не срабатывает.", category="magic_water_exalted"))
        elif spell_id == "ice_spear":
            if self.try_spell_dodge(player, target, messages, "Ледяное копьё"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 2.0)
            actual_dmg = self.apply_damage(target, dmg)
            hit_success = True
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"❄ {player.name} пронзает {target.name} ледяным копьём на {actual_dmg}{crit_str} урона.", category="magic_water_exalted"))
            freeze_proc = random.randint(1, 100) <= 20
            if freeze_proc and target.frozen_turns > 0:
                if random.randint(1, 100) <= 33:
                    target.hp = 0
                    messages.append(self.make_log_entry(f"🧊 {target.name} уже был заморожен и раскалывается на куски!", category="magic_water_exalted"))
                else:
                    bonus_damage = player.intellect
                    actual_bonus = self.apply_damage(target, bonus_damage)
                    messages.append(self.make_log_entry(f"🧊 Повторная заморозка не раскалывает {target.name}, но наносит ещё {actual_bonus} урона.", category="magic_water_exalted"))
            elif freeze_proc:
                if self.apply_freeze(target, 1):
                    messages.append(self.make_log_entry(f"🧊 {target.name} заморожен на 1 ход!", category="magic_water_exalted"))
        elif spell_id == "earth_blast":
            if self.try_spell_dodge(player, target, messages, "Взрыв земли"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.5)
            actual_dmg = self.apply_damage(target, dmg)
            hit_success = True
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"◼ {player.name} взрывает землю под {target.name} и наносит {actual_dmg}{crit_str} урона!", category="magic_earth_exalted"))
            if random.randint(1, 100) <= 50 and self.apply_stun(target, 1):
                messages.append(self.make_log_entry(f"◼ {target.name} ошеломлён ударной волной и пропустит ход!", category="magic_earth_exalted"))
            for other in [p for p in self.players if p.hp > 0 and p not in (player, target)]:
                if random.randint(1, 100) <= 65:
                    if self.try_spell_dodge(player, other, messages, "осколков взрыва земли"):
                        continue
                    splash_dmg = self.apply_damage(other, dmg)
                    messages.append(self.make_log_entry(f"◼ Обломки земли задевают {other.name}: -{splash_dmg} HP", category="magic_earth_exalted"))
        elif spell_id == "earthquake":
            hit_success = False
            messages.append(self.make_log_entry(f"◼ {player.name} обрушивает землетрясение на арену!", category="magic_earth_exalted"))
            for other in [p for p in self.players if p.hp > 0 and p.magic_path != "Путь земли"]:
                if other != player and self.try_spell_dodge(player, other, messages, "землетрясения"):
                    continue
                quake_dmg = self.apply_damage(other, self.get_spell_damage(player, 0.7))
                if quake_dmg > 0:
                    hit_success = True
                    messages.append(self.make_log_entry(f"◼ Земля разламывается под {other.name}: -{quake_dmg} HP", category="magic_earth_exalted"))
                    stun_chance = 50 if other == target else 30
                    if random.randint(1, 100) <= stun_chance and self.apply_stun(other, 1):
                        messages.append(self.make_log_entry(f"◼ {other.name} ошеломлён толчками и пропустит ход!", category="magic_earth_exalted"))
        elif spell_id == "wind_blades":
            if self.try_spell_dodge(player, target, messages, "Лезвия ветра"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.0)
            actual_dmg = self.apply_damage(target, dmg)
            hit_success = True
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"✦ {player.name} выпускает лезвия ветра и наносит {actual_dmg}{crit_str} урона {target.name}.", category="magic_air_normal"))
            if random.randint(1, 100) <= 30:
                bleed_damage = max(1, int(actual_dmg * 0.4))
                if self.apply_bleeding(target, 3, bleed_damage):
                    messages.append(self.make_log_entry(f"♥ Воздушные порезы открывают кровотечение у {target.name}: {bleed_damage} урона ещё 3 хода.", category="magic_air_normal"))
        elif spell_id == "tailwind":
            actual_target = player
            if player.tailwind_turns <= 0:
                player.dodge += 30
            player.tailwind_turns = max(player.tailwind_turns, 3)
            player.tailwind_fresh = True
            hit_success = True
            messages.append(self.make_log_entry(f"✦ {player.name} призывает попутный ветер и получает +30% к уклонению на текущий и ещё 2 следующих своих хода.", category="magic_air_normal"))
        elif spell_id == "sky_thunder":
            if self.try_spell_dodge(player, target, messages, "Небесная молния"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 2.2)
            actual_dmg = self.apply_damage(target, dmg)
            hit_success = True
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"✦ {player.name} низводит небесную молнию и наносит {actual_dmg}{crit_str} урона {target.name}.", category="magic_air_exalted"))
            if random.randint(1, 100) <= 35 and self.apply_stun(target, 1):
                messages.append(self.make_log_entry(f"✦ {target.name} ошеломлён ударом молнии!", category="magic_air_exalted"))
            chain_targets = [p for p in self.players if p.hp > 0 and p not in (player, target)]
            if chain_targets and random.randint(1, 100) <= 50:
                chained = random.choice(chain_targets)
                if not self.try_spell_dodge(player, chained, messages, "цепной молнии"):
                    chain_dmg = self.apply_damage(chained, self.get_spell_damage(player, 1.1))
                    messages.append(self.make_log_entry(f"✦ Цепная молния перескакивает на {chained.name}: -{chain_dmg} HP", category="magic_air_exalted"))
        elif spell_id == "storm_front":
            actual_target = target
            hit_success = False
            messages.append(self.make_log_entry(f"✦ {player.name} раскрывает ураганный фронт!", category="magic_air_exalted"))
            for other in [p for p in self.players if p.hp > 0 and p != player]:
                if self.try_spell_dodge(player, other, messages, "ураганного фронта"):
                    continue
                storm_dmg = self.apply_damage(other, self.get_spell_damage(player, 0.9))
                if storm_dmg > 0:
                    hit_success = True
                    messages.append(self.make_log_entry(f"✦ Буря рвёт {other.name}: -{storm_dmg} HP", category="magic_air_exalted"))
                disarm_chance = 80 if other == target else 40
                if random.randint(1, 100) <= disarm_chance and self.apply_disarm(other, 1):
                    messages.append(self.make_log_entry(f"✦ Порыв выбивает оружие из рук {other.name}!", category="magic_air_exalted"))
        elif spell_id == "shadow_shroud":
            actual_target = player
            if player.shadow_shroud_turns <= 0:
                player.dodge += 25
            player.shadow_shroud_turns = 2
            player.shadow_shroud_fresh = True
            hit_success = True
            messages.append(self.make_log_entry(f"☽ {player.name} окутывает себя покровом мрака: урон снижен, уклонение повышено на 25%.", category="magic_dark_normal"))
        elif spell_id == "soul_reap":
            if self.try_spell_dodge(player, target, messages, "Жатва души"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.1)
            actual_dmg = self.apply_damage(target, dmg)
            healed = max(1, actual_dmg // 2)
            player.hp = min(player.max_hp, player.hp + healed)
            crit_str = " (КРИТ)" if crit_hit else ""
            messages.append(self.make_log_entry(f"☽ {player.name} пожинает душу {target.name} и наносит {actual_dmg}{crit_str} урона, восстанавливая {healed} HP.", category="magic_dark_normal"))
            if random.randint(1, 100) <= 35:
                self.apply_soul_curse(target, 2)
                messages.append(self.make_log_entry(f"☽ Душа {target.name} скована проклятием: урон и интеллект снижены на 25% на 2 хода.", category="magic_dark_normal"))
            hit_success = True
        elif spell_id == "black_sun":
            if self.try_spell_dodge(player, target, messages, "Чёрное солнце"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 2.2)
            actual_dmg = self.apply_damage(target, dmg)
            crit_str = " (КРИТ)" if crit_hit else ""
            hit_success = True
            messages.append(self.make_log_entry(f"☽ {player.name} раскрывает Чёрное солнце и обрушивает {actual_dmg}{crit_str} урона на {target.name}.", category="magic_dark_exalted"))
            if random.randint(1, 100) <= 50 and self.apply_stun(target, 1):
                messages.append(self.make_log_entry(f"☽ {target.name} оглушён мраком Чёрного солнца!", category="magic_dark_exalted"))
            for other in [p for p in self.players if p.hp > 0 and p not in (player, target)]:
                if random.randint(1, 100) <= 75:
                    if self.try_spell_dodge(player, other, messages, "теней Чёрного солнца"):
                        continue
                    splash = self.apply_damage(other, self.get_spell_damage(player, 1.1))
                    messages.append(self.make_log_entry(f"☽ Тени Чёрного солнца задевают {other.name}: -{splash} HP", category="magic_dark_exalted"))
        elif spell_id == "abyss_name":
            if self.try_spell_dodge(player, target, messages, "Имя Бездны"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.6)
            actual_dmg = self.apply_damage(target, dmg)
            crit_str = " (КРИТ)" if crit_hit else ""
            hit_success = True
            messages.append(self.make_log_entry(f"☽ {player.name} произносит Имя Бездны и наносит {actual_dmg}{crit_str} урона {target.name}.", category="magic_dark_exalted"))
            if target.hp > 0 and target.hp <= int(target.max_hp * 0.35):
                target.hp = 0
                messages.append(self.make_log_entry(f"☽ Бездна узнаёт {target.name} и мгновенно забирает его!", category="magic_dark_exalted"))
            else:
                bleed = max(1, int(actual_dmg * 0.5))
                if self.apply_bleeding(target, 3, bleed):
                    messages.append(self.make_log_entry(f"♥ Бездна рвёт сущность {target.name}: кровотечение на 3 хода по {bleed} урона.", category="magic_dark_exalted"))
        elif spell_id == "impossible_angle":
            if self.try_spell_dodge(player, target, messages, "Невозможный угол"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 0.5)
            actual_dmg = self.apply_damage(target, dmg)
            crit_str = " (КРИТ)" if crit_hit else ""
            hit_success = True
            messages.append(self.make_log_entry(f"※ {player.name} выворачивает пространство и наносит {actual_dmg}{crit_str} урона {target.name}.", category="magic_void_normal"))
            roll = random.choice(("stun", "freeze", "disarm", "bleed", "burn"))
            if roll == "stun" and self.apply_stun(target, 1):
                messages.append(self.make_log_entry(f"※ Логика мира ломается: {target.name} оглушён.", category="magic_void_normal"))
            elif roll == "freeze" and self.apply_freeze(target, 1):
                messages.append(self.make_log_entry(f"※ Реальность застывает вокруг {target.name}.", category="magic_void_normal"))
            elif roll == "disarm" and self.apply_disarm(target, 1):
                messages.append(self.make_log_entry(f"※ Пространство выворачивает оружие из рук {target.name}.", category="magic_void_normal"))
            elif roll == "burn" and self.apply_burning(target, max(1, int(max(1, actual_dmg) * 0.5))):
                messages.append(self.make_log_entry(f"※ Искажённая геометрия поджигает саму плоть {target.name}.", category="magic_void_normal"))
            else:
                bleed = max(1, int(actual_dmg * 0.35))
                if self.apply_bleeding(target, 3, bleed):
                    messages.append(self.make_log_entry(f"♥ Искажённый разрез оставляет {target.name} истекать кровью по {bleed} урона 3 хода.", category="magic_void_normal"))
        elif spell_id == "outer_whisper":
            actual_target = player
            if random.randint(1, 100) <= 65:
                player.unfathomable_next = True
                hit_success = True
                messages.append(self.make_log_entry(f"※ {player.name} слышит шёпот извне. Возвышенная магия открыта прямо сейчас, а следующее заклинание усилено в 1.5 раза.", category="magic_void_normal"))
            else:
                messages.append(self.make_log_entry(f"※ Шёпот извне ускользает от {player.name}, и реальность не раскрывается.", category="magic_void_normal"))
        elif spell_id == "doorless_gate":
            if self.try_spell_dodge(player, target, messages, "Врата без двери"):
                return messages, False, target
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 2.3)
            actual_dmg = self.apply_damage(target, dmg)
            crit_str = " (КРИТ)" if crit_hit else ""
            hit_success = True
            messages.append(self.make_log_entry(f"※ {player.name} открывает Врата без двери и наносит {actual_dmg}{crit_str} урона {target.name}.", category="magic_void_exalted"))
            for other in [p for p in self.players if p.hp > 0 and p not in (player, target)]:
                if random.randint(1, 100) <= 65:
                    if self.try_spell_dodge(player, other, messages, "осколков невозможного"):
                        continue
                    splash = self.apply_damage(other, self.get_spell_damage(player, 0.9))
                    messages.append(self.make_log_entry(f"※ Волна невозможного ломает {other.name}: -{splash} HP", category="magic_void_exalted"))
                    if random.randint(1, 100) <= 30:
                        extra = random.choice(("stun", "freeze", "burn", "disarm"))
                        if extra == "stun" and self.apply_stun(other, 1):
                            messages.append(self.make_log_entry(f"※ {other.name} ошеломлён невозможным ударом.", category="magic_void_exalted"))
                        elif extra == "freeze" and self.apply_freeze(other, 1):
                            messages.append(self.make_log_entry(f"※ {other.name} застывает в трещине реальности.", category="magic_void_exalted"))
                        elif extra == "burn" and self.apply_burning(other, max(1, splash // 3)):
                            messages.append(self.make_log_entry(f"※ Чужой жар охватывает {other.name}.", category="magic_void_exalted"))
                        elif extra == "disarm" and self.apply_disarm(other, 1):
                            messages.append(self.make_log_entry(f"※ Мир отказывается держать оружие {other.name}.", category="magic_void_exalted"))
        elif spell_id == "unknowable_touch":
            if self.try_spell_dodge(player, target, messages, "Касание непознаваемого"):
                return messages, False, target
            effect_count = sum([
                target.bleeding > 0,
                target.burning > 0,
                target.frozen_turns > 0,
                target.stunned > 0,
                target.disarmed_turns > 0,
                target.soul_curse_turns > 0,
            ])
            dmg, crit_hit = self.get_spell_damage_and_crit(player, 1.6 + 1.0 * effect_count)
            actual_dmg = self.apply_damage(target, dmg)
            crit_str = " (КРИТ)" if crit_hit else ""
            hit_success = True
            messages.append(self.make_log_entry(f"※ {player.name} касается непознаваемого и наносит {actual_dmg}{crit_str} урона {target.name}.", category="magic_void_exalted"))
            if effect_count > 0:
                target.bleeding = 0
                target.bleed_damage = 0
                target.burning = 0
                target.burn_damage = 0
                target.frozen_turns = 0
                target.stunned = 0
                target.disarmed_turns = 0
                if target.soul_curse_turns > 0:
                    target.soul_curse_turns = 0
                    target.damage = target.soul_curse_damage_base
                    target.intellect = target.soul_curse_intellect_base
                messages.append(self.make_log_entry(f"※ Все искажения на {target.name} сорваны и поглощены непознаваемым.", category="magic_void_exalted"))
            else:
                extra_pool = ["stun", "freeze", "disarm", "bleed", "burn"]
                random.shuffle(extra_pool)
                for extra in extra_pool[:2]:
                    if extra == "stun" and self.apply_stun(target, 1):
                        messages.append(self.make_log_entry(f"※ {target.name} ошеломлён касанием непознаваемого.", category="magic_void_exalted"))
                    elif extra == "freeze" and self.apply_freeze(target, 1):
                        messages.append(self.make_log_entry(f"※ Реальность застывает вокруг {target.name}.", category="magic_void_exalted"))
                    elif extra == "disarm" and self.apply_disarm(target, 1):
                        messages.append(self.make_log_entry(f"※ Оружие выпадает из рук {target.name}.", category="magic_void_exalted"))
                    elif extra == "bleed":
                        bleed = max(1, int(actual_dmg * 0.35))
                        if self.apply_bleeding(target, 3, bleed):
                            messages.append(self.make_log_entry(f"♥ На теле {target.name} раскрываются невозможные раны: {bleed} урона 3 хода.", category="magic_void_exalted"))
                    elif extra == "burn" and self.apply_burning(target, max(1, actual_dmg // 3)):
                        messages.append(self.make_log_entry(f"※ Чужой огонь вгрызается в {target.name}.", category="magic_void_exalted"))

        if player.unfathomable_next and spell_id != "outer_whisper":
            player.unfathomable_next = False

        return messages, hit_success, actual_target

    def perform_loot_action(self, player):
        messages = [self.make_log_entry(f"{player.name} ищет предмет", category="action", actor=player.name, verb="ищет предмет", indent=True)]
        luck_backup = player.luck
        if player.disarmed_turns > 0:
            player.luck -= 20
        loot_result = loot(player)
        player.luck = luck_backup
        if isinstance(loot_result, str) and loot_result:
            messages.append(self.make_log_entry(f"🎒 {player.name} {loot_result}"))
        else:
            messages.append(self.make_log_entry(f"🎒 {player.name} ничего не нашёл"))
        return messages

    def get_spell_by_button_index(self, player, index):
        spells = self.get_spells_for_player(player, self.spell_tier)
        if 0 <= index < len(spells):
            return spells[index]
        return None

    def toggle_spell_menu(self):
        if self.spell_tier == "exalted":
            return
        if self.state == self.BATTLE and 0 <= self.current_turn < len(self.players):
            current = self.players[self.current_turn]
            if self.is_spellcasting_blocked(current):
                self.append_log(f"🪨 {current.name} покрыт каменной кожей и не может колдовать.", category="warning")
                return
        self.spell_menu_open = not self.spell_menu_open

    def perform_spell_cast(self, player, spell, target=None):
        spell_id = spell["id"]
        if self.is_spellcasting_blocked(player):
            self.append_log(f"🪨 {player.name} покрыт каменной кожей и не может колдовать.", category="warning")
            return False
        path_key = self.get_magic_path_key(player.magic_path)
        category = f"magic_{path_key}_{self.spell_tier}"
        requires_target = spell.get("target") == "enemy"
        if requires_target and (target is None or target.hp <= 0):
            self.append_log("Сначала выберите цель для заклинания", category="warning")
            return False

        actual_target = target if requires_target else player
        messages, hit_success, result_target = self.perform_spell_action(player, spell_id, actual_target, self.spell_tier)
        shown_target = actual_target.name if requires_target and actual_target else None
        self.append_log(
            f"{player.name} колдует {spell['name']}",
            category=category,
            actor=player.name,
            verb=f"колдует {spell['name']}",
            target=shown_target,
            target_hit=hit_success if requires_target else None,
            indent=True,
        )
        if messages:
            self.log.extend(messages)
        self.hit_target = result_target
        self.hit_timer = 10 if result_target else 0
        self.normalize_health()

        if spell_id == "outer_whisper" and hit_success and player.hp > 0:
            self.spell_menu_open = True
            self.spell_tier = "exalted"
            return True

        if self.spell_tier == "normal" and self.maybe_trigger_insight(player):
            return True

        self.advance_turn()
        return True

    def handle_battle_events(self, events):
        current = self.players[self.current_turn]

        for event in events:
            if self.show_info_idx is not None:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.show_info_idx = None
                    return
                if self.close_popup_rect and self.close_popup_rect.collidepoint(getattr(event, "pos", (-1, -1))):
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.show_info_idx = None
                        return
                continue

            if current.is_ai:
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(self.info_rects):
                    if rect and rect.collidepoint(event.pos):
                        self.show_info_idx = idx
                        return

                for player, rect in self.get_target_rects():
                    if rect.collidepoint(event.pos) and player != current and player.hp > 0:
                        self.selected_target = player
                        return

                if self.spell_menu_open:
                    for index, button in enumerate(self.spell_buttons):
                        spell = self.get_spell_by_button_index(current, index)
                        if spell and button.clicked(event):
                            self.perform_spell_cast(current, spell, self.selected_target)
                            return

                spells_only = self.spell_menu_open and self.spell_tier == "exalted"

                if self.battle_buttons[0].clicked(event, enabled=not spells_only):
                    self.reset_spell_state()
                    self.perform_player_action("attack")
                    return
                if self.battle_buttons[1].clicked(event, enabled=not spells_only):
                    self.reset_spell_state()
                    self.perform_player_action("cautious")
                    return
                if self.battle_buttons[2].clicked(event, enabled=not spells_only):
                    self.reset_spell_state()
                    self.perform_player_action("special")
                    return
                if self.battle_buttons[3].clicked(event, enabled=not spells_only):
                    self.reset_spell_state()
                    self.perform_player_action("loot")
                    return
                if self.battle_buttons[4].clicked(event, enabled=not spells_only or self.spell_menu_open):
                    self.toggle_spell_menu()
                    return

    def perform_player_action(self, action_name):
        player = self.players[self.current_turn]

        if action_name in {"attack", "cautious"} and (self.selected_target is None or self.selected_target.hp <= 0):
            self.append_log("Сначала выберите цель", category="warning")
            return
        if action_name == "special" and player.role not in ("Боевой маг", "Шаман") and (self.selected_target is None or self.selected_target.hp <= 0):
            self.append_log("Сначала выберите цель", category="warning")
            return

        if action_name == "attack":
            messages, hit_success = self.execute_attack(player, self.selected_target, True)
            self.append_log(
                f"{player.name} атакует {self.selected_target.name}",
                category="action",
                actor=player.name,
                verb="атакует",
                target=self.selected_target.name,
                target_hit=hit_success,
                indent=True,
            )
            self.hit_target = self.selected_target
            self.hit_timer = 10
            if messages:
                self.log.extend(messages)
        elif action_name == "cautious":
            messages, hit_success = self.execute_attack(player, self.selected_target, False, True)
            self.append_log(
                f"{player.name} осторожно атакует {self.selected_target.name}",
                category="action",
                actor=player.name,
                verb="осторожно атакует",
                target=self.selected_target.name,
                target_hit=hit_success,
                indent=True,
            )
            self.hit_target = self.selected_target
            self.hit_timer = 10
            if messages:
                self.log.extend(messages)
        elif action_name == "special":
            messages, hit_success, actual_target = self.perform_special_action(player, self.selected_target)
            shown_target = self.selected_target.name if self.selected_target and self.selected_target.hp > 0 else None
            self.append_log(
                f"{player.name} использует спец" + (f" против {shown_target}" if shown_target else ""),
                category="action",
                actor=player.name,
                verb="использует спец" + (" против" if shown_target else ""),
                target=shown_target,
                target_hit=hit_success,
                indent=True,
            )
            self.hit_target = actual_target
            self.hit_timer = 10 if actual_target else 0
            if messages:
                self.log.extend(messages)
        elif action_name == "loot":
            self.log.extend(self.perform_loot_action(player))

        self.normalize_health()
        if self.bonus_turn_player is player:
            self.advance_turn()
            return
        if self.try_grant_assassin_bonus_turn(player):
            return
        self.advance_turn()

    def perform_ai_turn(self, player):
        alive_targets = [x for x in self.players if x.hp > 0 and x != player]
        if not alive_targets:
            return

        target = min(alive_targets, key=lambda x: x.hp)

        # Шаман: если HP < 50% — предпочитает транс
        if player.role == "Шаман" and player.hp < player.max_hp * 0.5 and not player.trance_next and not player.trance_active:
            messages, hit_success, actual_target = self.perform_special_action(player, target)
            self.append_log(f"{player.name} уходит в транс", category="action", actor=player.name, verb="уходит в транс", indent=True)
            if messages:
                self.log.extend(messages)
            self.normalize_health()
            self.advance_turn()
            return

        # Боевой маг: иногда заряжает оружие
        if player.role == "Боевой маг" and player.weapon_enchanted_turns == 0 and random.randint(1, 100) <= 35:
            messages, hit_success, actual_target = self.perform_special_action(player, target)
            self.append_log(f"{player.name} заряжает оружие", category="action", actor=player.name, verb="заряжает оружие", indent=True)
            if messages:
                self.log.extend(messages)
            self.normalize_health()
            self.advance_turn()
            return

        roll = random.randint(1, 100)

        spell_blocked = self.is_spellcasting_blocked(player)
        special_blocked = self.has_stone_skin(player)

        if player.magic_path == "Путь земли" and not self.has_stone_skin(player) and player.hp < player.max_hp * 0.6:
            stone_skin_spell = next((s for s in self.get_spells_for_player(player, "normal") if s["id"] == "stone_skin"), None)
            if stone_skin_spell:
                self.spell_tier = "normal"
                self.spell_menu_open = True
                self.perform_spell_cast(player, stone_skin_spell, player)
                if self.state == self.BATTLE and self.current_turn < len(self.players) and self.players[self.current_turn] == player and self.spell_tier == "exalted" and player.hp > 0:
                    exalted_spells = self.get_spells_for_player(player, "exalted")
                    if exalted_spells:
                        exalted_spell = random.choice(exalted_spells)
                        chosen_target = target if exalted_spell.get("target") == "enemy" and target.hp > 0 else player
                        self.perform_spell_cast(player, exalted_spell, chosen_target)
                return

        if roll <= 20:
            self.log.extend(self.perform_loot_action(player))
        elif roll <= 40 and not spell_blocked:
            normal_spells = self.get_spells_for_player(player, "normal")
            if normal_spells:
                spell = random.choice(normal_spells)
                chosen_target = target if spell.get("target") == "enemy" else player
                self.spell_tier = "normal"
                self.spell_menu_open = True
                self.perform_spell_cast(player, spell, chosen_target)
                if self.state == self.BATTLE and self.current_turn < len(self.players) and self.players[self.current_turn] == player and self.spell_tier == "exalted" and player.hp > 0:
                    exalted_spells = self.get_spells_for_player(player, "exalted")
                    if exalted_spells:
                        exalted_spell = random.choice(exalted_spells)
                        chosen_target = target if exalted_spell.get("target") == "enemy" and target.hp > 0 else player
                        self.perform_spell_cast(player, exalted_spell, chosen_target)
                return
            self.log.extend(self.perform_loot_action(player))
        elif roll <= 45 and not special_blocked:
            messages, hit_success, actual_target = self.perform_special_action(player, target)
            self.append_log(
                f"{player.name} использует спец против {target.name}",
                category="action",
                actor=player.name,
                verb="использует спец против",
                target=target.name,
                target_hit=hit_success,
                indent=True,
            )
            self.hit_target = actual_target
            self.hit_timer = 10 if actual_target else 0
            if messages:
                self.log.extend(messages)
        elif roll <= 65:
            messages, hit_success = self.execute_attack(player, target, False, True)
            self.append_log(
                f"{player.name} осторожно атакует {target.name}",
                category="action",
                actor=player.name,
                verb="осторожно атакует",
                target=target.name,
                target_hit=hit_success,
                indent=True,
            )
            self.hit_target = target
            self.hit_timer = 10
            if messages:
                self.log.extend(messages)
        else:
            messages, hit_success = self.execute_attack(player, target, True)
            self.append_log(
                f"{player.name} атакует {target.name}",
                category="action",
                actor=player.name,
                verb="атакует",
                target=target.name,
                target_hit=hit_success,
                indent=True,
            )
            self.hit_target = target
            self.hit_timer = 10
            if messages:
                self.log.extend(messages)

        self.normalize_health()
        if self.bonus_turn_player is player:
            self.advance_turn()
            return
        if self.try_grant_assassin_bonus_turn(player):
            return
        self.advance_turn()

    def normalize_health(self):
        for player in self.players:
            player.hp = max(0, player.hp)

    def finish_battle(self, winner_name):
        self.winner_name = winner_name
        self.scores[winner_name] = self.scores.get(winner_name, 0) + 1
        self.champion = self.scores[winner_name] >= 3
        self.set_state(self.POST_BATTLE)

    def handle_post_battle_events(self, events):
        for event in events:
            if not self.champion and self.post_rematch_button.clicked(event):
                self.rematch_mode = True
                self.start_setup_flow(allow_back_to_names=False)
                return
            if self.post_restart_button.clicked(event):
                self.reset_to_menu()
                return
            if self.post_quit_button.clicked(event):
                self.running = False
                return

    def reset_to_menu(self):
        self.player_count = 0
        self.human_names = []
        self.player_builds = []
        self.scores = {}
        self.rematch_mode = False
        self.name_index = 0
        self.name_buffer = ""
        self.selected_class = None
        self.selected_group = None
        self.selected_magic_path = None
        self.selected_stats = []
        self.players = []
        self.log = []
        self.selected_target = None
        self.show_info_idx = None
        self.winner_name = ""
        self.champion = False
        self.reset_spell_state()
        self.set_state(self.MENU)

    def render_menu(self):
        self.screen.fill(DARK)
        panel = pygame.Rect(620, 120, 560, 650)
        pygame.draw.rect(self.screen, (55, 55, 55), panel, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, panel, 3, border_radius=20)

        title = self.title_font.render("RPG ARENA", True, WHITE)
        self.screen.blit(title, (705, 145))

        for button in self.menu_buttons:
            button.draw(self.screen, self.medium_font)
        self.menu_exit_button.draw(self.screen, self.medium_font)

    def render_name_input(self):
        self.screen.fill(DARK)

        panel = pygame.Rect(330, 110, 1140, 760)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=24)
        pygame.draw.rect(self.screen, WHITE, panel, 3, border_radius=24)

        title = self.big_font.render(f"Игрок {self.name_index + 1}: введи имя", True, WHITE)
        self.screen.blit(title, (560, 160))

        hint = self.small_font.render("Безопасный режим: ввод имени только экранной клавиатурой, чтобы окно не зависало.", True, (200, 200, 200))
        self.screen.blit(hint, (445, 245))

        pygame.draw.rect(self.screen, GRAY, (510, 300, 780, 90), border_radius=12)
        txt_surface = self.medium_font.render(self.name_buffer, True, WHITE)
        self.screen.blit(txt_surface, (535, 324))

        if pygame.time.get_ticks() % 1000 < 500 and len(self.name_buffer) < 12:
            cursor_x = 535 + txt_surface.get_width() + 4
            pygame.draw.line(self.screen, WHITE, (cursor_x, 322), (cursor_x, 368), 3)

        for _, button in self.name_key_buttons:
            button.draw(self.screen, self.small_font, enabled=len(self.name_buffer) < 12)

        self.name_space_button.draw(self.screen, self.font, enabled=len(self.name_buffer) < 12 and bool(self.name_buffer))
        self.name_delete_button.draw(self.screen, self.font, enabled=bool(self.name_buffer))
        self.name_clear_button.draw(self.screen, self.font)
        self.name_confirm_button.draw(self.screen, self.font, enabled=bool(self.name_buffer.strip()))
        self.name_back_button.draw(self.screen, self.font)

    def render_class_select(self):
        self.screen.fill(DARK)

        left_panel = pygame.Rect(70, 120, 400, 690)
        right_panel = pygame.Rect(520, 120, 1210, 690)
        pygame.draw.rect(self.screen, PANEL, left_panel, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, left_panel, 3, border_radius=20)

        player_name = self.human_names[self.setup_index]
        title = self.big_font.render(f"Выбор класса: {player_name}", True, WHITE)
        self.screen.blit(title, (610, 50))

        for button in self.class_buttons:
            button.draw(self.screen, self.font, active=(button.text == self.selected_group))

        if self.selected_group:
            subclasses = self.class_groups.get(self.selected_group, [])
            portrait_items = self.get_subclass_portrait_positions(self.selected_group)
            mouse = pygame.mouse.get_pos()

            # Рисуем кружки-аватарки подклассов
            for rect, sub_name in portrait_items:
                center = rect.center
                radius = rect.width // 2 + 7
                is_selected = (sub_name == self.selected_class)
                is_hovered = rect.collidepoint(mouse)

                # Фон
                if sub_name == "Шаман":
                    pygame.draw.circle(self.screen, (60, 46, 22), center, radius)
                    pygame.draw.circle(self.screen, (34, 34, 42), center, radius - 8)
                    pygame.draw.circle(self.screen, (56, 148, 136), (center[0] - 30, center[1] - 18), 26)
                    pygame.draw.circle(self.screen, (176, 102, 26), (center[0] + 34, center[1] + 24), 22)
                    pygame.draw.circle(self.screen, (34, 34, 42), center, radius - 22)
                else:
                    pygame.draw.circle(self.screen, (50, 50, 70), center, radius)

                # Портретная картинка
                sub_image = self.icons.get(sub_name)
                if sub_image:
                    scaled = self._make_circle_portrait(sub_image, rect.width)
                    self.screen.blit(scaled, (rect.x, rect.y))

                # Кольцо выбора
                if is_selected:
                    pygame.draw.circle(self.screen, GOLD, center, radius, 4)
                elif is_hovered:
                    pygame.draw.circle(self.screen, (200, 200, 210), center, radius, 3)
                else:
                    pygame.draw.circle(self.screen, (110, 110, 130), center, radius, 2)

                # Подпись под кружком
                label_color = GOLD if is_selected else (WHITE if is_hovered else GRAY)
                label = self.font.render(sub_name, True, label_color)
                self.screen.blit(label, (center[0] - label.get_width() // 2, rect.y + rect.height + 10))

                showcase = self.subclass_showcase_art.get(sub_name)
                if showcase:
                    art_rect = showcase.get_rect(midtop=(center[0], rect.y + rect.height + 48))
                    self.screen.blit(showcase, art_rect)

            # Описание выбранного подкласса
            display_class = self.selected_class
            if display_class:
                data = self.class_data[display_class]
                preview = self.get_class_preview_stats(display_class)
                class_color = self.get_class_color(display_class)

                y_text = 190
                class_title = self.class_name_font.render(display_class.upper(), True, class_color)
                self.screen.blit(class_title, (620, 125))

                lines = [
                    f"Сила: {preview['strength']} ({preview['damage']} урона)",
                    f"Выносливость: {preview['stamina']} ({preview['hp']} HP)",
                    f"Ловкость: {preview['agility']} ({preview['dodge']}% уклон)",
                    f"Удача: {preview['luck']} ({preview['crit']}% крит)",
                    f"Инициатива: {preview['initiative']} (ходит раньше)",
                    f"Интеллект: {preview['intellect']} ({preview['insight']}% прозрения)",
                    "",
                    "Пассивная способность:",
                    data["passive"],
                    "Активная способность:",
                    data["active"],
                    "",
                    data["desc"],
                ]
                for line in lines:
                    if not line:
                        y_text += 20
                        continue
                    wrapped = self.wrap_text(line, self.font, 640)
                    line_color = self.get_info_line_color(line, display_class)
                    for part in wrapped:
                        txt = self.font.render(part, True, line_color)
                        self.screen.blit(txt, (620, y_text))
                        y_text += 40
            elif len(subclasses) == 2:
                # Подкласс не выбран — подсказка
                group_color = self.get_class_color(subclasses[0])
                group_title = self.class_name_font.render(self.selected_group.upper(), True, group_color)
                self.screen.blit(group_title, (620, 125))
                hint = self.font.render("← Выбери подкласс, нажав на портрет", True, (170, 170, 190))
                self.screen.blit(hint, (620, 200))
                if self.selected_group == "Дикарь":
                    y_text = 270
                    group_lines = self.wrap_text(
                        "Люди диких племён живут по заветам предков. В бою они яростны и опасны: одни крушат врага грубой силой, другие шепчут духам и зовут древние обряды.",
                        self.font,
                        560,
                    )
                    for part in group_lines:
                        txt = self.font.render(part, True, (215, 215, 225))
                        self.screen.blit(txt, (620, y_text))
                        y_text += 40
                elif self.selected_group == "Боец":
                    y_text = 270
                    group_lines = self.wrap_text(
                        "Бойцы идут напролом и держат строй до конца. Одни побеждают сталью и щитом, другие сплавляют воинское мастерство с тайной боевой магией.",
                        self.font,
                        560,
                    )
                    for part in group_lines:
                        txt = self.font.render(part, True, (215, 215, 225))
                        self.screen.blit(txt, (620, y_text))
                        y_text += 40

        self.class_confirm_button.draw(self.screen, self.font, enabled=bool(self.selected_class))

    def render_magic_select(self):
        self.screen.fill(DARK)

        left_panel = pygame.Rect(70, 120, 420, 720)
        right_panel = pygame.Rect(540, 120, 1190, 720)
        pygame.draw.rect(self.screen, PANEL, left_panel, border_radius=20)
        pygame.draw.rect(self.screen, PANEL, right_panel, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, left_panel, 3, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, right_panel, 3, border_radius=20)

        player_name = self.human_names[self.setup_index]
        title = self.big_font.render(f"Мистический путь: {player_name}", True, WHITE)
        self.screen.blit(title, (520, 50))

        for button in self.magic_buttons:
            button.draw(self.screen, self.small_font, active=(button.text == self.selected_magic_path))

        if self.selected_magic_path:
            data = self.magic_data[self.selected_magic_path]
            y_text = 208
            path_color, normal_color, exalted_color = self.get_magic_tier_colors(self.selected_magic_path)
            path_title = self.class_name_font.render(self.selected_magic_path.upper(), True, path_color)
            self.screen.blit(path_title, (620, 145))

            lines = [
                data["desc"],
                "",
                "Обычные заклинания:",
            ]
            for spell in data["normal"]:
                lines.append(f"{spell['name']} — {spell['desc']}")
            lines.extend(["", "Возвышенные заклинания:"])
            for spell in data["exalted"]:
                lines.append(f"{spell['name']} — {spell['desc']}")

            for line in lines:
                if not line:
                    y_text += 18
                    continue
                color = WHITE
                if line == "Обычные заклинания:":
                    color = normal_color
                elif line == "Возвышенные заклинания:":
                    color = exalted_color
                wrapped = self.wrap_text(line, self.font, 980)
                for part in wrapped:
                    txt = self.font.render(part, True, color)
                    self.screen.blit(txt, (620, y_text))
                    y_text += 38

        self.magic_back_button.draw(self.screen, self.font)
        self.magic_confirm_button.draw(self.screen, self.font, enabled=bool(self.selected_magic_path))

    def render_stat_select(self):
        self.screen.fill(DARK)

        left_panel = pygame.Rect(70, 120, 420, 720)
        right_panel = pygame.Rect(540, 120, 1190, 720)
        desc_panel = pygame.Rect(570, 170, 560, 560)
        preview_panel = pygame.Rect(1170, 170, 520, 560)
        pygame.draw.rect(self.screen, PANEL, left_panel, border_radius=20)
        pygame.draw.rect(self.screen, PANEL, right_panel, border_radius=20)
        pygame.draw.rect(self.screen, (35, 35, 45), desc_panel, border_radius=18)
        pygame.draw.rect(self.screen, (35, 35, 45), preview_panel, border_radius=18)
        pygame.draw.rect(self.screen, WHITE, left_panel, 3, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, right_panel, 3, border_radius=20)
        pygame.draw.rect(self.screen, WHITE, desc_panel, 2, border_radius=18)
        pygame.draw.rect(self.screen, WHITE, preview_panel, 2, border_radius=18)

        player_name = self.human_names[self.setup_index]
        title = self.big_font.render(f"Какой ты воин, {player_name}?", True, WHITE)
        self.screen.blit(title, (560, 50))

        for button in self.stat_buttons:
            button.draw(self.screen, self.font, active=(button.text in self.selected_stats))

        desc_title = self.font.render("Суть характеристик", True, WHITE)
        self.screen.blit(desc_title, (610, 185))

        y_text = 245
        for name, desc in self.stat_data.items():
            if name == "Интеллектуальный":
                txt = self.font.render(f"{name} — шанс прозрения", True, WHITE)
                self.screen.blit(txt, (610, y_text))
                txt2 = self.font.render("                 и сила магии", True, WHITE)
                self.screen.blit(txt2, (610, y_text + 30))
                y_text += 64
            else:
                txt = self.font.render(f"{name} — {desc}", True, WHITE)
                self.screen.blit(txt, (610, y_text))
                y_text += 64

        if self.selected_class:
            preview = self.get_stat_selection_preview(self.selected_class, self.selected_stats)
            class_color = self.get_class_color(self.selected_class)
            preview_title = self.font.render("Текущие характеристики", True, WHITE)
            class_title = self.class_name_font.render(self.selected_class.upper(), True, class_color)
            self.screen.blit(preview_title, (1200, 185))
            self.screen.blit(class_title, (1200, 230))

            preview_lines = [
                f"Сила: {preview['strength']} ({preview['damage']} урона)",
                f"Выносливость: {preview['stamina']} ({preview['hp']} HP)",
                f"Ловкость: {preview['agility']} ({preview['dodge']}% уклон)",
                f"Удача: {preview['luck']} ({preview['crit']}% крит)",
                f"Инициатива: {preview['initiative']}",
                f"Интеллект: {preview['intellect']} ({preview['insight']}% прозрения)",
            ]
            preview_y = 300
            for line in preview_lines:
                txt = self.font.render(line, True, WHITE)
                self.screen.blit(txt, (1200, preview_y))
                preview_y += 62

        selected_text = self.medium_font.render(f"Выбрано: {len(self.selected_stats)}/2", True, WHITE)
        self.screen.blit(selected_text, (610, 650))

        self.stat_back_button.draw(self.screen, self.font)
        self.stat_confirm_button.draw(self.screen, self.font, enabled=len(self.selected_stats) == 2)

    def get_target_rects(self):
        rects = []
        for i, player in enumerate(self.players):
            x, y = 50, 50 + i * 120
            rects.append((player, pygame.Rect(x - 18, y, 238, 80)))
        return rects

    def draw_player_card(self, player, x, y, highlight=False, dead=False, idx=0):
        rect_x = x - 18
        player_rect = pygame.Rect(rect_x, y, 238, 80)
        if dead:
            pygame.draw.rect(self.screen, (80, 80, 80), player_rect)
        if highlight:
            pygame.draw.rect(self.screen, GREEN, player_rect, 4)

        name_font = pygame.font.SysFont("arial", 32)
        name = name_font.render(player.name, True, WHITE if not dead else (180, 180, 180))
        self.screen.blit(name, (x, y + 2))

        icon = self.icons.get(player.role)
        if icon:
            small_icon = pygame.transform.scale(icon, (80, 80))
            self.screen.blit(small_icon, (x + 220, y))

        info_x = x + 308
        info_y = y + 22
        pygame.draw.circle(self.screen, SKY, (info_x + 14, info_y + 14), 14)
        pygame.draw.circle(self.screen, WHITE, (info_x + 14, info_y + 14), 14, 2)
        i_font = pygame.font.SysFont("arial", 20, bold=True)
        i_txt = i_font.render("i", True, WHITE)
        i_rect = i_txt.get_rect(center=(info_x + 14, info_y + 13))
        self.screen.blit(i_txt, i_rect)
        self.info_rects[idx] = pygame.Rect(info_x, info_y, 28, 28)

        hp_bar_height = 12
        pygame.draw.rect(self.screen, RED, (x, y + 40, 200, hp_bar_height))
        hp_width = int(200 * (player.hp / player.max_hp)) if player.max_hp else 0
        if not dead:
            pygame.draw.rect(self.screen, GREEN, (x, y + 40, hp_width, hp_bar_height))

        hp_font = pygame.font.SysFont("arial", 22)
        hp_text = hp_font.render(f"{player.hp}/{player.max_hp}", True, WHITE if not dead else (180, 180, 180))
        self.screen.blit(hp_text, (x + 60, y + 54))

    def render_battle(self):
        self.screen.fill(DARK)

        arena_title = self.big_font.render(f"Арена: {self.arena_name}", True, WHITE)
        self.screen.blit(arena_title, (650, 20))

        self.info_rects = [None] * len(self.players)
        for i, player in enumerate(self.players):
            x, y = 50, 50 + i * 120
            current = player == self.players[self.current_turn] and player.hp > 0
            dead = player.hp <= 0
            self.draw_player_card(player, x, y, highlight=current, dead=dead, idx=i)

            if self.selected_target == player:
                pygame.draw.rect(self.screen, (255, 255, 0), pygame.Rect(x - 18, y, 238, 80), 4)
            if self.hit_timer > 0 and self.hit_target == player:
                pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(x - 18, y, 238, 80), 6)

        self.render_log()
        self.render_battle_descriptions()

        if not self.players[self.current_turn].is_ai:
            spells_only = self.spell_menu_open and self.spell_tier == "exalted"
            current_player = self.players[self.current_turn]
            special_locked = self.has_stone_skin(current_player)
            spell_locked = self.is_spellcasting_blocked(current_player)
            for index, button in enumerate(self.battle_buttons):
                enabled = not spells_only or index == 4
                if index == 2 and special_locked:
                    enabled = False
                if index == 4 and spell_locked and not self.spell_menu_open:
                    enabled = False
                button.draw(self.screen, self.medium_font, enabled=enabled, active=(index == 4 and self.spell_menu_open))

            if self.spell_menu_open:
                spell_title = "Возвышенная магия" if self.spell_tier == "exalted" else "Обычная магия"
                _, normal_color, exalted_color = self.get_magic_tier_colors(current_player.magic_path)
                title_surface = self.font.render(spell_title, True, exalted_color if self.spell_tier == "exalted" else normal_color)
                self.screen.blit(title_surface, (1375, 545))
                spells = self.get_spells_for_player(self.players[self.current_turn], self.spell_tier)
                hovered_spell = None
                for index, button in enumerate(self.spell_buttons):
                    if index < len(spells):
                        button.text = spells[index]["name"]
                        self.draw_spell_button(button, self.font, self.players[self.current_turn].magic_path, self.spell_tier)
                        if button.rect.collidepoint(pygame.mouse.get_pos()):
                            hovered_spell = spells[index]
                if hovered_spell:
                    wrapped = self.wrap_text(hovered_spell["desc"], self.small_font, 340)
                    box_h = min(len(wrapped), 5) * 22 + 18
                    box_rect = pygame.Rect(1338, 758, 360, box_h)
                    tooltip_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
                    tooltip_surf.fill((25, 25, 45, 210))
                    self.screen.blit(tooltip_surf, (box_rect.x, box_rect.y))
                    pygame.draw.rect(self.screen, (140, 140, 180), box_rect, 1, border_radius=6)
                    for row, part in enumerate(wrapped[:5]):
                        txt = self.small_font.render(part, True, WHITE)
                        self.screen.blit(txt, (box_rect.x + 10, box_rect.y + 9 + row * 22))
        else:
            thinking = self.medium_font.render("AI обдумывает ход...", True, WHITE)
            self.screen.blit(thinking, (120, 620))

        if self.show_info_idx is not None:
            self.close_popup_rect = self.draw_info_popup(self.players[self.show_info_idx])
        else:
            self.close_popup_rect = None

    def render_log(self):
        y_log = 30
        log_x = WIDTH - 600
        log_width = 550
        log_height = 520
        pygame.draw.rect(self.screen, (40, 40, 40), (log_x - 10, y_log - 10, log_width + 20, log_height), border_radius=12)

        max_log_width = log_width - 20
        for entry in self.log[-10:]:
            y_log = self.render_log_entry(entry, log_x, y_log, max_log_width)
            if y_log > 475:
                break

    def render_battle_descriptions(self):
        descriptions = [
            "Обычная атака по выбранной цели.",
            "Атака с меньшим уроном, но с шансом уклониться.",
            self.class_data.get(self.players[self.current_turn].role, {}).get("skill", "Спец-удар персонажа."),
            "Попытаться найти предмет.",
            "Открыть выбор заклинаний мистического пути.",
        ]
        desc_y = 710
        for i, text in enumerate(descriptions):
            x = [70, 320, 570, 820, 1070][i]
            words = text.split(" ")
            lines = []
            current_line = ""
            for word in words:
                test = (current_line + " " + word).strip()
                if self.small_font.size(test)[0] <= 220:
                    current_line = test
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            for j, line in enumerate(lines):
                txt = self.small_font.render(line, True, WHITE)
                self.screen.blit(txt, (x + 10, desc_y + j * 28))

    def draw_info_popup(self, player):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        popup_w, popup_h = 780, 760
        popup_x = (WIDTH - popup_w) // 2
        popup_y = (HEIGHT - popup_h) // 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)

        pygame.draw.rect(self.screen, PANEL, popup_rect, border_radius=18)
        pygame.draw.rect(self.screen, WHITE, popup_rect, 3, border_radius=18)

        title = self.medium_font.render(player.name, True, WHITE)
        self.screen.blit(title, (popup_x + 30, popup_y + 25))

        status_lines = []
        if player.disarmed_turns > 0:
            status_lines.append("Эффект: обезоружен — активка заблокирована, урон x0.5, пассивка выкл, лут -20%.")
        if player.arm_severed:
            status_lines.append("Эффект: отрублена рука — урон снижен вдвое до конца боя.")
        if player.leg_severed:
            status_lines.append("Эффект: отрублена нога — инициатива снижена до 1.")
        if player.bleeding > 0:
            status_lines.append(f"Эффект: кровотечение ещё {player.bleeding} ход(а), {player.bleed_damage} урона за тик.")
        if player.burning > 0:
            status_lines.append(f"Эффект: горение ещё {player.burning} ход(а), {player.burn_damage} урона за тик.")
        if player.stunned > 0:
            status_lines.append("Эффект: оглушён — пропустит следующий ход.")
        if player.frozen_turns > 0:
            status_lines.append("Эффект: заморожен — пропустит следующий ход.")
        if player.fire_wall_turns > 0:
            status_lines.append(f"Эффект: стена огня активна ещё {player.fire_wall_turns} ход(а).")
        if player.stone_skin_turns > 0:
            status_lines.append(f"Эффект: каменная кожа активна ещё {player.stone_skin_turns} ход(а) — входящий урон x0.5, доп. эффекты блокируются, магия и активка недоступны.")
        if player.tailwind_turns > 0:
            status_lines.append(f"Эффект: попутный ветер активен ещё {player.tailwind_turns} ход(а) — уклонение повышено на 30%.")
        if player.shadow_shroud_turns > 0:
            status_lines.append(f"Эффект: покров мрака активен ещё {player.shadow_shroud_turns} ход(а) — урон понижен на 40%, уклонение +25%.")
        if player.soul_curse_turns > 0:
            status_lines.append(f"Эффект: проклятие души ещё {player.soul_curse_turns} ход(а) — урон и интеллект снижены на 25%.")
        if player.unfathomable_next:
            status_lines.append("Эффект: шёпот извне — следующее заклинание усилено в 1.5 раза.")
        if player.weapon_enchanted_turns > 0:
            status_lines.append(f"Эффект: оружие заряжено магией ещё {player.weapon_enchanted_turns} ход(а).")
        if player.totem_active:
            status_lines.append("Эффект: тотем зверя активен — сила и ловкость x1.5 в этот ход.")
        if player.trance_active:
            status_lines.append("Эффект: транс шамана — интеллект x1.5 в этот ход.")
        if not status_lines:
            status_lines.append("Эффекты: активных эффектов сейчас нет.")

        lines = [
            f"Класс: {player.role or 'Не выбран'}",
            f"Мистический путь: {player.magic_path or 'Не выбран'}",
            f"HP: {player.hp}/{player.max_hp}",
            f"Сила: {player.strength} (наносит {player.damage} урона)",
            f"Выносливость: {player.stamina} ({player.max_hp} HP)",
            f"Ловкость: {player.agility} ({player.dodge}% уклон)",
            f"Удача: {player.luck} ({player.crit}% крит)",
            f"Инициатива: {player.initiative}",
            f"Интеллект: {player.intellect} ({self.get_insight_chance(player)}% прозрения)",
            "Инвентарь: пусто",
            "",
            "Пассивная способность:",
            self.class_data.get(player.role, {}).get("passive", "Нет"),
            "Активная способность:",
            self.class_data.get(player.role, {}).get("active", "Нет"),
            "",
            "Текущие эффекты:",
        ]

        y_text = popup_y + 95
        for line in lines + status_lines:
            if not line:
                y_text += 12
                continue
            wrapped = self.wrap_text(line, self.small_font if len(line) > 55 else self.font, popup_w - 60)
            line_color = self.get_info_line_color(line, player.role, player.magic_path)
            for part in wrapped:
                font = self.small_font if len(part) > 50 else self.font
                txt = font.render(part, True, line_color)
                self.screen.blit(txt, (popup_x + 30, y_text))
                y_text += 28

        close_rect = pygame.Rect(popup_x + popup_w - 150, popup_y + popup_h - 75, 120, 48)
        pygame.draw.rect(self.screen, RED, close_rect, border_radius=10)
        close_txt = self.font.render("Закрыть", True, WHITE)
        self.screen.blit(close_txt, (close_rect.x + 8, close_rect.y + 7))
        return close_rect

    def render_post_battle(self):
        self.screen.fill(DARK)

        overlay_rect = pygame.Rect(250, 110, WIDTH - 500, HEIGHT - 220)
        pygame.draw.rect(self.screen, PANEL, overlay_rect, border_radius=24)
        pygame.draw.rect(self.screen, GOLD, overlay_rect, 4, border_radius=24)

        if self.champion:
            crown_points = [
                (WIDTH // 2 - 120, 145),
                (WIDTH // 2 - 70, 85),
                (WIDTH // 2 - 20, 145),
                (WIDTH // 2 + 30, 75),
                (WIDTH // 2 + 80, 145),
                (WIDTH // 2 + 120, 120),
                (WIDTH // 2 + 120, 165),
                (WIDTH // 2 - 120, 165),
            ]
            pygame.draw.polygon(self.screen, GOLD, crown_points)
            pygame.draw.circle(self.screen, (255, 240, 120), (WIDTH // 2 - 70, 88), 8)
            pygame.draw.circle(self.screen, (255, 240, 120), (WIDTH // 2 + 30, 78), 8)
            pygame.draw.circle(self.screen, (255, 240, 120), (WIDTH // 2 + 118, 122), 8)
        winner_surface = self.hero_font.render(self.winner_name, True, GOLD)
        winner_rect = winner_surface.get_rect(center=(WIDTH // 2, 245 if self.champion else 220))
        self.screen.blit(winner_surface, winner_rect)

        winner_score = self.scores.get(self.winner_name, 0)
        if self.champion:
            message = self.medium_font.render("непревзойдённый чемпион", True, WHITE)
            score = self.font.render(f"Итог серии: {winner_score} победы", True, SILVER)
            hint = self.small_font.render("Реванш недоступен: чемпион уже определён", True, SILVER)
            self.screen.blit(message, message.get_rect(center=(WIDTH // 2, 345)))
            self.screen.blit(score, score.get_rect(center=(WIDTH // 2, 410)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 470)))
        else:
            line1 = self.medium_font.render("одержал доблестную победу", True, WHITE)
            line2 = self.medium_font.render("в суровой схватке", True, WHITE)
            score = self.font.render(f"Побед у {self.winner_name}: {winner_score}/3", True, SILVER)
            self.screen.blit(line1, line1.get_rect(center=(WIDTH // 2, 300)))
            self.screen.blit(line2, line2.get_rect(center=(WIDTH // 2, 360)))
            self.screen.blit(score, score.get_rect(center=(WIDTH // 2, 430)))

        board_title = self.font.render("Счёт серии", True, WHITE)
        self.screen.blit(board_title, (760, 500))

        score_panel = pygame.Rect(700, 535, 400, max(90, len(self.scores) * 44 + 30))
        pygame.draw.rect(self.screen, (35, 35, 45), score_panel, border_radius=16)
        pygame.draw.rect(self.screen, (120, 120, 145), score_panel, 2, border_radius=16)

        sorted_scores = sorted(self.scores.items(), key=lambda item: (-item[1], item[0]))
        for idx, (name, wins) in enumerate(sorted_scores):
            color = GOLD if idx == 0 else SILVER if idx == 1 else BRONZE if idx == 2 else WHITE
            line = self.font.render(f"{idx + 1}. {name}: {wins}", True, color)
            self.screen.blit(line, (735, 550 + idx * 40))

        self.post_rematch_button.draw(self.screen, self.font, enabled=not self.champion)
        self.post_restart_button.draw(self.screen, self.font)
        self.post_quit_button.draw(self.screen, self.font)


def run_game():
    ArenaGame().run()