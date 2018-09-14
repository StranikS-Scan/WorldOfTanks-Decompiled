# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/login/__init__.py
from gui import GUI_SETTINGS
from skeletons.gui.login_manager import ILoginManager
__all__ = ('getLoginManagerConfig',)

def getLoginManagerConfig(manager):
    """ Configures services for package login.
    :param manager: instance of dependency manager.
    :return: instance of dependency manager.
    """
    if GUI_SETTINGS.socialNetworkLogin['enabled']:
        from social_networks import Manager, SOCIAL_NETWORKS
        instance = Manager()
    else:
        from Manager import Manager
        instance = Manager()
    instance.init()
    manager.bindInstance(ILoginManager, instance, finalizer='fini')
