# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/controllers/sound_ctrls/vehicle_frags_sound_player.py
import typing
from fall_tanks.gui.battle_control.mixins import FallTanksBattleMixin
from fall_tanks.gui.feature.fall_tanks_sounds import FallTanksSounds
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayer
if typing.TYPE_CHECKING:
    from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksVehicleInfo

class VehicleFragsSoundPlayer(SoundPlayer, FallTanksBattleMixin):

    def __init__(self):
        self.__isPlayerVehicle = False
        self.__frags = 0

    def init(self):
        super(VehicleFragsSoundPlayer, self).init()
        attachedInfo = self.getFallTanksAttachedVehicleInfo()
        self.__isPlayerVehicle = attachedInfo.isPlayerVehicle
        self.__frags = attachedInfo.frags

    def destroy(self):
        self.__frags = 0
        self.__isPlayerVehicle = False
        super(VehicleFragsSoundPlayer, self).destroy()

    def _subscribe(self):
        self.startFallTanksAttachedListening(self.__onFallTanksAttachedInfoUpdate)

    def _unsubscribe(self):
        self.stopFallTanksAttachedListening(self.__onFallTanksAttachedInfoUpdate)

    def __onFallTanksAttachedInfoUpdate(self, attachedInfo):
        frags = attachedInfo.frags
        isPlayerVehicle = attachedInfo.isPlayerVehicle
        if isPlayerVehicle and self.__isPlayerVehicle and frags > self.__frags:
            self._playSound2D(FallTanksSounds.ENEMY_KILLED)
        self.__isPlayerVehicle = isPlayerVehicle
        self.__frags = frags
