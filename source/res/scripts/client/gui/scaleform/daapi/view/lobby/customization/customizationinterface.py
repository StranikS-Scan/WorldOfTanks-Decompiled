# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/CustomizationInterface.py
import Event
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class CustomizationInterface(BaseDAAPIModule):
    _eventManager = Event.EventManager()
    onDataInited = Event.Event(_eventManager)
    onCustomizationChangeSuccess = Event.Event(_eventManager)
    onCustomizationChangeFailed = Event.Event(_eventManager)
    onCustomizationDropSuccess = Event.Event(_eventManager)
    onCustomizationDropFailed = Event.Event(_eventManager)
    onCurrentItemChange = Event.Event(_eventManager)

    def __init__(self, name, nationId, type, position = -1):
        super(CustomizationInterface, self).__init__()
        self._name = name
        self._position = position
        self._positionShift = 0
        self.isTurret = False
        self._nationID = nationId
        self._type = type

    def fetchCurrentItem(self, vehDescr):
        pass

    def invalidateData(self, vehType, refresh = False):
        pass

    def isNewItemSelected(self):
        return False

    def getNewItems(self):
        return None

    def isNewItemIGR(self):
        return False

    def getSelectedItemCost(self):
        return (-1, 0)

    def getSelectedItemsCount(self, *args):
        return int(self.isNewItemSelected())

    def getItemCost(self, itemId, priceIndex):
        return (-1, 0)

    def isCurrentItemRemove(self):
        return True

    def getCurrentItemRemoveStr(self):
        return None

    def isEnabled(self):
        return True

    def change(self, vehInvID, section, showMessage):
        self.onCustomizationChangeFailed('Section {0:>s} is not implemented'.format(self._name))

    def drop(self, vehInvID, kind):
        self.onCustomizationDropFailed('Section {0:>s} is not implemented'.format(self._name))

    def update(self, vehicleDescr):
        pass
