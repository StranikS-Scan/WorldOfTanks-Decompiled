# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBVehicleIncendiaryShotComponent.py
from HBSpecialShotComponent import HBSpecialShotComponent
from gui.battle_control import avatar_getter
from historical_battles.gui.sounds.sound_constants import HBGameplayVoiceovers

class HBVehicleIncendiaryShotComponent(HBSpecialShotComponent):

    def set_targetOnFireTime(self, _):
        if self.targetOnFireTime > 0:
            avatar_getter.getSoundNotifications().play(HBGameplayVoiceovers.ABILITY_INCENDIARY_SHOT_HB)
