# weapon.py
from constants import WeaponType

class Weapon:
    def __init__(self, name, weapon_type, might, hit, crit, weight, range_min, range_max, durability):
        self.name = name
        self.weapon_type = weapon_type
        self.might = might
        self.hit = hit
        self.crit = crit
        self.weight = weight
        self.range_min = range_min
        self.range_max = range_max
        self.durability = durability
        self.max_durability = durability