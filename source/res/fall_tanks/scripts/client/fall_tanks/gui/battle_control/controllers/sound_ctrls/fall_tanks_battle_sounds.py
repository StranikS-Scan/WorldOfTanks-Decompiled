# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/controllers/sound_ctrls/fall_tanks_battle_sounds.py
import typing
import BattleReplay
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayersBattleController
from fun_random.gui.battle_control.controllers.sound_ctrls.fun_random_battle_sounds import FunRandomBattleSoundController, FunRandomBattleReplaySoundController
from fall_tanks.gui.battle_control.controllers.sound_ctrls.race_music_sound_player import RaceMusicSoundPlayer
from fall_tanks.gui.battle_control.controllers.sound_ctrls.vehicle_frags_sound_player import VehicleFragsSoundPlayer
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers import BattleSessionSetup
    from gui.battle_control.controllers.sound_ctrls.common import SoundPlayer

class FallTanksBattleSoundController(FunRandomBattleSoundController):

    def _initializeSoundPlayers(self):
        return (RaceMusicSoundPlayer(), VehicleFragsSoundPlayer())


class FallTanksBattleReplaySoundController(FunRandomBattleReplaySoundController):

    def _initializeSoundPlayers(self):
        return (RaceMusicSoundPlayer(), VehicleFragsSoundPlayer())


def createFallTanksBattleSoundsController(setup):
    return FallTanksBattleReplaySoundController(setup) if BattleReplay.g_replayCtrl.isPlaying else FallTanksBattleSoundController(setup)
