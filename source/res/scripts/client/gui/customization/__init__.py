# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/__init__.py
from gui.customization.service import CustomizationService
from skeletons.gui.customization import ICustomizationService
__all__ = ('getCustomizationServiceConfig',)

def getCustomizationServiceConfig(manager):
    """ Configures services for customization package.
    :param manager: helpers.dependency.DependencyManager
    """
    instance = CustomizationService()
    instance.init()
    manager.addInstance(ICustomizationService, instance, finalizer='fini')
