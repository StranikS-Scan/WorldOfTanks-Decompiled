# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/stepper_calculator.py
from helpers import dependency
from items.tankmen import TankmanDescr, MAX_SKILL_LEVEL, _MAX_FREE_XP as MAX_FREE_XP
from skeletons.gui.shared import IItemsCache
from skill_formatters import SkillLvlFormatter

class FreeXpStepperCalculator(object):
    availableFreeXp = property(lambda self: self.itemsCache.items.stats.freeXP)
    exchangeRate = property(lambda self: self.itemsCache.items.shop.freeXPToTManXPRate)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__lastSkillsCount = 0
        self.__possibleSkillsCount = 0
        self.__availableSkillsCount = 0
        self.__lastSkillLevel = SkillLvlFormatter()
        self.__possibleSkillLevel = SkillLvlFormatter()
        self.__lastPossibleStateXpCost = 0
        self.__lastPossibleRoleStateXpCost = 0
        self.__lastRoleLevel = SkillLvlFormatter(50)
        self.__possibleRoleLevel = SkillLvlFormatter(50)

    def setAvailableSkillsCount(self, availableSkillsCount):
        self.__availableSkillsCount = availableSkillsCount

    def setState(self, lastSkillsCount, possibleSkillsCount, lastSkillLevel, possibleSkillLevel, lastRoleLevel, possibleRoleLevel):
        self.__lastSkillsCount = lastSkillsCount
        self.__lastSkillLevel = lastSkillLevel
        self.__lastRoleLevel = lastRoleLevel
        if self.__lastSkillsCount > self.__availableSkillsCount or self.__lastSkillsCount == self.__availableSkillsCount and self.__lastSkillLevel == MAX_SKILL_LEVEL:
            self.__lastSkillsCount = self.__availableSkillsCount
            self.__lastSkillLevel = SkillLvlFormatter(MAX_SKILL_LEVEL)
        self.__possibleSkillsCount = possibleSkillsCount if possibleSkillsCount > 0 else self.__lastSkillsCount
        self.__possibleSkillLevel = possibleSkillLevel if possibleSkillLevel.isSkillLvl else self.__lastSkillLevel
        self.__possibleRoleLevel = possibleRoleLevel if possibleRoleLevel.intSkillLvl > 0 else self.__lastRoleLevel
        if self.__possibleSkillsCount > self.__availableSkillsCount or self.__possibleSkillsCount == self.__availableSkillsCount and self.__possibleSkillLevel == MAX_SKILL_LEVEL:
            self.__possibleSkillsCount = self.__availableSkillsCount
            self.__possibleSkillLevel = SkillLvlFormatter(MAX_SKILL_LEVEL)
        self.__lastPossibleStateXpCost = FreeXpStepperCalculator._getXpCostImpl(self.__possibleSkillLevel, self.__possibleSkillsCount)
        self.__lastPossibleRoleStateXpCost = FreeXpStepperCalculator._getXpCostImpl(self.__possibleRoleLevel, 0)

    def getMaxAvailbleStateCostXp(self):
        lastSkillsLevelsXpCost = FreeXpStepperCalculator._getXpCostImpl(self.__lastSkillLevel, self.__lastSkillsCount)
        targetSkillsLevelsXpCost = FreeXpStepperCalculator._getXpCostImpl(SkillLvlFormatter(MAX_SKILL_LEVEL if self.__availableSkillsCount else 0), self.__availableSkillsCount)
        return self._getTargetFreeXp(targetSkillsLevelsXpCost - lastSkillsLevelsXpCost)

    def getLevelDownXpState(self):
        if self.__possibleRoleLevel >= self.__lastRoleLevel and (self.__possibleSkillLevel == 0 or self.__possibleSkillsCount >= self.__availableSkillsCount or self.__possibleSkillLevel.intSkillLvl == self.__lastSkillLevel.intSkillLvl and self.__possibleSkillsCount == self.__lastSkillsCount):
            possibleSkillLevel = self.__possibleRoleLevel - 1
            possibleSkillsCount = 0
            targetTmanXp = self.getRoleStepXpCost(possibleSkillsCount, possibleSkillLevel)
        else:
            if not self.__possibleSkillsCount:
                possibleSkillLevel = self.__lastSkillLevel
                possibleSkillsCount = self.__lastSkillsCount
            else:
                possibleSkillLevel = self.__possibleSkillLevel
                possibleSkillsCount = self.__possibleSkillsCount
                if self.__possibleSkillLevel == 0:
                    possibleSkillLevel = SkillLvlFormatter(MAX_SKILL_LEVEL, self.__possibleSkillLevel.residualXp, self.__possibleSkillLevel.lvlCostXp)
                    possibleSkillsCount = self.__possibleSkillsCount - 1
                possibleSkillLevel -= int(possibleSkillLevel.residualXp < self.exchangeRate)
            targetTmanXp = self.getStepXpCost(possibleSkillsCount, possibleSkillLevel)
        return self._getTargetFreeXp(targetTmanXp)

    def getLevelUpXpState(self):
        if self.__possibleRoleLevel < MAX_SKILL_LEVEL and (self.__possibleSkillLevel == 0 or self.__possibleSkillsCount >= self.__availableSkillsCount):
            possibleSkillLevel = self.__possibleRoleLevel + 1
            possibleSkillsCount = 0
            targetTmanXp = self.getRoleStepXpCost(possibleSkillsCount, possibleSkillLevel)
        else:
            if not self.__possibleSkillsCount:
                possibleSkillLevel = self.__lastSkillLevel
                possibleSkillsCount = self.__lastSkillsCount
            else:
                possibleSkillLevel = self.__possibleSkillLevel
                possibleSkillsCount = self.__possibleSkillsCount
                if possibleSkillLevel == MAX_SKILL_LEVEL:
                    possibleSkillLevel = SkillLvlFormatter(0, self.__possibleSkillLevel.residualXp, self.__possibleSkillLevel.lvlCostXp)
                    possibleSkillsCount = self.__possibleSkillsCount + 1
                possibleSkillLevel += 1
            targetTmanXp = self.getStepXpCost(possibleSkillsCount, possibleSkillLevel)
        return self._getTargetFreeXp(targetTmanXp)

    def getSkillDownXpState(self):
        if (self.__possibleSkillsCount <= 1 or self.__lastSkillsCount == self.__availableSkillsCount) and self.__lastRoleLevel.intSkillLvl < MAX_SKILL_LEVEL:
            if self.__possibleRoleLevel > self.__lastRoleLevel:
                before = TankmanDescr.getXpCostForSkillsLevels(self.__possibleRoleLevel.intSkillLvl, 0)
                after = TankmanDescr.getXpCostForSkillsLevels(self.__lastRoleLevel.intSkillLvl, 0)
                return self._getTargetFreeXp(after - before)
            return 0
        possibleSkillsCount = self.__possibleSkillsCount - int(not self.__possibleSkillLevel.intSkillLvl) if self.__possibleSkillsCount else self.__lastSkillsCount
        possibleSkillLevel = SkillLvlFormatter(0) if self.__possibleSkillsCount else self.__lastSkillLevel
        targetTmanXp = self.getStepXpCost(possibleSkillsCount, possibleSkillLevel)
        return self._getTargetFreeXp(targetTmanXp)

    def getSkillUpXpState(self):
        isRoleMax = self.__possibleRoleLevel.intSkillLvl == MAX_SKILL_LEVEL
        if self.__possibleSkillsCount > self.__availableSkillsCount or self.__possibleSkillsCount == 0 and not isRoleMax:
            if not isRoleMax:
                before = TankmanDescr.getXpCostForSkillsLevels(self.__possibleRoleLevel.intSkillLvl, 0)
                after = TankmanDescr.getXpCostForSkillsLevels(MAX_SKILL_LEVEL, 0)
                return self._getTargetFreeXp(after - before)
            return 0
        possibleSkillsCount = self.__possibleSkillsCount + 1 if self.__possibleSkillsCount else self.__lastSkillsCount
        possibleSkillLevel = SkillLvlFormatter(0) if self.__possibleSkillsCount else self.__lastSkillLevel
        targetTmanXp = self.getStepXpCost(possibleSkillsCount, possibleSkillLevel)
        return self._getTargetFreeXp(targetTmanXp)

    def _getTargetFreeXp(self, targetTmanXp):
        return self._checkAvailableXp(self._convertToFreeXP(min(targetTmanXp, MAX_FREE_XP), self.exchangeRate), self.availableFreeXp)

    def getStepXpCost(self, targetSkillsCount, targetSkillLevel):
        if targetSkillsCount < self.__lastSkillsCount or targetSkillsCount == self.__lastSkillsCount and targetSkillLevel <= self.__lastSkillLevel:
            targetSkillsCount = self.__lastSkillsCount
            targetSkillLevel = self.__lastSkillLevel
        elif targetSkillsCount > self.__availableSkillsCount or targetSkillsCount == self.__availableSkillsCount and targetSkillLevel == MAX_SKILL_LEVEL:
            targetSkillsCount = self.__availableSkillsCount
            targetSkillLevel = SkillLvlFormatter(MAX_SKILL_LEVEL if self.__availableSkillsCount else 0)
        return FreeXpStepperCalculator._getStepXpCost(self.__lastPossibleStateXpCost, targetSkillsCount, targetSkillLevel)

    def getRoleStepXpCost(self, targetSkillsCount, targetSkillLevel):
        return FreeXpStepperCalculator._getStepXpCost(self.__lastPossibleRoleStateXpCost, targetSkillsCount, targetSkillLevel)

    @staticmethod
    def _getXpCostImpl(skillLevel, skillsCount):
        return TankmanDescr.getXpCostForSkillsLevels(skillLevel.intSkillLvl, skillsCount) + skillLevel.residualXp

    @staticmethod
    def _getStepXpCost(lastSkillsLevelsXpCost, targetSkillsCount, targetSkillLevel):
        targetSkillsLevelsXpCost = FreeXpStepperCalculator._getXpCostImpl(targetSkillLevel, targetSkillsCount)
        return targetSkillsLevelsXpCost - lastSkillsLevelsXpCost

    @staticmethod
    def _convertToFreeXP(tmanXP, exchangeRate):
        targetFreeXp = tmanXP / exchangeRate
        if tmanXP % exchangeRate != 0:
            targetFreeXp += 1
        return targetFreeXp

    @staticmethod
    def _checkAvailableXp(targetFreeXp, availableFreeXp):
        return min(targetFreeXp, availableFreeXp)
