# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/customization/CustomizationInterface.py
# Compiled at: 2011-12-20 18:23:08
import Event
from gui.Scaleform.windows import UIInterface

class CustomizationInterface(UIInterface):
    _eventManager = Event.EventManager()
    onDataInited = Event.Event(_eventManager)
    onCustomizationChangeSuccess = Event.Event(_eventManager)
    onCustomizationChangeFailed = Event.Event(_eventManager)
    onCustomizationDropSuccess = Event.Event(_eventManager)
    onCustomizationDropFailed = Event.Event(_eventManager)

    def __init__(self, name):
        super(CustomizationInterface, self).__init__()
        self._name = name

    def fetchCurrentItem(self, vehDescr):
        pass

    def invalidateData(self, vehType, refresh=False):
        pass

    def isNewItemSelected(self):
        return False

    def getSelectedItemCost(self):
        pass

    def isCurrentItemRemove(self):
        return True

    def change(self, vehInvID):
        self.onCustomizationChangeFailed('Section {0:>s} is not implemented'.format(self._name))

    def drop(self, vehInvID):
        self.onCustomizationDropFailed('Section {0:>s} is not implemented'.format(self._name))

    def update(self, vehicleDescr):
        pass
