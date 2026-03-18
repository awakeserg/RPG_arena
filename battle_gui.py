
import pygame
import sys
import os

pygame.init()



# Размеры окна боя
WIDTH, HEIGHT = 1800, 900

WHITE = (255,255,255)
GRAY = (120,120,120)
GREEN = (0,200,0)
RED = (200,0,0)
DARK = (30,30,30)


class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)

    def draw(self, screen, font):
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


def draw_player(screen, font, p, x, y, highlight=False, class_icons=None, dead=False, info_icon=None, info_rects=None, idx=None):
    # рамка вокруг игрока (чуть длиннее влево)
    rect_x = x - 18
    player_rect = pygame.Rect(rect_x, y, 238, 80)
    # фон для мёртвого игрока
    if dead:
        pygame.draw.rect(screen, (80,80,80), player_rect)
    # рамка
    if highlight:
        pygame.draw.rect(screen, GREEN, player_rect, 4)
    # имя (уменьшенный шрифт)
    name_font = pygame.font.SysFont("arial", 28)
    name = name_font.render(p.name, True, WHITE if not dead else (180,180,180))
    screen.blit(name, (x, y))

    # иконка класса
    if class_icons and p.role in class_icons:
        icon = class_icons[p.role]
        if icon:
            screen.blit(icon, (x + 220, y))
    # Кнопка инфо — рисуем кружок с 'i' справа от иконки класса
    if info_rects is not None and idx is not None:
        info_x = x + 260
        info_y = y + 20
        pygame.draw.circle(screen, (80,180,255), (info_x+16, info_y+16), 16)
        pygame.draw.circle(screen, WHITE, (info_x+16, info_y+16), 16, 2)
        i_font = pygame.font.SysFont("arial", 28, bold=True)
        i_txt = i_font.render("i", True, WHITE)
        screen.blit(i_txt, (info_x+10, info_y+2))
        rect = pygame.Rect(info_x, info_y, 32, 32)
        info_rects[idx] = rect
    # HP бар (уменьшенная высота)
    hp_bar_height = 14
    pygame.draw.rect(screen, RED, (x, y+30, 200, hp_bar_height))
    hp_width = int(200 * (p.hp / p.max_hp))
    if not dead:
        pygame.draw.rect(screen, GREEN, (x, y+30, hp_width, hp_bar_height))
    # числовое обозначение HP (уменьшенный шрифт, ниже полоски)
    hp_font = pygame.font.SysFont("arial", 22)
    hp_text = hp_font.render(f"{p.hp}/{p.max_hp}", True, WHITE if not dead else (180,180,180))
    screen.blit(hp_text, (x+60, y+30+hp_bar_height+2))




