import random

def attack(a,d,strong=False,cautious=False):

    messages = []
    dodge = d.dodge + d.temp_dodge
    crit = a.crit

    if strong:
        crit += 10

    if cautious:
        a.temp_dodge += 10

    if random.randint(1, 100) <= dodge:
        if random.randint(1, 100) < 15:
            messages.append("⚡ Парирование!")
            a.hp -= a.damage // 2
        else:
            messages.append(f"{d.name} уклонился")
        return messages

    dmg = a.damage
    crit_hit = False
    if random.randint(1, 100) <= crit:
        dmg *= 2
        crit_hit = True
        messages.append("💥 крит")

    if d.hp < 15 and random.randint(1, 100) < 20:
        messages.append("💀 ФАТАЛИТИ!")
        d.hp = 0
        return messages

    if random.randint(1, 100) < 10:
        messages.append("🩸 смертельная рана")
        d.bleeding = 4
        d.bleed_damage = dmg // 2

    d.hp -= dmg
    messages.append(f"{a.name} нанёс {dmg}")
    return messages


def special(a,d):

    messages = []
    if a.role == "Воин":
        dmg = a.damage // 2
        d.hp -= dmg
        messages.append(f"{a.name} использует спец и наносит {dmg}")
        if random.randint(1, 100) < 30:
            d.stunned = 1
            messages.append("оглушение")

    elif a.role == "Варвар":
        dmg = a.damage * 2
        if random.randint(1, 100) < 30:
            a.hp -= dmg
            messages.append("варвар ударил себя")
        else:
            d.hp -= dmg
            messages.append(f"{a.name} использует спец и наносит {dmg}")

    elif a.role == "Ассасин":
        attack_msgs = attack(a, d)
        messages.extend(attack_msgs)
        if random.randint(1, 100) < 60:
            bleed = int(a.damage * 0.4)
            d.bleeding = 3
            d.bleed_damage = bleed
            messages.append("кровотечение")

    elif a.role == "Копейщик":
        dmg = a.damage // 2
        d.hp -= dmg
        messages.append(f"{a.name} использует спец и наносит {dmg}")
        if random.randint(1, 100) < 30:
            d.stunned = 1
            messages.append("оглушение")

    return messages