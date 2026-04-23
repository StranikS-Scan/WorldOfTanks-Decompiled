# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBLastStand.py
import typing
import logging
import BigWorld
import CGF
import functools
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from items import vehicles
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)

class HBLastStand(BigWorld.DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def vehicle(self):
        return self.entity

    def set_isLastStandActive(self, _):
        if self.isLastStandActive:
            feedbackCtrl = self.guiSessionProvider.shared.feedback
            if feedbackCtrl:
                feedbackCtrl.setVehicleNewHealth(self.vehicle.id, 0)
            BigWorld.callback(self.destructionDelaySec, self.__loadEffect)
            if self.vehicle.id != avatar_getter.getPlayerVehicleID():
                self.__onActivatedNPC()
                return
            data = {'destructionDelay': self.destructionDelaySec,
             'destructionTime': BigWorld.serverTime() + self.destructionDelaySec}
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HB_LAST_STAND, data)
            chatCommands = self.guiSessionProvider.shared.chatCommands
            if chatCommands:
                chatCommands.handleChatCommand(BATTLE_CHAT_COMMAND_NAMES.HB_LAST_STAND, targetID=-1)

    def __loadEffect(self):
        if not self.equipmentID:
            _logger.error("Can't load HBLastStand destroy effect. Invalid equipmentID %s", self.equipmentID)
            return
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        if equipment.effectDuration < 0:
            _logger.error('HBLastStand Effect duration must be greater then 0')
            return
        CGF.loadGameObject(equipment.effectPrefabPath, self.vehicle.spaceID, self.vehicle.position, self.__onEffectLoaded)

    def __onEffectLoaded(self, gameObject):
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        BigWorld.callback(equipment.effectDuration, functools.partial(CGF.removeGameObject, gameObject))

    def __onActivatedNPC(self):
        equipment = vehicles.g_cache.equipments()[self.equipmentID]
        activationSoundNPC = equipment.soundNotificationNPC
        avatar_getter.getSoundNotifications().play(activationSoundNPC, vehicleID=self.vehicle.id)
