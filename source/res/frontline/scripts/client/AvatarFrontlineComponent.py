# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/AvatarFrontlineComponent.py
from debug_utils import LOG_DEBUG
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.game_control import IEpicBattleController

class AvatarFrontlineComponent(DynamicScriptComponent):
    __battleController = dependency.descriptor(IEpicBattleController)

    def onDestroy(self):
        super(AvatarFrontlineComponent, self).onDestroy()
        self.__battleController.reset()

    def set_sectors(self, _):
        self.__battleController.setOwnSectors(self.sectors)
        LOG_DEBUG('[EPIC_QUEST] New sectors', self.sectors)

    def set_questName(self, _):
        LOG_DEBUG('[EPIC_QUEST] New quest', self.questName)
        self.__battleController.setQuest(self.questName)

    def set_sectorProgression(self, _):
        self.__battleController.setSectorProgression(self.sectorProgression)
        LOG_DEBUG('[EPIC_QUEST] New sectorProgression', self.sectorProgression)

    def updateQuestProgress(self, questName, progressesInfo):
        LOG_DEBUG('[EPIC_QUEST] Progress:', self.questName, questName, progressesInfo)
        self.__battleController.updateQuestProgress(questName, progressesInfo)

    def notifySupplyActivated(self, supplyTypeID):
        LOG_DEBUG('[EPIC_PROGRESSION] Supply activated:', supplyTypeID)
        self.__battleController.onSupplyActivated(supplyTypeID)

    def notifyAirshipCome(self, isAlly):
        LOG_DEBUG('[EPIC_PROGRESSION] Airship Come')
        self.__battleController.onAirshipCome(isAlly)

    def setCurrentSector(self, sectorID):
        self.__battleController.setCurrentSector(sectorID)

    def _onAvatarReady(self):
        if self.questName:
            self.__battleController.setQuest(self.questName)
        if self.sectors:
            self.__battleController.setOwnSectors(self.sectors)
        if self.sectorProgression:
            self.__battleController.setSectorProgression(self.sectorProgression)
