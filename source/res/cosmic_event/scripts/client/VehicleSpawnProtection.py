# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/VehicleSpawnProtection.py
import logging
from cosmic_sound import CosmicBattleSounds
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class VehicleSpawnProtection(DynamicScriptComponent):

    def __init__(self, *_, **__):
        super(VehicleSpawnProtection, self).__init__(*_, **__)
        from gui.battle_control import avatar_getter
        if self.entity.id == avatar_getter.getPlayerVehicleID():
            CosmicBattleSounds.Abilities.playRespawnProtectionActivated()

    def onDestroy(self):
        from gui.battle_control import avatar_getter
        if self.entity.id == avatar_getter.getPlayerVehicleID():
            CosmicBattleSounds.Abilities.playRespawnProtectionElapsed()
        super(VehicleSpawnProtection, self).onDestroy()
