# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/battle_control/controllers/repositories.py
from gui.battle_control.controllers.repositories import ClassicControllersRepository
from historical_battles.gui.shared import battle_hints
from historical_battles.gui.battle_control.controllers.appearance_cache_controller import HBAppearanceCacheController
from historical_battles.gui.sounds.sound_battle_controller import HBBattleSoundRemappingController

class HBControllersRepository(ClassicControllersRepository):

    @classmethod
    def create(cls, setup):
        repository = super(HBControllersRepository, cls).create(setup)
        repository.addViewController(battle_hints.createBattleHintsController(), setup)
        repository.addController(HBBattleSoundRemappingController())
        return repository

    @staticmethod
    def _getAppearanceCacheController(setup):
        return HBAppearanceCacheController(setup)
