import random

good=["heal","dodge","luck","rejuvenation","beer"]
bad=["curse","bad_beer","knife"]


def loot(p):
    """
    Поиск предмета с шансом 50% + удача игрока (1% за 1 luck).
    Предмет сразу применяется, возвращается подробное описание для лога.
    """
    chance = 50 + p.luck
    roll = random.randint(1, 100)
    if roll > chance:
        return None

    # Список предметов и их эффектов/описаний
    items = [
        {
            "id": "heal_potion",
            "name": "Зелье здоровья",
            "effect": lambda p: setattr(p, "hp", min(p.max_hp, p.hp + 30)),
            "desc": "+30 HP",
            "log": f"получает 30 HP"
        },
        {
            "id": "poison_potion",
            "name": "Отравленное зелье",
            "effect": lambda p: setattr(p, "hp", max(0, p.hp - 20)),
            "desc": "-20 HP",
            "log": f"теряет 20 HP"
        },
        {
            "id": "rejuvenation_potion",
            "name": "Зелье омоложения",
            "effect": lambda p: setattr(p, "hp", p.max_hp),
            "desc": "восстанавливает всё HP",
            "log": f"полностью восстанавливает здоровье"
        },
        {
            "id": "luck_amulet",
            "name": "Амулет удачи",
            "effect": lambda p: setattr(p, "luck", p.luck + 10),
            "desc": "+10 к удаче навсегда",
            "log": f"навсегда увеличивает удачу на 10"
        },
        {
            "id": "cursed_amulet",
            "name": "Проклятый амулет",
            "effect": lambda p: setattr(p, "luck", p.luck - 7),
            "desc": "-7 к удаче навсегда",
            "log": f"навсегда уменьшает удачу на 7"
        },
        {
            "id": "beer",
            "name": "Баночка пива",
            "effect": None,  # Особый эффект обрабатывается в GUI
            "desc": "игрок случайно делает 2 действия, затем засыпает (стан)",
            "log": f"выпивает пиво: хаос и сон!"
        },
    ]
    item = random.choice(items)
    # Применяем эффект (кроме пива, оно обрабатывается отдельно)
    if item["id"] != "beer":
        item["effect"](p)
    # Возвращаем подробный лог
    return f"нашёл {item['name']} ({item['desc']}) и {item['log']}"


def use_item(p):

    if not p.inventory:
        print("пусто")
        return

    for i,it in enumerate(p.inventory):
        print(i+1,it)

    if p.is_ai:
        idx=0
    else:
        idx=int(input("> "))-1

    item=p.inventory.pop(idx)

    if item=="heal":
        p.hp+=20

    elif item=="dodge":
        p.temp_dodge+=20

    elif item=="luck":
        p.luck+=5
        p.crit+=10

    elif item=="rejuvenation":
        p.hp=p.max_hp

    elif item=="beer":
        print("🍺 хаос")

    elif item=="curse":
        p.hp-=20

    elif item=="bad_beer":
        p.stunned=1

    elif item=="knife":
        p.hp-=10