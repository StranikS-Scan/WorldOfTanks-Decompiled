# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clubs/__init__.py
from skeletons.gui.clubs import IClubsController
__all__ = ('getClubsServicesConfig',)

def getClubsServicesConfig(manager):
    """ Configures services for package clubs.
    :param manager: helpers.dependency.DependencyManager
    """
    from gui.clubs.ClubsController import ClubsController
    ctrl = ClubsController()
    ctrl.init()
    manager.bindInstance(IClubsController, ctrl, finalizer='fini')
