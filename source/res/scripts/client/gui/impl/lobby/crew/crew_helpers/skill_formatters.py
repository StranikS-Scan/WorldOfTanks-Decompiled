# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/skill_formatters.py
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from items.tankmen import MAX_SKILL_LEVEL

class SkillLvlFormatter(object):
    NDIG = 1
    MIN_FRACTION = 0.01
    MAX_FRACTION = MAX_SKILL_LEVEL - MIN_FRACTION
    intSkillLvl = property(lambda self: int(self.__skillLvl), lambda self, value: None)
    residualXp = property(lambda self: self.__residual, lambda self, value: None)
    lvlCostXp = property(lambda self: self.__lvlCost, lambda self, value: None)
    isSkillLvl = property(lambda self: self.__skillLvl != CrewConstants.DONT_SHOW_LEVEL, lambda self, value: None)
    realSkillLvl = property(lambda self: self.makeRealLvl(), lambda self, value: None)
    formattedSkillLvl = property(lambda self: self.formatLvl(), lambda self, value: None)
    __slots__ = ('__skillLvl', '__residual', '__lvlCost')

    def __init__(self, skillLvl=CrewConstants.DONT_SHOW_LEVEL, residual=0, lvlCost=0):
        self.__skillLvl = skillLvl
        self.__residual = residual
        self.__lvlCost = lvlCost

    def __str__(self):
        return 'SkillLvlFormatter(skillLvl={}, residual={}, lvlCost={})'.format(self.__skillLvl, self.__residual, self.__lvlCost)

    def __add__(self, other):
        if self.isSkillLvl:
            if isinstance(other, SkillLvlFormatter):
                if other.isSkillLvl:
                    residual = other.lvlCostXp * self.residualXp + self.lvlCostXp * other.residualXp
                    return SkillLvlFormatter(self.intSkillLvl + other.intSkillLvl, residual, self.lvlCostXp * other.lvlCostXp)
            if isinstance(other, int):
                return SkillLvlFormatter(self.intSkillLvl + other)
        return self

    def __sub__(self, other):
        if self.isSkillLvl:
            if isinstance(other, SkillLvlFormatter):
                if other.isSkillLvl:
                    residual = other.lvlCostXp * self.residualXp - self.lvlCostXp * other.residualXp
                    return SkillLvlFormatter(self.intSkillLvl - other.intSkillLvl, residual, self.lvlCostXp * other.lvlCostXp)
            if isinstance(other, int):
                return SkillLvlFormatter(self.intSkillLvl - other)
        return self

    def __lt__(self, other):
        return self._cmp(other) < 0

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def __le__(self, other):
        return self._cmp(other) <= 0

    def __ge__(self, other):
        return self._cmp(other) >= 0

    def __ne__(self, other):
        return self._cmp(other) != 0

    def __hash__(self):
        raise TypeError('hash not implemented')

    def _cmp(self, other):
        return cmp(self.intSkillLvl, other) if isinstance(other, int) else cmp(self.makeRealLvl(), other.makeRealLvl())

    def makeRealLvl(self):
        if not self.isSkillLvl:
            return self.intSkillLvl
        realLvl = float(self.__skillLvl)
        if self.__lvlCost and self.__residual:
            realLvl += float(self.__residual) / self.__lvlCost
        return realLvl

    def formatLvl(self):
        if not self.isSkillLvl:
            return self.intSkillLvl
        realLvl = self.makeRealLvl()
        if self.MIN_FRACTION <= realLvl <= self.MAX_FRACTION:
            return self.roundLvl(realLvl, self.NDIG)
        if realLvl < self.MIN_FRACTION:
            return realLvl
        return self.MAX_FRACTION if realLvl < MAX_SKILL_LEVEL else MAX_SKILL_LEVEL

    @staticmethod
    def roundLvl(realNumber, ndig):
        multiplier = 10 ** ndig
        return int(realNumber * multiplier) / float(multiplier)
