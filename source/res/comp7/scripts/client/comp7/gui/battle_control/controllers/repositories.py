# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_control/controllers/repositories.py
from comp7_core.gui.battle_control.controllers.appearance_cache_ctrls.comp7_appearance_cache_ctrl import Comp7AppearanceCacheController
from comp7_core.gui.battle_control.controllers.comp7_voip_ctrl import Comp7VOIPController
from comp7_core.gui.battle_control.controllers.sound_ctrls.comp7_battle_sounds import Comp7BattleSoundController
from gui.battle_control.controllers.prebattle_setup_ctrl import PrebattleSetupController
from gui.battle_control.controllers.repositories import ClassicControllersRepository
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7ControllerRepository(ClassicControllersRepository):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @classmethod
    def create(cls, setup):
        repository = super(Comp7ControllerRepository, cls).create(setup)
        settings = cls.__comp7Controller.getModeSettings()
        isTeamChannelAvailable = settings.createVivoxTeamChannels if settings is not None else False
        repository.addArenaController(Comp7VOIPController(isTeamChannelAvailable), setup)
        repository.addController(Comp7BattleSoundController())
        repository.addArenaViewController(PrebattleSetupController(setup), setup)
        return repository

    @staticmethod
    def _getAppearanceCacheController(setup):
        return Comp7AppearanceCacheController(setup)
