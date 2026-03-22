import random

def attack(a,d,strong=False,cautious=False):

    messages = []
    dodge = min(80, max(0, d.dodge + d.temp_dodge))
    crit = min(80, max(0, a.crit))

    if strong:
        crit = min(80, crit + 10)

    if cautious:
        a.temp_dodge += 10

    if random.randint(1, 100) <= dodge:
        if random.randint(1, 100) < 15:
            messages.append("⚡ Парирование!")
            parry_damage = a.damage // 2
            if getattr(a, "lycan_form", "") == "bear" and random.randint(1, 100) <= 25:
                parry_damage = 0
            if getattr(a, "stone_skin_turns", 0) > 0:
                parry_damage = max(1, parry_damage // 2)
            elif getattr(a, "shadow_shroud_turns", 0) > 0:
                parry_damage = max(1, int(parry_damage * 0.6))
            a.hp -= parry_damage
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

    if getattr(d, "lycan_form", "") == "bear" and random.randint(1, 100) <= 25:
        messages.append("🐻 урон проигнорирован")
        return messages

    if random.randint(1, 100) < 10 and getattr(d, "stone_skin_turns", 0) <= 0:
        messages.append("🩸 смертельная рана")
        d.bleeding = 4
        d.bleed_damage = dmg // 2

    actual_dmg = dmg
    if getattr(d, "stone_skin_turns", 0) > 0:
        actual_dmg = max(1, dmg // 2)
    elif getattr(d, "shadow_shroud_turns", 0) > 0:
        actual_dmg = max(1, int(dmg * 0.6))
    d.hp -= actual_dmg
    messages.append(f"{a.name} нанёс {actual_dmg}")
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

    elif a.role == "Эльф":
        dmg = a.damage // 2
        d.hp -= dmg
        messages.append(f"{a.name} использует спец и наносит {dmg}")
        if random.randint(1, 100) < 30:
            d.stunned = 1
            messages.append("оглушение")

    elif a.role == "Орк":
        dmg = a.damage * 2
        if random.randint(1, 100) < 30:
            a.hp -= dmg
            messages.append("орк ударил себя")
        else:
            d.hp -= dmg
            messages.append(f"{a.name} использует спец и наносит {dmg}")

    return messages