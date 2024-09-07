# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/CrewAccountController.py
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from gui.shared.gui_items import GUI_ITEM_TYPE

class CrewAccountController(object):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, inventory):
        self.__inventory = inventory
        self.tankmanIdxSkillsUnlockAnimation = {}
        self.tankmanLearnedSkillsAnimanion = {}
        self.tankmanVeteranAnimanion = {}
        self.__inventory.onStartSynchronize += self.__onStartSynchronizeInventory

    def clearTankmanAnimanions(self, tankmaninvID):
        if tankmaninvID in self.tankmanVeteranAnimanion:
            del self.tankmanVeteranAnimanion[tankmaninvID]
        if tankmaninvID in self.tankmanIdxSkillsUnlockAnimation:
            del self.tankmanIdxSkillsUnlockAnimation[tankmaninvID]
        if tankmaninvID in self.tankmanLearnedSkillsAnimanion:
            del self.tankmanLearnedSkillsAnimanion[tankmaninvID]

    def getTankmanVeteranAnimanion(self, tankmaninvID):
        tankman = self.__itemsCache.items.getTankman(tankmaninvID)
        concurrent = not bool(tankman.descriptor.needXpForVeteran)
        before = self.tankmanVeteranAnimanion.get(tankmaninvID)
        return before is not None and not before and concurrent

    def setLearnedSkillsAnimanion(self, tankmaninvID, learnedSkills):
        skills = self.tankmanLearnedSkillsAnimanion.setdefault(tankmaninvID, [])
        skills += learnedSkills

    def hasLearnedSkillAnimation(self, tankmaninvID, skillName):
        return skillName in self.tankmanLearnedSkillsAnimanion.get(tankmaninvID, [])

    def indexSkillsUnlockAnimation(self, tankmaninvID):
        return self.tankmanIdxSkillsUnlockAnimation.get(tankmaninvID)

    def clear(self):
        self.__inventory.onStartSynchronize -= self.__onStartSynchronizeInventory

    def __onStartSynchronizeInventory(self, isFullSync, diff):
        if isFullSync:
            return
        descriptors = diff.get('inventory', {}).get(GUI_ITEM_TYPE.TANKMAN, {}).get('compDescr', {})
        for invID in descriptors.iterkeys():
            tankman = self.__itemsCache.items.getTankman(invID)
            if tankman:
                self.tankmanIdxSkillsUnlockAnimation.setdefault(invID, 0)
                self.tankmanIdxSkillsUnlockAnimation[invID], _ = tankman.descriptor.getTotalSkillsProgress(True)
                self.tankmanVeteranAnimanion.setdefault(invID, False)
                self.tankmanVeteranAnimanion[invID] = not bool(tankman.descriptor.needXpForVeteran)
