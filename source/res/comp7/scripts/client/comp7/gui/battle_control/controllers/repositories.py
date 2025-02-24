# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_control/controllers/repositories.py
from comp7.gui.battle_control.controllers.appearance_cache_ctrls.comp7_appearance_cache_ctrl import Comp7AppearanceCacheController
from comp7.gui.battle_control.controllers.comp7_voip_ctrl import Comp7VOIPController
from comp7.gui.battle_control.controllers.sound_ctrls.comp7_battle_sounds import Comp7BattleSoundController
from gui.battle_control.controllers.prebattle_setup_ctrl import PrebattleSetupController
from gui.battle_control.controllers.repositories import ClassicControllersRepository

class Comp7ControllerRepository(ClassicControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(Comp7ControllerRepository, cls).create(setup)
        repository.addArenaController(Comp7VOIPController(), setup)
        repository.addController(Comp7BattleSoundController())
        repository.addArenaViewController(PrebattleSetupController(setup), setup)
        return repository

    @staticmethod
    def _getAppearanceCacheController(setup):
        return Comp7AppearanceCacheController(setup)
