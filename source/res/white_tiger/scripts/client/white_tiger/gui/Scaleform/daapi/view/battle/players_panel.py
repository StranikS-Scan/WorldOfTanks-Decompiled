# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/players_panel.py
from typing import TYPE_CHECKING
import BigWorld
from helpers import time_utils
from debug_utils import LOG_ERROR_DEV
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerPlayersPanelMeta import WhiteTigerPlayersPanelMeta
from white_tiger.gui.wt_event_helpers import isBoss
from white_tiger.cgf_components.wt_helpers import getBattleStateComponent, getPlasmaBonusComponent, isBossBot
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from account_helpers.settings_core import settings_constants
if TYPE_CHECKING:
    from gui.battle_control.arena_info.interfaces import IBattleFieldController

class WhiteTigerPlayersPanel(WhiteTigerPlayersPanelMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerPlayersPanel, self).__init__()
        self.__captureTimePerGenerator = {}
        self.__lastCapturedGeneratorIndex = -1

    def _populate(self):
        super(WhiteTigerPlayersPanel, self)._populate()
        self.as_setIsBossS(self.__isBossPlayer())
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.onGeneratorCapture += self.__onGeneratorCapture
            battleStateComponent.onGeneratorStopCapture += self.__onGeneratorStopCapture
            battleStateComponent.onGeneratorLocked += self.__onGeneratorLocked
            battleStateComponent.onGeneratorsLeftInitialize += self.__onGeneratorDestroyed
            battleStateComponent.onGeneratorDestroyed += self.__onGeneratorDestroyed
            battleStateComponent.onUpdateCamp += self.__onUpdateCamp
            battleStateComponent.onShieldDowntime += self.__onShieldDowntime
            battleFieldCtrl = self.guiSessionProvider.dynamic.battleField
            if battleFieldCtrl:
                battleFieldCtrl.onSpottedStatusChanged += self.__updateSpottedStatus
            else:
                LOG_ERROR_DEV('WhiteTigerPlayersPanel: _populate: Could not find battleFieldCtrl')
        plasmaComponent = getPlasmaBonusComponent()
        if plasmaComponent:
            plasmaComponent.onPlasmaChanged += self.__onPlasmaChanged
        else:
            LOG_ERROR_DEV('WhiteTigerPlayersPanel: _populate: Could not find plasmaBonusComponent')
        self.as_setColorBlindS(self.settingsCore.getSetting('isColorBlind'))
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged

    def _onDispose(self):
        battleStateComponent = getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.onGeneratorCapture -= self.__onGeneratorCapture
            battleStateComponent.onGeneratorStopCapture -= self.__onGeneratorStopCapture
            battleStateComponent.onGeneratorLocked -= self.__onGeneratorLocked
            battleStateComponent.onGeneratorDestroyed -= self.__onGeneratorDestroyed
            battleStateComponent.onGeneratorsLeftInitialize -= self.__onGeneratorDestroyed
            battleStateComponent.onUpdateCamp -= self.__onUpdateCamp
            battleStateComponent.onShieldDowntime -= self.__onShieldDowntime
            battleStateComponent.onSpottedStatusChanged -= self.__updateSpottedStatus
            battleFieldCtrl = self.guiSessionProvider.dynamic.battleField
            if battleFieldCtrl:
                battleFieldCtrl.onSpottedStatusChanged -= self.__updateSpottedStatus
            else:
                LOG_ERROR_DEV('WhiteTigerPlayersPanel: _onDispose: Could not find battleFieldCtrl')
        plasmaComponent = getPlasmaBonusComponent()
        if plasmaComponent:
            plasmaComponent.onPlasmaChanged -= self.__onPlasmaChanged
        else:
            LOG_ERROR_DEV('WhiteTigerPlayersPanel: _onDispose: Could not find plasmaBonusComponent')
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(WhiteTigerPlayersPanel, self)._dispose()

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        if newHealth < 0:
            newHealth = 0
        if isBossBot(vehicleID):
            self.as_updateBossBotHpS(vehicleID, maxHealth, newHealth)
        else:
            super(WhiteTigerPlayersPanel, self).updateVehicleHealth(vehicleID, newHealth, maxHealth)

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        for vehicleID in deadEnemies | deadAllies:
            if vehicleID in aliveAllies | aliveEnemies:
                continue
            if isBossBot(vehicleID):
                arenaDP = self.sessionProvider.getArenaDP()
                vInfo = arenaDP.getVehicleInfo(vehicleID)
                self.as_updateBossBotHpS(vehicleID, vInfo.vehicleType.maxHealth, 0)
            self.as_setPlayerHPS(vehicleID in deadAllies, vehicleID, 0)

    def __updateSpottedStatus(self, data, arenaDP):
        for flags, vStatsVO in data:
            if flags == INVALIDATE_OP.VEHICLE_STATS:
                vehicleID = vStatsVO.vehicleID
                if isBossBot(vehicleID):
                    self.as_setBossBotSpottedS(vehicleID, vStatsVO.spottedStatus)

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

    def __onUpdateCamp(self, generatorID, vehicleIDs):
        self.destroyCamp(generatorID)
        vInfos = []
        arenaDP = self.__sessionProvider.getArenaDP()
        for vID in vehicleIDs:
            vInfo = arenaDP.getVehicleInfo(vID)
            if vInfo.vehicleID == vID:
                vInfos.append(vInfo)

        self.updateCamp(generatorID, vInfos)
        self.updateCampInfoStatus(generatorID)

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

    def __onGeneratorCapture(self, index, progress, timeLeft, numInvaders, isBlocked):
        if self.__captureTimePerGenerator.get(index) is None:
            self.__captureTimePerGenerator[index] = {}
        self.__captureTimePerGenerator[index]['timeLeft'] = timeLeft
        self.as_updateGeneratorCaptureTimerS(index, timeLeft, progress, numInvaders, 1)
        self.as_updateGeneratorDownTimeS(index, '')
        return

    def __onGeneratorStopCapture(self, index, wasCaptured):
        if wasCaptured:
            self.as_setIsDestroyedS(index)
            self.__lastCapturedGeneratorIndex = index
            return
        if not self.__captureTimePerGenerator.get(index):
            return
        self.as_resetGeneratorCaptureTimerS(index)

    def __onShieldDowntime(self, _, remainingTime):
        timeText = time_utils.getTimeLeftFormat(remainingTime)
        self.as_updateGeneratorDownTimeS(self.__lastCapturedGeneratorIndex, timeText)

    def __onGeneratorDestroyed(self, generatorsLeft):
        if generatorsLeft == 0:
            self.as_setAllBossBotCampsOfflineS()
            self.__captureTimePerGenerator.clear()

    def __onGeneratorLocked(self, generatorID, isLocked, _, __, ___):
        self.as_lockGeneratorS(generatorID, isLocked)
        self.updateCampInfoStatus(generatorID)

    def __onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.COLOR_BLIND in diff:
            self.as_setColorBlindS(self.settingsCore.getSetting('isColorBlind'))

    def __onPlasmaChanged(self, plasmaDict):
        for vehId, value in plasmaDict.items():
            self.as_setPlasmaForVehiclesS(vehId, value)
