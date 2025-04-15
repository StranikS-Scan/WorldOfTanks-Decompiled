# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/repository.py
from gui.battle_control.controllers.repositories import SharedControllersRepository, ClassicControllersRepository
from gui.battle_control.controllers.vse_hud_settings_ctrl import vse_hud_settings_ctrl
from fall_tanks.gui.battle_control.controllers import consumables
from fall_tanks.gui.battle_control.controllers.fall_tanks_battle_ctrl import createFallTanksBattleController
from fall_tanks.gui.battle_control.controllers.sound_ctrls.fall_tanks_battle_sounds import createFallTanksBattleSoundsController

class FallTanksSharedControllersRepository(SharedControllersRepository):
    __slots__ = ()

    @classmethod
    def getOptionalDevicesController(cls, setup):
        return consumables.createOptDevicesCtrl(setup)


class FallTanksControllersRepository(ClassicControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(FallTanksControllersRepository, cls).create(setup)
        repository.addArenaController(createFallTanksBattleController(), setup)
        repository.addController(vse_hud_settings_ctrl.VSEHUDSettingsController())
        repository.addController(createFallTanksBattleSoundsController(setup))
        return repository
