# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/dependency/registrator.py
import typing
if typing.TYPE_CHECKING:
    from dependency_injection_container import DependencyManager

def registerSkeletons(manager):
    from museum_of_glory.skeletons.game_control import IMuseumOfGloryController
    from museum_of_glory.gui.game_control.museum_of_glory_controller import MuseumOfGloryController
    manager.addInstance(IMuseumOfGloryController, MuseumOfGloryController())


def registerMuseumOfGloryPersonality():
    from gui.shared.system_factory import registerGameControllers
    from museum_of_glory.skeletons.game_control import IMuseumOfGloryController
    from museum_of_glory.gui.game_control.museum_of_glory_controller import MuseumOfGloryController
    registerGameControllers([(IMuseumOfGloryController, MuseumOfGloryController, False)])
