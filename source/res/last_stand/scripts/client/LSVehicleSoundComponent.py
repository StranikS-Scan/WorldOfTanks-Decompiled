# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSVehicleSoundComponent.py
import BigWorld
import SoundGroups
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from last_stand_common.last_stand_constants import PLAYERS_TEAM
from last_stand.gui.sounds import ComponentsHolder
from last_stand.gui.sounds.vehicle_components import LSCommonEnemySounds, LSLootSounds
from last_stand.gui.sounds.sound_constants import VEHICLE_OBJ_NAME_PATTERN
from skeletons.gui.battle_session import IBattleSessionProvider
_VEHICLE_SOUND_COMPONENTS = [(LSCommonEnemySounds, lambda parent: parent.isEnemy), (LSLootSounds, lambda parent: not parent.isEnemy)]

class LSVehicleSoundComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LSVehicleSoundComponent, self).__init__()
        self._components = ComponentsHolder([], self)
        self._soundObject = SoundGroups.g_instance.WWgetSoundObject(VEHICLE_OBJ_NAME_PATTERN.format(self.entity.id), self.entity.matrix)

    def onDestroy(self):
        self._components.onDestroy()
        self.soundObject.stopAll()
        player = BigWorld.player()
        if player is not None:
            player.arena.onVehicleKilled -= self._onVehicleKilled
        super(LSVehicleSoundComponent, self).onDestroy()
        return

    @property
    def soundObject(self):
        return self._soundObject

    @property
    def isEnemy(self):
        return self.sessionProvider.getArenaDP().getVehicleInfo(self.entity.id).team != PLAYERS_TEAM

    @property
    def soulsContainer(self):
        return self.entity.dynamicComponents.get('lsSoulsContainer')

    @property
    def lsBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def onLootFailed(self, lootID, vehicleIDs):
        self._components.call('onLootFailed', lootID, vehicleIDs)

    def onLootSucceed(self, lootID, vehicleIDs):
        self._components.call('onLootSucceed', lootID, vehicleIDs)

    def _onAvatarReady(self):
        componentList = [ component for component, condition in _VEHICLE_SOUND_COMPONENTS if condition(self) ]
        self._components.addComponents(componentList)
        self._components.onAvatarReady()
        player = BigWorld.player()
        if player is not None:
            player.arena.onVehicleKilled += self._onVehicleKilled
        return

    def _onVehicleKilled(self, victimID, *args):
        if self.entity.id == victimID:
            self.soundObject.stopAll()
        self._components.call('onVehicleKilled', victimID, *args)
