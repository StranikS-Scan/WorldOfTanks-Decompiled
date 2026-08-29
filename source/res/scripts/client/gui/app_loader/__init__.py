# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/__init__.py
from gui.app_loader import settings, decorators
from gui.app_loader.decorators import app_getter, def_lobby, def_battle, sf_lobby, sf_battle
__all__ = ('getAppLoaderConfig', 'decorators', 'settings', 'app_getter', 'def_lobby', 'def_battle', 'sf_lobby', 'sf_battle')

def getAppLoaderConfig(manager):
    from gui.app_loader.loader import AppLoader
    from skeletons.gui.app_loader import IAppLoader
    manager.addInstance(IAppLoader, AppLoader(), finalizer='fini')
