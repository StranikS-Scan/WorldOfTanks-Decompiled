# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/white_tiger_players_panel.py
import BigWorld
from gui.battle_control.controllers.players_panel_ctrl import IPlayersPanelListener, isBossBot
from white_tiger.gui.Scaleform.daapi.view.meta.WTPlayersPanelMeta import WTPlayersPanelMeta
from gui.wt_event.wt_event_helpers import isBoss
from helpers import time_utils
from white_tiger_common.wt_constants import WT_COMPONENT_NAMES

class WhiteTigerPlayersPanel(WTPlayersPanelMeta, IPlayersPanelListener):

    def __init__(self):
        super(WhiteTigerPlayersPanel, self).__init__()
        self.__captureTimePerGenerator = {}
        self.__lastCapturedGeneratorIndex = -1

    def _populate(self):
        super(WhiteTigerPlayersPanel, self)._populate()
        self.as_setIsBossS(self.__isBossPlayer())
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onGeneratorCapture += self.__onGeneratorCapture
            feedback.onGeneratorStopCapture += self.__onGeneratorStopCapture
            feedback.onArenaTimer += self.__onGeneratorDestroy
            feedback.onPublicCounter += self.__onPublicCounter
        return

    def _onDispose(self):
        feedback = self.sessionProvider.shared.feedback
        if feedback is not None:
            feedback.onGeneratorCapture -= self.__onGeneratorCapture
            feedback.onGeneratorStopCapture -= self.__onGeneratorStopCapture
            feedback.onArenaTimer -= self.__onGeneratorDestroy
            feedback.onPublicCounter -= self.__onPublicCounter
        super(WhiteTigerPlayersPanel, self)._dispose()
        return

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        if newHealth < 0:
            newHealth = 0
        if isBossBot(vehicleID):
            self.as_updateBossBotHpS(vehicleID, maxHealth, newHealth)
        else:
            super(WhiteTigerPlayersPanel, self).updateVehicleHealth(vehicleID, newHealth, maxHealth)

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        for vehicleID in deadEnemies | deadAllies:
            if not isBossBot(vehicleID):
                continue
            arenaDP = self.sessionProvider.getArenaDP()
            vInfo = arenaDP.getVehicleInfo(vehicleID)
            self.as_updateBossBotHpS(vehicleID, vInfo.vehicleType.maxHealth, 0)

    def updateSpottedStatus(self, vehicleID, spottedState):
        if isBossBot(vehicleID):
            self.as_setBossBotSpottedS(vehicleID, spottedState)

    def updateCamp(self, campID, vInfos):
        ctrl = self.sessionProvider.dynamic.battleField
        for vInfo in vInfos:
            currentHealth = vInfo.vehicleType.maxHealth
            if ctrl is not None:
                if vInfo.isAlive():
                    healthInfo = ctrl.getVehicleHealthInfo(vInfo.vehicleID)
                    if healthInfo is not None:
                        currentHealth = healthInfo[0]
                else:
                    currentHealth = 0
            botInfo = {'typeVehicle': vInfo.vehicleType.classTag,
             'hpMax': vInfo.vehicleType.maxHealth,
             'hpCurrent': currentHealth,
             'vehID': vInfo.vehicleID,
             'vehicleIcon': vInfo.vehicleType.iconName,
             'campIndex': campID,
             'vehicleGuiName': vInfo.vehicleType.guiName}
            self.as_setBossBotInfoS(botInfo)

        return

    def destroyCamp(self, campID):
        self.as_clearBossBotCampS(campID)

    def updateCampInfoStatus(self, campID):
        self.as_updateCampInfoStatusS(campID)

    def _handleNextMode(self, _):
        pass

    def __isBossPlayer(self):
        vInfo = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        tags = vInfo.vehicleType.tags
        return isBoss(tags)

    def __onGeneratorCapture(self, index, progress, timeLeft, numInvaders):
        if self.__captureTimePerGenerator.get(index) is None:
            self.__captureTimePerGenerator[index] = {}
        self.__captureTimePerGenerator[index]['timeLeft'] = timeLeft
        self.as_updateGeneratorCaptureTimerS(index, timeLeft, progress, numInvaders, 1)
        return

    def __onGeneratorStopCapture(self, index, wasCaptured):
        if wasCaptured:
            self.as_setIsDestroyedS(index, True)
            self.__lastCapturedGeneratorIndex = index
            return
        if not self.__captureTimePerGenerator.get(index):
            return
        if index == self.__lastCapturedGeneratorIndex:
            return
        self.as_resetGeneratorCaptureTimerS(index)

    def __onGeneratorDestroy(self, name, totalTime, remainingTime):
        if name == WT_COMPONENT_NAMES.SHIELD_DEBUFF_ARENA_TIMER and remainingTime > 0:
            timeText = time_utils.getTimeLeftFormat(remainingTime)
            self.as_updateGeneratorDownTimeS(self.__lastCapturedGeneratorIndex, totalTime, remainingTime, timeText)

    def __onPublicCounter(self, counter, _, counterName):
        if counterName == WT_COMPONENT_NAMES.GENERATORS_COUNTER and counter == 0:
            self.as_setAllBossBotCampsOfflineS()
            self.__captureTimePerGenerator.clear()
