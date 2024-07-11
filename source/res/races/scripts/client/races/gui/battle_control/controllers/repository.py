# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/battle_control/controllers/repository.py
from races.gui.battle_control.controllers.consumables.equipment_ctrl import RacesEquipmentsController
from races.gui.battle_control.controllers.consumables.equipment_key_binder import EquipmentKeyBinder
from gui.battle_control.controllers import arena_load_ctrl, consumables, feedback_adaptor, msgs_ctrl, period_ctrl, vehicle_state_ctrl, view_points_ctrl, anonymizer_fakes_ctrl, prebattle_setups_ctrl
from gui.battle_control.controllers.repositories import SharedControllersRepository
from races.gui.battle_control.controllers.races_sound_controller import RacesSoundController
from races.gui.battle_control.controllers.races_help_controller import RacesHelpController

class RacesSharedControllersRepository(SharedControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = cls()
        from gui.battle_control.controllers import crosshair_proxy
        repository.addController(crosshair_proxy.CrosshairDataProxy())
        repository.addController(RacesEquipmentsController(setup))
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
        repository.addController(RacesSoundController())
        repository.addController(RacesHelpController(setup))
        return repository
