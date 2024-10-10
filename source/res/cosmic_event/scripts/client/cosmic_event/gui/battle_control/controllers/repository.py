# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/battle_control/controllers/repository.py
from cosmic_event.gui.battle_control.controllers.consumables.equipment_ctrl import CosmicEquipmentsController
from cosmic_event.gui.battle_control.controllers.consumables.equipment_key_binder import EquipmentKeyBinder
from cosmic_event.gui.battle_control.controllers.cosmic_hints_ctrl import CosmicBattleHintsController
from cosmic_event.gui.battle_control.controllers.ingame_help_ctrl import CosmicIngameHelpController
from gui.battle_control.controllers import arena_load_ctrl, consumables, feedback_adaptor, msgs_ctrl, period_ctrl, vehicle_state_ctrl, view_points_ctrl, anonymizer_fakes_ctrl, prebattle_setups_ctrl, debug_ctrl
from gui.battle_control.controllers.appearance_cache_ctrls.default_appearance_cache_ctrl import DefaultAppearanceCacheController
from gui.battle_control.controllers.repositories import SharedControllersRepository, _ControllersRepositoryByBonuses
from gui.battle_control.controllers.sound_ctrls.vehicle_hit_sound_ctrl import VehicleHitSound

class CosmicSharedControllersRepository(SharedControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = cls()
        from gui.battle_control.controllers import crosshair_proxy
        repository.addController(crosshair_proxy.CrosshairDataProxy())
        repository.addController(CosmicEquipmentsController(setup))
        repository.addController(consumables.createOptDevicesCtrl(setup))
        ammo = consumables.createAmmoCtrl(setup)
        ammo.setViewComponents(EquipmentKeyBinder())
        repository.addViewController(ammo, setup)
        repository.addController(vehicle_state_ctrl.createCtrl(setup))
        repository.addController(feedback_adaptor.createFeedbackAdaptor(setup))
        repository.addController(msgs_ctrl.createBattleMessagesCtrl(setup))
        repository.addArenaController(view_points_ctrl.ViewPointsController(setup), setup)
        repository.addArenaController(anonymizer_fakes_ctrl.AnonymizerFakesController(setup), setup)
        repository.addArenaViewController(prebattle_setups_ctrl.PrebattleSetupsController(), setup)
        repository.addArenaViewController(arena_load_ctrl.createArenaLoadController(setup), setup)
        repository.addArenaViewController(period_ctrl.createPeriodCtrl(setup), setup)
        from gui.battle_control.controllers import area_marker_ctrl
        repository.addArenaController(area_marker_ctrl.AreaMarkersController(), setup)
        repository.addController(CosmicIngameHelpController(setup))
        return repository


class CosmicDynamicControllersRepository(_ControllersRepositoryByBonuses):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(CosmicDynamicControllersRepository, cls).create(setup)
        repository.addViewController(debug_ctrl.DebugController(), setup)
        repository.addArenaController(DefaultAppearanceCacheController(setup), setup)
        repository.addViewController(CosmicBattleHintsController(), setup)
        repository.addController(VehicleHitSound())
        return repository
