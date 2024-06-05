# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/controllers/repository.py
from gui.battle_control.controllers import _ControllersRepository, debug_ctrl, SharedControllersRepository
from gui.battle_control.controllers.battle_hints import controller as battle_hints_ctrl
from gui.battle_control.controllers.sound_ctrls.vehicle_hit_sound_ctrl import VehicleHitSound
from gui.battle_control.controllers.vse_hud_settings_ctrl import vse_hud_settings_ctrl
from story_mode.gui.battle_control.controllers.appearance_cache_controller import AppearanceCacheController
from story_mode.gui.battle_control.controllers.messages_controller import StoryModeBattleMessagesPlayer, StoryModeBattleMessagesController
from story_mode.gui.battle_control.controllers.settings_contoller import OverrideSettingsController

class StoryModeRepository(_ControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(StoryModeRepository, cls).create(setup)
        repository.addArenaController(AppearanceCacheController(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addController(VehicleHitSound())
        repository.addViewController(battle_hints_ctrl.BattleHintsController(), setup)
        repository.addController(vse_hud_settings_ctrl.VSEHUDSettingsController())
        return repository


class OnboardingRepository(StoryModeRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(OnboardingRepository, cls).create(setup)
        repository.addArenaController(OverrideSettingsController(), setup)
        return repository


class StoryModeSharedRepository(SharedControllersRepository):
    __slots__ = ()

    @classmethod
    def getMessagesController(cls, setup):
        return StoryModeBattleMessagesPlayer(setup) if setup.isReplayPlaying else StoryModeBattleMessagesController(setup)

    @classmethod
    def getAreaMarkersController(cls):
        from story_mode.gui.battle_control.controllers.area_marker_ctrl import StoryModeAreaMarkersController
        return StoryModeAreaMarkersController()
