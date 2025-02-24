# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/stepper_calculator.py
from math import ceil
from helpers import dependency
from items.tankmen import MAX_SKILL_LEVEL
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getSkillsLevelsForXp
from skeletons.gui.shared import IItemsCache

class FreeXpStepperCalculator(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, exchangeRate):
        self._currentTankman = None
        self._exchangeRate = exchangeRate
        self._currentSkillsCount = 0
        self._currentSkillLevel = 0
        self._possibleSkillsCount = 0
        self._possibleSkillLevel = 0
        self._aquiringPersonalXpAmount = 0
        return

    def setCurrentTankman(self, tankman):
        self._currentTankman = tankman
        self.setInitialPossibleValues()

    def setInitialPossibleValues(self):
        if self._currentTankman is None:
            return
        else:
            skillsCount, lastSkillLevel = self._currentTankman.descriptor.getTotalSkillsProgress(withFree=False)
            self._currentSkillsCount = self._possibleSkillsCount = skillsCount
            self._currentSkillLevel = self._possibleSkillLevel = lastSkillLevel
            self._aquiringPersonalXpAmount = 0
            return

    def setManualInputPossibleValues(self, possibleCount, possibleLevel):
        if possibleCount > 0 and possibleLevel >= 0 and (possibleCount != self._possibleSkillsCount or possibleLevel != self._possibleSkillLevel):
            self._possibleSkillsCount = possibleCount
            self._possibleSkillLevel = possibleLevel

    def setAquiringPersonalXp(self, value):
        if self._currentTankman is None:
            return
        else:
            self._aquiringPersonalXpAmount = value
            skillsCount, lastSkillLevel = self._currentTankman.descriptor.getTotalSkillsProgress(withFree=False, extraXP=value)
            self._possibleSkillsCount = skillsCount
            self._possibleSkillLevel = lastSkillLevel
            return

    def getLevelUpXpCost(self):
        if not self._currentTankman:
            return 0
        if self._possibleSkillLevel == MAX_SKILL_LEVEL - 1:
            self._possibleSkillsCount += 1
            self._possibleSkillLevel = 0
        else:
            self._possibleSkillLevel += 1
        return self._countResultAndConvertToFreeXp()

    def getLevelDownXpCost(self):
        if not self._currentTankman:
            return 0
        if self._possibleSkillsCount > self._currentSkillsCount:
            if self._possibleSkillLevel == 0:
                self._possibleSkillsCount -= 1
                self._possibleSkillLevel = MAX_SKILL_LEVEL - 1
            else:
                self._possibleSkillLevel -= 1
        elif self._possibleSkillLevel > max(self._currentSkillLevel, 1):
            self._possibleSkillLevel -= 1
        else:
            return 1
        return self._countResultAndConvertToFreeXp()

    def getSkillUpXpCost(self):
        if not self._currentTankman:
            return 0
        if self._possibleSkillsCount + 1 <= self._currentTankman.maxSkillsCount:
            self._possibleSkillsCount += 1
            self._possibleSkillLevel = 0
        elif self._possibleSkillsCount == self._currentTankman.maxSkillsCount:
            self._possibleSkillLevel = MAX_SKILL_LEVEL
        return self._countResultAndConvertToFreeXp()

    def getSkillDownXpCost(self):
        if not self._currentTankman:
            return 0
        if self._possibleSkillLevel > 0 and self._possibleSkillsCount != self._currentSkillsCount:
            self._possibleSkillLevel = 0
        elif self._possibleSkillsCount - 1 > self._currentSkillsCount:
            self._possibleSkillsCount -= 1
        return self._countResultAndConvertToFreeXp()

    def getMaxPossibleValue(self):
        maxCost = self._currentTankman.descriptor.getXpCostForSkillsLevels(MAX_SKILL_LEVEL, self._currentTankman.maxSkillsCount)
        freeXpMaxPossibleValue = self.__convertToFreeXp(maxCost)
        return min(freeXpMaxPossibleValue, self.itemsCache.items.stats.freeXP)

    def _countResultAndConvertToFreeXp(self):
        cost = self._currentTankman.descriptor.getXpCostForSkillsLevels(self._possibleSkillLevel, self._possibleSkillsCount)
        freeXpCost = self.__convertToFreeXp(cost)
        availableFreeXp = self.itemsCache.items.stats.freeXP
        if freeXpCost > availableFreeXp:
            skillsCount, skillLevel = getSkillsLevelsForXp(self._currentTankman, availableFreeXp * self._exchangeRate)
            self._possibleSkillsCount = skillsCount
            self._possibleSkillLevel = int(ceil(skillLevel.formattedSkillLvl))
            return availableFreeXp
        return freeXpCost

    def __convertToFreeXp(self, value):
        value -= self._currentTankman.descriptor.totalXP() + self._aquiringPersonalXpAmount
        targetFreeXp = max(value, 1) / self._exchangeRate
        if value % self._exchangeRate != 0:
            targetFreeXp += 1
        return targetFreeXp
