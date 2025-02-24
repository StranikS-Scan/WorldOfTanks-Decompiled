# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/battle_control/controllers/repository.py
from fun_random.gui.battle_control.controllers.sound_ctrls.fun_random_battle_sounds import createFunRandomBattleSoundsController
from gui.battle_control.controllers.repositories import ClassicControllersRepository
from gui.battle_control.controllers.progress_circle_ctrl import ProgressTimerController

class FunRandomControllerRepository(ClassicControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(FunRandomControllerRepository, cls).create(setup)
        repository.addController(ProgressTimerController(setup))
        repository.addController(createFunRandomBattleSoundsController(setup))
        return repository
