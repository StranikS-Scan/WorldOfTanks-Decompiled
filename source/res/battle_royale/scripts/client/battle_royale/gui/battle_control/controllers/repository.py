# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/controllers/repository.py
from battle_royale.gui.battle_control.controllers.battle_royale_voip_ctrl import BRVOIPController
from battle_royale.gui.battle_control.controllers.notification_manager import NotificationManager
from gui.battle_control.controllers import battle_field_ctrl, debug_ctrl, default_maps_ctrl, perk_ctrl
from gui.battle_control.controllers.battle_hints import controller as battle_hints_ctrl
from gui.battle_control.controllers.repositories import _ControllersRepository, registerBattleControllerRepo
from gui.battle_control.controllers.sound_ctrls.vehicle_hit_sound_ctrl import VehicleHitSound
from battle_royale.gui.battle_control.controllers import spawn_ctrl, vehicles_count_ctrl, radar_ctrl, progression_ctrl, death_ctrl
from battle_royale.gui.battle_control.controllers.battle_royale_appearance_cache_ctrl import BattleRoyaleAppearanceCacheController
from constants import ARENA_GUI_TYPE

class BattleRoyaleControllersRepository(_ControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(BattleRoyaleControllersRepository, cls).create(setup)
        notificationManager = NotificationManager()
        repository.addArenaViewController(progression_ctrl.ProgressionController(notificationManager), setup)
        repository.addArenaViewController(battle_field_ctrl.BattleFieldCtrl(), setup)
        repository.addViewController(battle_hints_ctrl.BattleHintsController(), setup)
        repository.addViewController(perk_ctrl.PerksController(), setup)
        repository.addViewController(spawn_ctrl.SpawnController(notificationManager), setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addArenaViewController(vehicles_count_ctrl.VehicleCountController(), setup)
        repository.addViewController(default_maps_ctrl.DefaultMapsController(setup), setup)
        repository.addArenaController(BattleRoyaleAppearanceCacheController(setup), setup)
        repository.addArenaController(death_ctrl.DeathScreenController(), setup)
        repository.addController(VehicleHitSound())
        repository.addArenaController(BRVOIPController(), setup)
        if setup.isReplayPlaying:
            radarCtrl = radar_ctrl.RadarReplayController()
        else:
            radarCtrl = radar_ctrl.RadarController()
        repository.addViewController(radarCtrl, setup)
        return repository


def registerBRBattleRepo():
    registerBattleControllerRepo(ARENA_GUI_TYPE.BATTLE_ROYALE, BattleRoyaleControllersRepository)
