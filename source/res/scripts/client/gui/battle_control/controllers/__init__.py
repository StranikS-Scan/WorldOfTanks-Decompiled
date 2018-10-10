# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/__init__.py
from gui.battle_control.controllers.repositories import BattleSessionSetup
from gui.battle_control.controllers.repositories import SharedControllersLocator
from gui.battle_control.controllers.repositories import DynamicControllersLocator
from gui.battle_control.controllers.repositories import ClassicControllersRepository
from gui.battle_control.controllers.repositories import EpicControllersRepository
from gui.battle_control.controllers.repositories import SharedControllersRepository
__all__ = ('createShared', 'createDynamic', 'BattleSessionSetup', 'SharedControllersLocator', 'DynamicControllersLocator')

def createShared(setup):
    return SharedControllersLocator(SharedControllersRepository.create(setup))


def createDynamic(setup):
    guiVisitor = setup.arenaVisitor.gui
    if guiVisitor.isInEpicRange():
        repository = EpicControllersRepository.create(setup)
    elif not guiVisitor.isTutorialBattle():
        repository = ClassicControllersRepository.create(setup)
    else:
        repository = None
    return DynamicControllersLocator(repository=repository)
