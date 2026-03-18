
# --- Импортируем необходимые модули ---
from main_menu import main_menu
from engine.player import Player
from name_input import name_input
from engine.systems import build_player, choose_class, choose_arena
from stat_select import stat_select
from engine.combat import attack, special
from engine.items import loot, use_item
from engine.ai import ai_turn
from battle_gui import battle_gui

def apply_stat_bonuses(player, stats):
    """Применяет выбранные бонусы к игроку."""
    for s in stats:
        if s == "Сильный":
            player.strength += 10
        elif s == "Выносливый":
            player.stamina += 10
        elif s == "Ловкий":
            player.agility += 10
        elif s == "Удачливый":
            player.luck += 10
        elif s == "Инициативный":
            player.initiative += 10

def apply_class_bonuses(player, cls):
    """Применяет бонусы выбранного класса к игроку."""
    if cls == "Воин":
        player.damage += 5
        player.dodge += 20
    elif cls == "Варвар":
        player.damage += 15
    elif cls == "Копейщик":
        player.initiative += 10
        player.crit += 20
    # Ассасин — без дополнительных бонусов

def create_player(index):
    """Создаёт и настраивает игрока по номеру."""
    name = name_input(index + 1)
    p = Player(name)
    from class_select import class_select
    cls = class_select(p.name)
    p.role = cls
    stats = stat_select(p.name)
    apply_stat_bonuses(p, stats)
    p.calc()  # Пересчёт характеристик после бонусов
    apply_class_bonuses(p, cls)
    return p

def create_ai_player():
    """Создаёт и настраивает AI-игрока."""
    bot = Player("AI", True)
    build_player(bot)
    bot.calc()
    choose_class(bot)
    return bot

def main():
    print("⚔ RPG ARENA DELUXE ⚔")

    players = []
    count = main_menu()

    # --- Создание игроков ---
    for i in range(count):
        players.append(create_player(i))

    # --- Добавление AI, если 1 игрок ---
    if count == 1:
        players.append(create_ai_player())

    # --- Выбор арены ---
    choose_arena(players)

    # --- Сортировка по инициативе, удаче, ловкости ---
    players.sort(key=lambda x: (x.initiative, x.luck, x.agility), reverse=True)

    # --- Запуск боя ---
    winner = battle_gui(players, attack, special, loot, use_item, ai_turn)
    print("Победил:", winner)

if __name__ == "__main__":
    main()
