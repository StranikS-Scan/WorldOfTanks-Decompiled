# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/boss_widget.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EventBossWidgetMeta import EventBossWidgetMeta
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info import player_format
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_SHIELD_DEBUFF_ARENA_TIMER = 'wtShieldDebuffDuration'
_ACTIVATION_ARENA_TIMER = 'activationTimer'

class EventBossWidget(EventBossWidgetMeta):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __MAX_LIVES = 3

    def __init__(self):
        super(EventBossWidget, self).__init__()
        self.__playerFormatter = player_format.PlayerFullNameFormatter()

    def setupBossInfo(self, vInfo):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        parts = self.__playerFormatter.format(vInfo)
        self.as_setWidgetDataS({'playerName': parts.playerName,
         'playerFakeName': parts.playerFakeName,
         'playerFullName': parts.playerFullName,
         'clanAbbrev': vInfo.player.clanAbbrev,
         'hpCurrent': vInfo.vehicleType.maxHealth,
         'kills': self.__getKills(),
         'isPlayer': vInfo.vehicleID == playerVehicleID,
         'hpMax': vInfo.vehicleType.maxHealth,
         'isSpecial': VEHICLE_TAGS.EVENT_SPECIAL_BOSS in vInfo.vehicleType.tags,
         'region': parts.regionCode})

    def __getKills(self):
        teamLivesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
        if teamLivesComponent:
            kills = self.__MAX_LIVES * len(teamLivesComponent.teamLives) - sum(teamLivesComponent.teamLives.values())
        else:
            kills = 0
        return kills

    def _populate(self):
        super(EventBossWidget, self)._populate()
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
            feedback.onArenaTimer += self.__onArenaTimer
            feedback.onPublicCounter += self.__onPublicCounter
        spawnCtrl = self.__sessionProvider.dynamic.spawn
        if spawnCtrl is not None:
            spawnCtrl.onTeamLivesUpdated += self.__onTeamLivesUpdated
        return

    def _dispose(self):
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
            feedback.onArenaTimer -= self.__onArenaTimer
            feedback.onPublicCounter -= self.__onPublicCounter
        spawnCtrl = self.__sessionProvider.dynamic.spawn
        if spawnCtrl is not None:
            spawnCtrl.onTeamLivesUpdated -= self.__onTeamLivesUpdated
        super(EventBossWidget, self)._dispose()
        return

    def __onTeamLivesUpdated(self):
        self.as_updateKillsS(self.__getKills())

    def __onPublicCounter(self, name, count, maxCount):
        self.as_updateGeneratorsS(count)

    def __onArenaTimer(self, name, totalTime, remainingTime):
        if name == _SHIELD_DEBUFF_ARENA_TIMER:
            self.as_updateDebuffS(totalTime, remainingTime)
        if name == _ACTIVATION_ARENA_TIMER:
            self.as_updateGeneratorsChargingS(totalTime, remainingTime)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID != FEEDBACK_EVENT_ID.VEHICLE_HEALTH:
            return
        arenaDP = self.__sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo(vehicleID)
        newHealth = value[0]
        if {VEHICLE_TAGS.EVENT_BOSS} & vInfoVO.vehicleType.tags:
            self.as_updateHpS(newHealth)
