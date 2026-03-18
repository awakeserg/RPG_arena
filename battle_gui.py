import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Бой")

font = pygame.font.SysFont("arial", 22)
big_font = pygame.font.SysFont("arial", 30)

WHITE = (255,255,255)
GRAY = (120,120,120)
GREEN = (0,200,0)
RED = (200,0,0)
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


def draw_player(p, x, y):

    # имя
    name = font.render(p.name, True, WHITE)
    screen.blit(name, (x, y))

    # HP бар
    pygame.draw.rect(screen, RED, (x, y+30, 200, 20))

    hp_width = int(200 * (p.hp / p.max_hp))
    pygame.draw.rect(screen, GREEN, (x, y+30, hp_width, 20))

    hp_text = font.render(f"{p.hp}/{p.max_hp}", True, WHITE)
    screen.blit(hp_text, (x+60, y+32))


def battle_gui(players, attack, special, loot, use_item, ai_turn):

    buttons = [
        Button("Атака", 50, 450, 140, 50),
        Button("Осторожно", 200, 450, 140, 50),
        Button("Спец", 350, 450, 140, 50),
        Button("Лут", 500, 450, 140, 50),
        Button("Инвентарь", 650, 450, 200, 50),
    ]

    log = []
    current = 0
    selected_target = None

    hit_timer = 0

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

            draw_player(pl, x, y)

            rect = pygame.Rect(x, y, 220, 80)
            target_rects.append((pl, rect))

            # 🎯 подсветка выбранной цели
            if selected_target == pl:
                pygame.draw.rect(screen, (255,255,0), rect, 3)

            # 💥 анимация удара
            if hit_timer > 0 and pl == selected_target:
                pygame.draw.rect(screen, (255,0,0), rect, 4)

        if hit_timer > 0:
            hit_timer -= 1

        # 📜 лог
        y_log = 300
        for line in log[-6:]:
            txt = font.render(line, True, WHITE)
            screen.blit(txt, (50, y_log))
            y_log += 25

        # 🤖 AI
        if p.is_ai:
            ai_turn(p, players)
            log.append(f"{p.name} сделал ход")
            current = (current + 1) % len(players)
            selected_target = None
            continue

        # 🔘 кнопки
        for b in buttons:
            b.draw()

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
                loot(p)
                log.append(f"{p.name} ищет предмет")
                current = (current + 1) % len(players)

            if buttons[4].clicked(event):
                use_item(p)
                log.append(f"{p.name} использует предмет")
                current = (current + 1) % len(players)

        pygame.display.flip()