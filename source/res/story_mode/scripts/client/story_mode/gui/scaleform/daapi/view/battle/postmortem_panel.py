# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/postmortem_panel.py
from constants import VEHICLE_BUNKER_TURRET_TAG
from gui.Scaleform.daapi.view.battle.pve_base.postmortem_panel import PvePostmortemPanel
BUNKER_CODE = 'DEATH_FROM_BUNKER'
SHOT_CODE = 'DEATH_FROM_SHOT'
BOT_CODE = 'DEATH_FROM_BOT'

class StoryModePostmortemPanel(PvePostmortemPanel):
    __slots__ = ()

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
        elif code == SHOT_CODE and self.__isBot(killerVehID):
            self.__showCustomMessage(BOT_CODE, killerVehID, device)
        else:
            super(StoryModePostmortemPanel, self)._prepareMessage(code, killerVehID, device)

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
