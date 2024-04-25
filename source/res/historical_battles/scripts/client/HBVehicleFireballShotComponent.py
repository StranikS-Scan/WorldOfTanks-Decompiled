# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehicleFireballShotComponent.py
import BigWorld
from gui.battle_control import avatar_getter
from historical_battles.gui.sounds.sound_constants import HBGameplayVoiceovers

class HBVehicleFireballShotComponent(BigWorld.DynamicScriptComponent):

    def set_targetOnFireTime(self, _):
        avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.ABILITY_INCENDIARY_SHOT)