def battle_gui(players, attack, special, loot, use_item, ai_turn):
    # --- Загрузка иконок классов ---
    CLASS_ICON_PATHS = {
        "Воин": "assets/images/warrior.png",
        "Варвар": "assets/images/barbarian.png",
        "Ассасин": "assets/images/assassin.png",
        "Копейщик": "assets/images/spearman.png",
    }
    class_icons = {}
    for role, path in CLASS_ICON_PATHS.items():
        try:
            base_path = os.path.dirname(__file__)
            full_path = os.path.join(base_path, path)
            img = pygame.image.load(full_path)
            class_icons[role] = pygame.transform.scale(img, (60, 60))
        except Exception:
            class_icons[role] = None
    # Локальные объекты только для боя
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Бой")
    font = pygame.font.SysFont("arial", 44)
    big_font = pygame.font.SysFont("arial", 60)

    # --- Описания для кнопок ---
    ACTION_DESCRIPTIONS = {
        "Атака": "Обычная атака по выбранной цели.",
        "Осторожно": "Атака с меньшим уроном, но с шансом уклониться.",
        "Лут": "Попытаться найти предмет.",
        "Инвентарь": "Использовать предмет из инвентаря.",
    }

    # Спец-удары по классам
    SPECIAL_DESCRIPTIONS = {
        "Воин": "Удар щитом — 50% урона и шанс оглушить врага.",
        "Варвар": "Берсерк — двойной урон, но шанс получить ответный удар.",
        "Ассасин": "Кровотечение — наносит урон и вызывает кровотечение.",
        "Копейщик": "Пронзание — игнорирует броню, повышенный крит.",
        "": "Спец-удар персонажа.",
    }

    # Новые размеры и координаты для кнопок
    button_widths = [280, 280, 280, 280]
    button_xs = [100, 420, 740, 1060]
    button_y = 600
    button_height = 100
    buttons = [
        Button("Атака", button_xs[0], button_y, button_widths[0], button_height),
        Button("Осторожно", button_xs[1], button_y, button_widths[1], button_height),
        Button("Спец", button_xs[2], button_y, button_widths[2], button_height),
        Button("Лут", button_xs[3], button_y, button_widths[3], button_height),
    ]

    log = []
    current = 0
    selected_target = None
    hit_timer = 0

    # --- Загрузка иконки инфо ---
    try:
        base_path = os.path.dirname(__file__)
        info_icon_path = os.path.join(base_path, "assets/images/player_info_icon.png")
        info_icon = pygame.image.load(info_icon_path)
        info_icon = pygame.transform.scale(info_icon, (32, 32))
    except Exception:
        info_icon = None
    info_rects = [None] * len(players)
    show_info_idx = None
    while True:
        screen.fill(DARK)

        alive = [p for p in players if p.hp > 0]
        if len(alive) == 1:
            return alive[0].name

        p = players[current]

        # 👥 рисуем игроков
        target_rects = []
        for i, pl in enumerate(players):
            x, y = 50, 50 + i*120
            is_current = (pl == players[current]) and pl.hp > 0
            is_dead = pl.hp <= 0
            draw_player(screen, font, pl, x, y, highlight=is_current, class_icons=class_icons, dead=is_dead, info_icon=info_icon, info_rects=info_rects, idx=i)
            rect = pygame.Rect(x - 18, y, 220, 80)
            target_rects.append((pl, rect))
            # 🎯 подсветка выбранной цели (жёлтая, тоже чуть длиннее влево)
            if selected_target == pl:
                pygame.draw.rect(screen, (255,255,0), pygame.Rect(x - 18, y, 220, 80), 4)
            # 💥 анимация удара (красная)
            if hit_timer > 0 and pl == selected_target:
                pygame.draw.rect(screen, (255,0,0), pygame.Rect(x - 18, y, 220, 80), 6)

        if hit_timer > 0:
            hit_timer -= 1

        # 📜 лог — теперь в правом верхнем углу
        y_log = 30
        log_x = WIDTH - 600
        log_width = 550
        log_height = int(200 * 2.5)
        log_font = pygame.font.SysFont("arial", 28)
        # фон для читаемости
        pygame.draw.rect(screen, (40,40,40), (log_x-10, y_log-10, log_width+20, log_height), border_radius=12)
        # Перенос длинных строк лога
        max_log_width = log_width - 20
        log_lines = []
        for line in log[-6:]:
            words = line.split(' ')
            log_line = ''
            for word in words:
                test = (log_line + ' ' + word).strip()
                if log_font.size(test)[0] <= max_log_width:
                    log_line = test
                else:
                    if log_line:
                        log_lines.append(log_line)
                    log_line = word
            if log_line:
                log_lines.append(log_line)
        for l in log_lines:
            txt = log_font.render(l, True, WHITE)
            screen.blit(txt, (log_x, y_log))
            y_log += 44


        # --- ОПИСАНИЯ ПОД КАЖДОЙ КНОПКОЙ В СТОЛБИК ---
        desc_font = pygame.font.SysFont("arial", 32)
        desc_max_widths = button_widths
        desc_xs = button_xs
        desc_y = button_y + button_height + 10
        desc_texts = [
            ACTION_DESCRIPTIONS["Атака"],
            ACTION_DESCRIPTIONS["Осторожно"],
            SPECIAL_DESCRIPTIONS.get(p.role, SPECIAL_DESCRIPTIONS[""]),
            ACTION_DESCRIPTIONS["Лут"],
        ]

        for i, text in enumerate(desc_texts):
            lines = []
            words = text.split(' ')
            line = ''
            for word in words:
                test_line = (line + ' ' + word).strip()
                if desc_font.size(test_line)[0] <= desc_max_widths[i] - 20:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
            for j, l in enumerate(lines):
                txt = desc_font.render(l, True, WHITE)
                screen.blit(txt, (desc_xs[i] + 10, desc_y + j * 36))

        # 🤖 AI
        if p.is_ai:
            ai_turn(p, players)
            log.append(f"{p.name} сделал ход")
            current = (current + 1) % len(players)
            selected_target = None
            continue

        # 🔘 кнопки
        for b in buttons:
            b.draw(screen, font)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # 🎯 выбор цели
            if event.type == pygame.MOUSEBUTTONDOWN:
                for pl, rect in target_rects:
                    if rect.collidepoint(event.pos) and pl != p:
                        selected_target = pl

            # ⚔️ действия

            if selected_target:
                if buttons[0].clicked(event):
                    msgs = attack(p, selected_target, True)
                    log.append(f"{p.name} атакует {selected_target.name}")
                    if msgs:
                        log.extend(msgs)
                    hit_timer = 10

                elif buttons[1].clicked(event):
                    msgs = attack(p, selected_target, False, True)
                    log.append(f"{p.name} осторожно атакует")
                    if msgs:
                        log.extend(msgs)
                    hit_timer = 10

                elif buttons[2].clicked(event):
                    msgs = special(p, selected_target)
                    log.append(f"{p.name} использует спец")
                    if msgs:
                        log.extend(msgs)
                    hit_timer = 10

                else:
                    continue

                current = (current + 1) % len(players)
                selected_target = None

            if buttons[3].clicked(event):
                loot_result = loot(p)
                log.append(f"{p.name} ищет предмет")
                if isinstance(loot_result, str) and loot_result:
                    log.append(f"{p.name} {loot_result}")
                else:
                    log.append(f"{p.name} ничего не нашёл")
                # Явно убеждаемся, что current — это int
                current = (int(current) + 1) % len(players)

            # (Кнопка инвентарь и обработка больше не нужны)

        # Клик по иконке инфо
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if show_info_idx is not None:
                # Проверка на закрытие окна
                if close_rect.collidepoint(event.pos):
                    show_info_idx = None
            else:
                for idx, rect in enumerate(info_rects):
                    if rect and rect.collidepoint(event.pos):
                        show_info_idx = idx
                        break
        pygame.display.flip()