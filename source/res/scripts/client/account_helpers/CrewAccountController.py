# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/CrewAccountController.py
from CurrentVehicle import g_currentVehicle
from gui import SystemMessages
from gui.shared.gui_items.processors.tankman import TankmanAutoReturn
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from skeletons.gui.game_control import IGameController
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from gui.shared.gui_items import GUI_ITEM_TYPE
from skeletons.gui.shared.utils import IHangarSpace

class CrewAccountController(IGameController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, inventory):
        self.__inventory = inventory
        self.tankmanIdxSkillsUnlockAnimation = {}
        self.tankmanLearnedSkillsAnimanion = {}
        self.tankmanVeteranAnimanion = {}
        self._conversionResults = {}
        self.autoReturnCrewData = {}
        self.__inventory.onStartSynchronize += self.__onStartSynchronizeInventory
        self.__hangarSpace.onVehicleChanged += self.__returnCrew

    def getAutoReturnCrewData(self, vehicleIntCD):
        return self.autoReturnCrewData.get(vehicleIntCD, [])

    def onAvatarBecomePlayer(self):
        self.__returnCrew()

    def setAutoReturnCrewData(self, vehicleIntCD, skipTmanInvIDs):
        self.autoReturnCrewData[vehicleIntCD] = skipTmanInvIDs

    def clearTankmanAnimanions(self, tankmaninvID):
        if tankmaninvID in self.tankmanVeteranAnimanion:
            del self.tankmanVeteranAnimanion[tankmaninvID]
        if tankmaninvID in self.tankmanIdxSkillsUnlockAnimation:
            del self.tankmanIdxSkillsUnlockAnimation[tankmaninvID]
        if tankmaninvID in self.tankmanLearnedSkillsAnimanion:
            del self.tankmanLearnedSkillsAnimanion[tankmaninvID]

    def getTankmanVeteranAnimanion(self, tankmaninvID):
        tankman = self.__itemsCache.items.getTankman(tankmaninvID)
        if not tankman:
            return False
        else:
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

    def setConversionResults(self, resultsDict):
        self._conversionResults = resultsDict

    def getSkillsCrewBooksConversion(self):
        crewBooks = {}
        for book in self._conversionResults.get('skillsCrewBooksConversion', []):
            crewBooks.update({book['compDescr']: book['count']})

        return crewBooks

    def getSkillsCrewBoostersReplacement(self):
        return self._conversionResults.get('skillsCrewBoostersReplacement', {})

    def clear(self):
        self.__inventory.onStartSynchronize -= self.__onStartSynchronizeInventory
        self.__hangarSpace.onVehicleChanged -= self.__returnCrew

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

    @decorators.adisp_process('crewReturning')
    def __returnCrew(self):
        if not g_currentVehicle.isPresent():
            return
        currentVehicle = g_currentVehicle.item
        if currentVehicle.isAutoReturn:
            if currentVehicle.isInBattle or currentVehicle.isAwaitingBattle or currentVehicle.isInPrebattle:
                return
            result = yield TankmanAutoReturn(currentVehicle).request()
            if not result.success and result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
