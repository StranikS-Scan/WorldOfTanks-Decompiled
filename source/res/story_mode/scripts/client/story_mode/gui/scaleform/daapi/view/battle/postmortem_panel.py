# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/postmortem_panel.py
import SoundGroups
from constants import VEHICLE_BUNKER_TURRET_TAG
from gui.Scaleform.daapi.view.battle.pve_base.postmortem_panel import PvePostmortemPanel, LivesState
from story_mode.gui.sound_constants import RESPAWN_TIMER_SOUND_EVENT, RESPAWN_TIMER_STATE_GROUP, RESPAWN_TIMER_STATE_OFF, RESPAWN_TIMER_STATE_ON
BUNKER_CODE = 'DEATH_FROM_BUNKER'
SHOT_CODES = ('DEATH_FROM_SHOT', 'DEATH_FROM_DEVICE_EXPLOSION_AT_SHOT')
BOT_CODE = 'DEATH_FROM_BOT'
_TIMER_ZERO_VALUE = '00:00'

class StoryModePostmortemPanel(PvePostmortemPanel):
    __slots__ = ()

    def resetDeathInfo(self):
        super(StoryModePostmortemPanel, self).resetDeathInfo()
        SoundGroups.g_instance.setState(RESPAWN_TIMER_STATE_GROUP, RESPAWN_TIMER_STATE_OFF)

    def _dispose(self):
        SoundGroups.g_instance.setState(RESPAWN_TIMER_STATE_GROUP, RESPAWN_TIMER_STATE_OFF)
        super(StoryModePostmortemPanel, self)._dispose()

    def _showOwnDeathInfo(self):
        if not self._deathAlreadySet:
            deathInfo = self.getDeathInfo()
            if deathInfo is not None and self.__isBunkerTurret(deathInfo['killerVehicle']):
                self.as_setDeadReasonInfoS(self._makeReasonInfo(deathInfo), False, '', '', '', '', None)
                return
        super(StoryModePostmortemPanel, self)._showOwnDeathInfo()
        return

    def _prepareMessage(self, code, killerVehID, device=None):
        if self.__isBunkerTurret(killerVehID):
            self.__showCustomMessage(BUNKER_CODE, killerVehID, device)
        elif code in SHOT_CODES and self.__isBot(killerVehID):
            self.__showCustomMessage(BOT_CODE, killerVehID, device)
        else:
            super(StoryModePostmortemPanel, self)._prepareMessage(code, killerVehID, device)

    def _applyLivesState(self, livesState):
        if livesState == LivesState.HAS_LIVES:
            SoundGroups.g_instance.setState(RESPAWN_TIMER_STATE_GROUP, RESPAWN_TIMER_STATE_ON)
        super(StoryModePostmortemPanel, self)._applyLivesState(livesState)

    def __isBunkerTurret(self, vehicleID):
        if vehicleID is None:
            return False
        else:
            vehicleInfoVO = self.sessionProvider.getCtx().getArenaDP().getVehicleInfo(vehicleID)
            return VEHICLE_BUNKER_TURRET_TAG in vehicleInfoVO.vehicleType.tags

    def __isBot(self, vehicleID):
        if vehicleID is None:
            return False
        else:
            vehicleInfoVO = self.sessionProvider.getCtx().getArenaDP().getVehicleInfo(vehicleID)
            return vehicleInfoVO.player.isBot

    def __showCustomMessage(self, code, killerVehID, device=None):
        msgText, colors = self._messages[code]
        self._deathInfo = {'text': msgText,
         'colors': colors,
         'killerVehicle': killerVehID,
         'device': device}
        self._deathInfoReceived()

    def updateTime(self, value):
        if value != _TIMER_ZERO_VALUE:
            SoundGroups.g_instance.playSound2D(RESPAWN_TIMER_SOUND_EVENT)
