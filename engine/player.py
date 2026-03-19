class Player:

    def __init__(self,name,is_ai=False):

        self.name=name
        self.is_ai=is_ai

        self.role=""

        self.strength=10
        self.stamina=10
        self.agility=10
        self.luck=10
        self.initiative=10
        self.intellect=10

        self.inventory=[]

        self.hp=0
        self.max_hp=0

        self.damage=0
        self.dodge=0
        self.crit=0

        self.temp_dodge=0
        self.stunned=0
        self.disarmed_turns=0
        self.arm_severed=False
        self.leg_severed=False
        self.frozen_turns=0

        self.bleeding=0
        self.bleed_damage=0
        self.burning=0
        self.burn_damage=0
        self.fire_wall_turns=0
        self.fire_wall_fresh=False
        self.stone_skin_turns=0
        self.stone_skin_fresh=False
        self.tailwind_turns=0
        self.tailwind_fresh=False

        self.weapon_enchanted_turns=0

        self.totem_next=False
        self.totem_active=False
        self.totem_dmg_base=0
        self.totem_dodge_base=0

        self.trance_next=False
        self.trance_active=False
        self.trance_intel_base=0

        self.magic_path=""


    def calc(self):

        self.max_hp=self.stamina*8
        self.hp=self.max_hp

        self.damage=self.strength
        self.dodge=self.agility*2
        self.crit=self.luck*2


    def show(self):

        print("\n---",self.name,"---")
        print("Класс:",self.role)
        print("HP:",self.hp,"/",self.max_hp)
        print("Урон:",self.damage)
        print("Уклон:",self.dodge,"%")
        print("Крит:",self.crit,"%")
        print("Интеллект:",self.intellect)
        print("Инвентарь:",self.inventory)