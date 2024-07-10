# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/battle_control/controllers/repositories.py
from frontline.gui.battle_control.controllers.appearance_cache_ctrls.frontline_appearance_cache_ctrl import FLAppearanceCacheController
from gui.battle_control.controllers import battle_field_ctrl, debug_ctrl, dyn_squad_functional, epic_respawn_ctrl, progress_circle_ctrl, epic_maps_ctrl, epic_missions_ctrl, game_notification_ctrl, epic_team_bases_ctrl, perk_ctrl
from gui.battle_control.controllers.battle_hints import controller as battle_hints_ctrl
from gui.battle_control.controllers.repositories import _ControllersRepository, registerBattleControllerRepo
from gui.battle_control.controllers.sound_ctrls.epic_battle_sounds import EpicShotsResultSoundsController
from constants import ARENA_GUI_TYPE

class FLControllersRepository(_ControllersRepository):
    __slots__ = ()

    @staticmethod
    def _getAppearanceCacheController(setup):
        return FLAppearanceCacheController(setup)

    @classmethod
    def create(cls, setup):
        repository = super(FLControllersRepository, cls).create(setup)
        repository.addViewController(epic_respawn_ctrl.EpicRespawnsController(setup), setup)
        repository.addController(progress_circle_ctrl.ProgressTimerController(setup))
        repository.addViewController(epic_maps_ctrl.EpicMapsController(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(perk_ctrl.PerksController(), setup)
        repository.addArenaController(dyn_squad_functional.DynSquadFunctional(setup), setup)
        repository.addViewController(game_notification_ctrl.EpicGameNotificationsController(setup), setup)
        repository.addViewController(epic_missions_ctrl.EpicMissionsController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addArenaViewController(epic_team_bases_ctrl.createEpicTeamsBasesCtrl(setup), setup)
        repository.addArenaController(cls._getAppearanceCacheController(setup), setup)
        repository.addController(EpicShotsResultSoundsController())
        repository.addViewController(battle_hints_ctrl.BattleHintsController(), setup)
        return repository


def registerFLBattleRepositories():
    for guiType in ARENA_GUI_TYPE.EPIC_RANGE:
        registerBattleControllerRepo(guiType, FLControllersRepository)
