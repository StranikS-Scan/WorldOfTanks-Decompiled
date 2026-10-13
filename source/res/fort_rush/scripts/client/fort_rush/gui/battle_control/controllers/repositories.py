# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_control/controllers/repositories.py
from __future__ import absolute_import
from fort_rush.gui.battle_control.controllers import respawn_ctrl
from fort_rush.gui.battle_control.controllers.spectator_ctrl import FortRushSpectatorViewController
from gui.battle_control.controllers.repositories import SharedControllersRepository, ClassicControllersRepository
from gui.battle_control.controllers.spectator_ctrl import SpectatorViewController

class FortRushControllerRepository(ClassicControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(FortRushControllerRepository, cls).create(setup)
        repository.addViewController(respawn_ctrl.FortRushRespawnViewController(), setup)
        return repository


class FortRushSharedControllersRepository(SharedControllersRepository):
    __slots__ = ()

    def addViewController(self, ctrl, setup):
        if isinstance(ctrl, SpectatorViewController):
            ctrl = FortRushSpectatorViewController()
        super(FortRushSharedControllersRepository, self).addViewController(ctrl, setup)
