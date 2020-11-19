class Gem:
    def __init__(self, strength=0, agility=0, intelligence=0):
        self.__strength__ = strength
        self.__agility__ = agility
        self.__intelligence__ = intelligence

    def strength(self):
        return self.__strength__

    def agility(self):
        return self.__agility__

    def intelligence(self):
        return self.__intelligence__

    def copy(self):
        return Gem(self.strength(), self.agility(),
                   self.intelligence())

    def __add__(self, other):
        return Gem((self.strength() + other.strength()) // 2,
                   (self.agility() + other.agility()) // 2,
                   (self.intelligence() + other.intelligence()) // 2)

    def __iadd__(self, other):
        self.__agility__ = (other.agility() + self.agility()) // 2
        self.__intelligence__ = (other.intelligence() + self.intelligence()) // 2
        self.__strength__ = (other.strength() + self.strength()) // 2
        return self

    def __round__(self, number=2):
        res = sum((self.strength(), self.agility(), self.intelligence()))
        self.__agility__ = res // number
        self.__intelligence__ = res // number
        self.__strength__ = res // number
        return self

    def __str__(self):
        return 'Gem(strength: {}, agility: {}, intelligence: {})'.format(
            self.strength(), self.agility(), self.intelligence())


class Thing:
    def __init__(self, name, armor=0, strength=0, agility=0, intelligence=0):
        self.__things_name__ = name
        self.__armor__ = armor
        self.__list_gem__ = []
        self.__strength__ = strength
        self.__agility__ = agility
        self.__intelligence__ = intelligence

    def armor(self):
        return self.__armor__

    def strength(self):
        return self.__strength__

    def agility(self):
        return self.__agility__

    def intelligence(self):
        return self.__intelligence__

    def push(self, gem):
        if len(self.__list_gem__) >= 3:
            self.__list_gem__[0] = gem.copy()
        else:
            self.__list_gem__.append(gem.copy())

    def pop(self, count):
        self.__list_gem__ = list(self.__list_gem__[-count:])

    def __lshift__(self, other):
        self.push(other)

    def __next__(self):
        self.__list_gem__ = self.__list_gem__[:-1]

    def __str__(self):
        return self.__things_name__ + '(\nArmor: ' + str(self.armor()) + ',\nstrength: ' + str(
            self.strength()) + ',\nagilit\
y: ' + str(self.agility()) + ',\nintelligence: ' + str(self.intelligence()) + '\n)'
