# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/event_boards/__init__.py
from skeletons.gui.event_boards_controllers import IEventBoardController
__all__ = ('getEventServicesConfig',)

def getEventServicesConfig(manager):
    """ Configures services for package clans.
    :param manager: helpers.dependency.DependencyManager
    """
    from gui.event_boards.event_boards_controller import EventBoardsController
    ctrl = EventBoardsController()
    manager.addInstance(IEventBoardController, ctrl)
