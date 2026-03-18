import random

def build_player(p):

    points=25

    while points>0:

        print("\nОчков осталось:",points)

        print("""
1 Сила (+5 урон)
2 Выносливость (+25 HP)
3 Ловкость (+10% уклон)
4 Удача (+10% крит)
5 Инициатива (+5)
""")

        if p.is_ai:
            c=random.randint(1,5)
        else:
            c=int(input("> "))

        if c==1:
            p.strength+=5

        elif c==2:
            p.stamina+=5

        elif c==3:
            p.agility+=5

        elif c==4:
            p.luck+=5

        elif c==5:
            p.initiative+=5

        points-=5


def choose_class(p):

    if p.is_ai:
        c=random.randint(1,4)

    else:
        print("""
1 Воин
2 Варвар
3 Ассасин
4 Копейщик
""")
        c=int(input("> "))

    if c==1:
        p.role="Воин"
        p.damage+=5
        p.dodge+=20

    elif c==2:
        p.role="Варвар"
        p.damage+=15

    elif c==3:
        p.role="Ассасин"

    elif c==4:
        p.role="Копейщик"
        p.initiative+=10
        p.crit+=20


def choose_arena(players):

    arenas=[
    ("Колизей", "hp"),
    ("Лес","dodge"),
    ("Вулкан","damage"),
    ("Ледяная пустошь","crit")
    ]

    arena=random.choice(arenas)

    print("\n🏟 Арена:",arena[0])

    for p in players:

        if arena[1]=="hp":
            p.max_hp+=10
            p.hp+=10

        elif arena[1]=="dodge":
            p.dodge+=10

        elif arena[1]=="damage":
            p.damage+=5

        elif arena[1]=="crit":
            p.crit+=10