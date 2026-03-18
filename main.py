from main_menu import main_menu
from engine.player import Player
from name_input import name_input
from engine.systems import build_player, choose_class, choose_arena
from stat_select import stat_select
from engine.combat import attack, special
from engine.items import loot, use_item
from engine.ai import ai_turn
from battle_gui import battle_gui

print("⚔ RPG ARENA DELUXE ⚔")

players=[]

count = main_menu()
for i in range(count):

    name = name_input(i+1)

    p = Player(name)

    from class_select import class_select
    cls = class_select(p.name)
    p.role = cls

    # 👉 ВОТ ТУТ НОВЫЙ ЭКРАН
    stats = stat_select(p.name)

    # 👉 применяем выбранные бонусы
    for s in stats:
        if s == "Сильный":
            p.strength += 10
        elif s == "Выносливый":
            p.stamina += 10
        elif s == "Ловкий":
            p.agility += 10
        elif s == "Удачливый":
            p.luck += 10
        elif s == "Инициативный":
            p.initiative += 10

    # 👉 только теперь считаем характеристики
    p.calc()

    # применяем бонусы (как раньше)
    if cls == "Воин":
        p.damage += 5
        p.dodge += 20

    elif cls == "Варвар":
        p.damage += 15

    elif cls == "Ассасин":
        pass

    elif cls == "Копейщик":
        p.initiative += 10
        p.crit += 20

    players.append(p)

if count==1:

    bot=Player("AI",True)

    build_player(bot)
    bot.calc()
    choose_class(bot)

    players.append(bot)

choose_arena(players)

players.sort(key=lambda x:x.initiative,reverse=True)

round_num=1

winner = battle_gui(players, attack, special, loot, use_item, ai_turn)
print("Победил:", winner)
