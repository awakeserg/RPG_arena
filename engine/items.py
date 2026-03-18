import random

good=["heal","dodge","luck","rejuvenation","beer"]
bad=["curse","bad_beer","knife"]

def loot(p):

    print(p.name,"ищет предметы")

    if random.randint(1,100)>70:
        print("ничего")
        return

    if random.randint(1,100)<10:
        item=random.choice(bad)
    else:
        item=random.choice(good)

    p.inventory.append(item)

    print("найдено:",item)


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