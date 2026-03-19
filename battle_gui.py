
import pygame
import sys
import os
from ui import WIDTH, HEIGHT, get_screen

pygame.init()

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



def draw_player_info_popup(screen, player):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    popup_w, popup_h = 520, 420
    popup_x = (WIDTH - popup_w) // 2
    popup_y = (HEIGHT - popup_h) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)

    pygame.draw.rect(screen, (45,45,55), popup_rect, border_radius=18)
    pygame.draw.rect(screen, WHITE, popup_rect, 3, border_radius=18)

    title_font = pygame.font.SysFont("arial", 42, bold=True)
    text_font = pygame.font.SysFont("arial", 30)

    title = title_font.render(player.name, True, WHITE)
    screen.blit(title, (popup_x + 30, popup_y + 25))

    lines = [
        f"Класс: {player.role or 'Не выбран'}",
        f"HP: {player.hp}/{player.max_hp}",
        f"Сила: {player.strength}",
        f"Выносливость: {player.stamina}",
        f"Ловкость: {player.agility}",
        f"Удача: {player.luck}",
        f"Инициатива: {player.initiative}",
        f"Урон: {player.damage}",
        f"Уклон: {player.dodge}%",
        f"Крит: {player.crit}%",
        "Инвентарь: " + (", ".join(map(str, player.inventory)) if player.inventory else "пусто"),
    ]

    for i, line in enumerate(lines):
        txt = text_font.render(line, True, WHITE)
        screen.blit(txt, (popup_x + 30, popup_y + 95 + i * 28))

    close_rect = pygame.Rect(popup_x + popup_w - 140, popup_y + popup_h - 70, 110, 45)
    pygame.draw.rect(screen, RED, close_rect, border_radius=10)
    close_txt = text_font.render("Закрыть", True, WHITE)
    screen.blit(close_txt, (close_rect.x + 10, close_rect.y + 7))

    return close_rect


def show_post_battle_screen(winner_name, scores, champion=False):
    screen = get_screen("Итоги боя")

    title_font = pygame.font.SysFont("arial", 88, bold=True)
    text_font = pygame.font.SysFont("arial", 44)
    small_font = pygame.font.SysFont("arial", 32)
    hint_font = pygame.font.SysFont("arial", 28)

    rematch_btn = Button("Реванш", 420, 720, 260, 75)
    restart_btn = Button("Начать заново", 770, 720, 320, 75)
    quit_btn = Button("Закрыть игру", 1180, 720, 300, 75)

    winner_score = scores.get(winner_name, 0)

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

    while True:
        screen.fill(DARK)

        overlay_rect = pygame.Rect(250, 110, WIDTH - 500, HEIGHT - 220)
        pygame.draw.rect(screen, (45, 45, 55), overlay_rect, border_radius=24)
        pygame.draw.rect(screen, (212, 175, 55), overlay_rect, 4, border_radius=24)

        if champion:
            pygame.draw.polygon(screen, (255, 215, 0), crown_points)
            pygame.draw.circle(screen, (255, 240, 120), (WIDTH // 2 - 70, 88), 8)
            pygame.draw.circle(screen, (255, 240, 120), (WIDTH // 2 + 30, 78), 8)
            pygame.draw.circle(screen, (255, 240, 120), (WIDTH // 2 + 118, 122), 8)

        winner_surface = title_font.render(winner_name, True, (255, 215, 0))
        winner_rect = winner_surface.get_rect(center=(WIDTH // 2, 245 if champion else 220))
        screen.blit(winner_surface, winner_rect)

        if champion:
            message_surface = text_font.render("непревзойдённый чемпион", True, WHITE)
            champion_score = small_font.render(f"Итог серии: {winner_score} победы", True, (220, 220, 220))
            hint_surface = hint_font.render("Реванш недоступен: чемпион уже определён", True, (210, 210, 210))
            message_rect = message_surface.get_rect(center=(WIDTH // 2, 345))
            score_rect = champion_score.get_rect(center=(WIDTH // 2, 410))
            hint_rect = hint_surface.get_rect(center=(WIDTH // 2, 470))
            screen.blit(message_surface, message_rect)
            screen.blit(champion_score, score_rect)
            screen.blit(hint_surface, hint_rect)
        else:
            message_surface = text_font.render("одержал доблестную победу", True, WHITE)
            message_surface_2 = text_font.render("в суровой схватке", True, WHITE)
            score_surface = small_font.render(f"Побед у {winner_name}: {winner_score}/3", True, (220, 220, 220))
            message_rect = message_surface.get_rect(center=(WIDTH // 2, 300))
            message_rect_2 = message_surface_2.get_rect(center=(WIDTH // 2, 360))
            score_rect = score_surface.get_rect(center=(WIDTH // 2, 430))
            screen.blit(message_surface, message_rect)
            screen.blit(message_surface_2, message_rect_2)
            screen.blit(score_surface, score_rect)

        board_title = small_font.render("Счёт серии", True, WHITE)
        screen.blit(board_title, (760, 500))

        score_panel = pygame.Rect(700, 535, 400, max(90, len(scores) * 44 + 30))
        pygame.draw.rect(screen, (35, 35, 45), score_panel, border_radius=16)
        pygame.draw.rect(screen, (120, 120, 145), score_panel, 2, border_radius=16)

        sorted_scores = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        for idx, (name, wins) in enumerate(sorted_scores):
            if idx == 0:
                color = (255, 215, 0)
            elif idx == 1:
                color = (210, 210, 220)
            elif idx == 2:
                color = (205, 140, 90)
            else:
                color = WHITE

            score_line = small_font.render(f"{idx + 1}. {name}: {wins}", True, color)
            screen.blit(score_line, (735, 550 + idx * 40))

        if champion:
            pygame.draw.rect(screen, (85, 85, 85), rematch_btn.rect, border_radius=10)
            rematch_text = small_font.render("Реванш", True, (170, 170, 170))
            screen.blit(rematch_text, (rematch_btn.rect.x + 58, rematch_btn.rect.y + 20))
        else:
            rematch_btn.draw(screen, small_font)

        restart_btn.draw(screen, small_font)
        quit_btn.draw(screen, small_font)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if not champion and rematch_btn.clicked(event):
                return "rematch"

            if restart_btn.clicked(event):
                return "restart"

            if quit_btn.clicked(event):
                return "quit"




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
    screen = get_screen("Бой")
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

        close_rect = None
        if show_info_idx is not None:
            close_rect = draw_player_info_popup(screen, players[show_info_idx])

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_info_idx is not None:
                    if close_rect and close_rect.collidepoint(event.pos):
                        show_info_idx = None
                    continue

                for idx, rect in enumerate(info_rects):
                    if rect and rect.collidepoint(event.pos):
                        show_info_idx = idx
                        break

                if show_info_idx is not None:
                    continue

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
        pygame.display.flip()