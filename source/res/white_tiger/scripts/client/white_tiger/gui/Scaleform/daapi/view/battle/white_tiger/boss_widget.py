# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/boss_widget.py
from constants import WT_COMPONENT_NAMES
from white_tiger.gui.Scaleform.daapi.view.meta.WTBossWidgetMeta import WTBossWidgetMeta
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info import player_format
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class WhiteTigerBossWidget(WTBossWidgetMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WhiteTigerBossWidget, self).__init__()
        self.__playerFormatter = player_format.PlayerFullNameFormatter()

    def setupBossInfo(self, vInfo):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        parts = self.__playerFormatter.format(vInfo)
        self.as_setWidgetDataS({'playerName': parts.playerName,
         'playerFakeName': parts.playerFakeName,
         'playerFullName': parts.playerFullName,
         'clanAbbrev': vInfo.player.clanAbbrev,
         'hpCurrent': vInfo.vehicleType.maxHealth,
         'kills': self.__getKills(vInfo),
         'isPlayer': vInfo.vehicleID == playerVehicleID,
         'hpMax': vInfo.vehicleType.maxHealth,
         'isSpecial': VEHICLE_TAGS.EVENT_SPECIAL_BOSS in vInfo.vehicleType.tags,
         'region': parts.regionCode})

    def updateBossInfo(self, vInfo):
        self.as_updateKillsS(self.__getKills(vInfo))

    def _populate(self):
        super(WhiteTigerBossWidget, self)._populate()
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
            feedback.onArenaTimer += self.__onArenaTimer
            feedback.onPublicCounter += self.__onPublicCounter
            feedback.onGeneratorCapture += self.__onGeneratorCapture
            feedback.onGeneratorStopCapture += self.__onGeneratorStopCapture

    def _dispose(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
            feedback.onArenaTimer -= self.__onArenaTimer
            feedback.onPublicCounter -= self.__onPublicCounter
            feedback.onGeneratorCapture -= self.__onGeneratorCapture
            feedback.onGeneratorStopCapture -= self.__onGeneratorStopCapture
        super(WhiteTigerBossWidget, self)._dispose()

    def __onPublicCounter(self, count, maxCount, counterName):
        if counterName == WT_COMPONENT_NAMES.GENERATORS_COUNTER:
            self.as_updateGeneratorsS(count)
        elif counterName == WT_COMPONENT_NAMES.HYPERION_COUNTER:
            self.as_updateHyperionChargeS(count, maxCount)

    def __onArenaTimer(self, name, totalTime, remainingTime):
        if name == WT_COMPONENT_NAMES.SHIELD_DEBUFF_ARENA_TIMER:
            self.as_updateDebuffS(totalTime, remainingTime)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID != FEEDBACK_EVENT_ID.VEHICLE_HEALTH:
            return
        arenaDP = self.__sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo(vehicleID)
        newHealth = value[0]
        if VEHICLE_TAGS.EVENT_BOSS in vInfoVO.vehicleType.tags:
            self.as_updateHpS(newHealth)

    def __getKills(self, vInfo):
        arenaDP = self.__sessionProvider.getArenaDP()
        vStats = arenaDP.getVehicleStats(vInfo.vehicleID)
        frags = vStats.frags if vStats is not None else 0
        return frags

    def __onGeneratorCapture(self, index, progress, timeLeft, numInvaders):
        self.as_updateGeneratorsChargingS(index, timeLeft, progress, numInvaders, 1)

    def __onGeneratorStopCapture(self, index, wasCaptured):
        self.as_resetGeneratorCaptureTimerS(index)
