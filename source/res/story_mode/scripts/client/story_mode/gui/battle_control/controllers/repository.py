# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/repository.py
from gui.battle_control.controllers import _ControllersRepository, debug_ctrl
from gui.battle_control.controllers.battle_hints import controller as battle_hints_ctrl
from gui.battle_control.controllers.sound_ctrls.vehicle_hit_sound_ctrl import VehicleHitSound
from story_mode.gui.battle_control.controllers.appearance_cache_controller import AppearanceCacheController
from story_mode.gui.battle_control.controllers.settings_contoller import OverrideSettingsController

class StoryModeRepository(_ControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(StoryModeRepository, cls).create(setup)
        repository.addArenaController(AppearanceCacheController(setup), setup)
        repository.addArenaController(OverrideSettingsController(), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addController(VehicleHitSound())
        repository.addViewController(battle_hints_ctrl.BattleHintsController(), setup)
        return repository
