# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/personal_file/context.py
import typing
from gui.impl.lobby.crew.container_vews.common.base_personal_case_context import BasePersonalCaseContext
from gui.impl.lobby.crew.crew_helpers.skill_helpers import getTmanNewSkillCount
from gui.shared.gui_items.Tankman import SKILL_EFFICIENCY_UNTRAINED
if typing.TYPE_CHECKING:
    from typing import Tuple

class PersonalFileViewContext(BasePersonalCaseContext):
    __slots__ = ('_availableSkillsCount', '_lastSkillLevel', '_skillAnimationsSkipped')

    def __init__(self, tankmanID):
        self._availableSkillsCount = None
        self._lastSkillLevel = None
        self._skillAnimationsSkipped = False
        super(PersonalFileViewContext, self).__init__(tankmanID)
        return

    @property
    def availableSkillsCount(self):
        return self._availableSkillsCount

    @property
    def lastSkillLevel(self):
        return self._lastSkillLevel

    @property
    def skillAnimationsSkipped(self):
        return self._skillAnimationsSkipped

    @property
    def hasIncreaseDiscount(self):
        return not self.tankman.descriptor.isMaxSkillXp() and self.itemsCache.items.shop.freeXPToTManXPRate != self.itemsCache.items.shop.defaults.freeXPToTManXPRate

    @property
    def hasDropSkillDiscount(self):
        for currency, dropCost in self.itemsCache.items.shop.dropSkillsCost.iteritems():
            defaultDropCost = self.itemsCache.items.shop.defaults.dropSkillsCost[currency]
            if dropCost != defaultDropCost:
                return True

        return False

    @property
    def resetDisabled(self):
        return self.tankman.skillsCount == 0 and self.tankman.bonusSkillsCount == 0

    def update(self, tankmanID=None, skillAnimationsSkipped=False):
        self._skillAnimationsSkipped = skillAnimationsSkipped
        if tankmanID:
            super(PersonalFileViewContext, self).update(tankmanID)
            self._availableSkillsCount, self._lastSkillLevel = self._calcSkillsCountAndLevel()

    def getInstalledBooster(self):
        if not self.tankmanCurrentVehicle:
            return None
        else:
            installedBoosters = self.tankmanCurrentVehicle.battleBoosters.installed.getItems()
            installedBoostersCount = len(installedBoosters)
            return None if installedBoostersCount == 0 else installedBoosters[0]

    def _calcSkillsCountAndLevel(self):
        newSkillCnt, lastSkillLevel = getTmanNewSkillCount(self.tankman)
        freeNewSkillCnt = self.tankman.newFreeSkillsCount
        if self.tankman.currentVehicleSkillsEfficiency == SKILL_EFFICIENCY_UNTRAINED:
            skillsCount = freeNewSkillCnt + newSkillCnt
            return (skillsCount, lastSkillLevel)
        if not self.tankman.isMaxSkillEfficiency:
            return (freeNewSkillCnt + newSkillCnt, lastSkillLevel)
        if freeNewSkillCnt > 0:
            return (freeNewSkillCnt, lastSkillLevel)
        return (newSkillCnt, lastSkillLevel) if newSkillCnt > 0 else (0, lastSkillLevel)
