# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_control/controllers/repository.py
from gui.battle_control.controllers.repositories import ClassicControllersRepository, registerBattleControllerRepo
from portal_constants import ARENA_GUI_TYPE
from portal.sounds.sound_battle_controller import createPortalBattleSoundsController
from portal.gui.shared import battle_hints
from portal.gui.battle_control.controllers.markers.portal_markers_ctrl import createPortalMarkersController
from portal.gui.battle_control.controllers.effects.effects_controller import createPortalEffectsController

class PortalControllerRepository(ClassicControllersRepository):
    __slots__ = ()

    @classmethod
    def create(cls, setup):
        repository = super(PortalControllerRepository, cls).create(setup)
        repository.addController(createPortalBattleSoundsController(setup))
        repository.addController(createPortalMarkersController(setup))
        repository.addController(createPortalEffectsController(setup))
        repository.addViewController(battle_hints.createBattleHintsController(), setup)
        return repository


def registerPortalBattleRepo():
    registerBattleControllerRepo(ARENA_GUI_TYPE.PORTAL, PortalControllerRepository)
