import random
from engine.items import use_item, loot
from engine.combat import attack

def ai_turn(p,players):

    alive=[x for x in players if x.hp>0 and x!=p]

    target=min(alive,key=lambda x:x.hp)

    if p.inventory and random.randint(1,100)<40:
        use_item(p)
        return

    if random.randint(1,100)<25:
        loot(p)
        return

    attack(p,target)