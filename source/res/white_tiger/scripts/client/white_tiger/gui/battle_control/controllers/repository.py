# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/repository.py
from gui.battle_control.controllers import battle_field_ctrl, debug_ctrl, team_bases_ctrl, default_maps_ctrl, perk_ctrl, arena_info_ctrl, players_panel_ctrl, boss_info_ctrl, teleport_spawn_ctrl
from gui.battle_control.controllers.appearance_cache_ctrls.event_appearance_cache_ctrl import EventAppearanceCacheController
from gui.battle_control.controllers.repositories import _ControllersRepositoryByBonuses
from white_tiger.gui.battle_control.controllers.sound_ctrl.vehicle_hit_sound_ctrl import WTVehicleHitSound

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
        repository.addArenaViewController(boss_info_ctrl.BossInfoController(), setup)
        repository.addArenaController(arena_info_ctrl.ArenaInfoController(), setup)
        repository.addViewController(teleport_spawn_ctrl.TeleportSpawnController(), setup)
        repository.addViewController(battle_hints_event.createWTBattleHintsController(), setup)
        repository.addArenaController(EventAppearanceCacheController(setup), setup)
        repository.addController(WTVehicleHitSound())
        from gui.battle_control.controllers import area_marker_ctrl
        repository.addArenaController(area_marker_ctrl.AreaMarkersController(), setup)
        repository.addArenaViewController(players_panel_ctrl.PlayersPanelController(), setup)
        return repository
