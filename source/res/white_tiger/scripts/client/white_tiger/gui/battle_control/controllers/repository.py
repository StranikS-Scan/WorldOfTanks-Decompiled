# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/repository.py
from gui.battle_control.controllers import battle_field_ctrl, debug_ctrl, team_bases_ctrl, default_maps_ctrl, perk_ctrl
from gui.battle_control.controllers.appearance_cache_ctrls.event_appearance_cache_ctrl import EventAppearanceCacheController
from gui.battle_control.controllers.repositories import _ControllersRepositoryByBonuses
from white_tiger.gui.battle_control.controllers.wt_battle_effects_ctrl import WTBattleEffectsCtrl
from white_tiger.gui.battle_control.controllers.wt_boss_info_ctrl import WTBossInfoController
from white_tiger.gui.battle_control.controllers import wt_arena_info_ctrl, wt_players_panel_ctrl, wt_teleport_spawn_ctrl, wt_ability_ctrl

class WhiteTigerControllerRepository(_ControllersRepositoryByBonuses):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger import battle_hints_event
        repository = super(WhiteTigerControllerRepository, cls).create(setup)
        repository.addArenaViewController(team_bases_ctrl.createTeamsBasesCtrl(setup), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addViewController(default_maps_ctrl.DefaultMapsController(setup), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addViewController(perk_ctrl.PerksController(), setup)
        repository.addArenaViewController(WTBossInfoController(), setup)
        repository.addArenaController(wt_arena_info_ctrl.WTArenaInfoController(), setup)
        repository.addViewController(wt_teleport_spawn_ctrl.WTTeleportSpawnController(), setup)
        repository.addViewController(wt_ability_ctrl.WTAbilityController(), setup)
        repository.addViewController(battle_hints_event.createWTBattleHintsController(), setup)
        repository.addArenaController(EventAppearanceCacheController(setup), setup)
        from gui.battle_control.controllers import area_marker_ctrl
        repository.addArenaController(area_marker_ctrl.AreaMarkersController(), setup)
        repository.addArenaViewController(wt_players_panel_ctrl.WTPlayersPanelController(), setup)
        repository.addController(WTBattleEffectsCtrl())
        return repository
