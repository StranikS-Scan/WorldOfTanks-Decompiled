# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/new_year_binder.py
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager, INewYearController
from PlayerEvents import g_playerEvents

class NewYearBinder(object):

    @staticmethod
    def start():
        g_playerEvents.onAccountShowGUI += NewYearBinder.__onEstablishBinding

    @staticmethod
    def stop():
        NewYearBinder.__onDestroyBinding()
        g_playerEvents.onAccountShowGUI -= NewYearBinder.__onEstablishBinding

    @staticmethod
    def __onEstablishBinding(_):
        g_playerEvents.onAccountShowGUI -= NewYearBinder.__onEstablishBinding
        newYearController = dependency.instance(INewYearController)
        customizableObjectsMgr = dependency.instance(ICustomizableObjectsManager)
        newYearController.onSlotUpdated += customizableObjectsMgr.updateSlot
        g_playerEvents.onAccountBecomeNonPlayer += NewYearBinder.__onDestroyBinding

    @staticmethod
    def __onDestroyBinding():
        g_playerEvents.onAccountBecomeNonPlayer -= NewYearBinder.__onDestroyBinding
        newYearController = dependency.instance(INewYearController)
        customizableObjectsMgr = dependency.instance(ICustomizableObjectsManager)
        newYearController.onSlotUpdated -= customizableObjectsMgr.updateSlot
        g_playerEvents.onAccountShowGUI += NewYearBinder.__onEstablishBinding
