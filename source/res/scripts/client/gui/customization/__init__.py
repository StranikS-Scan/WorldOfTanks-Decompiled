# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/__init__.py
from skeletons.gui.customization import ICustomizationService
__all__ = ('getCustomizationServiceConfig',)

def getCustomizationServiceConfig(manager):
    from gui.customization.service import CustomizationService

    def _create():
        instance = CustomizationService()
        instance.init()
        return instance

    manager.addRuntime(ICustomizationService, _create, finalizer='fini')
