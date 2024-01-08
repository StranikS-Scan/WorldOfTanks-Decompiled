# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/base.py
import typing
import Event
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
from gui.shared.utils import decorators
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class InteractingItem(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__item', 'onItemUpdated', 'onSlotAction', 'onAcceptComplete')

    def __init__(self, item):
        self.__item = item
        self.onItemUpdated = Event.Event()
        self.onSlotAction = Event.Event()
        self.onAcceptComplete = Event.Event()

    def setItem(self, item):
        self.__item = item

    def getItem(self):
        return self.__item

    def clear(self):
        self.__item = None
        self.onItemUpdated.clear()
        self.onSlotAction.clear()
        self.onAcceptComplete.clear()
        return


class BaseAutoRenewal(object):
    __slots__ = ('_vehicle', '_value')

    def __init__(self, vehicle):
        self._vehicle = vehicle
        self._value = None
        return

    def getValue(self):
        raise NotImplementedError

    def getLocalValue(self):
        return self.getValue() if self._value is None else self._value

    def setLocalValue(self, value):
        self._value = value

    def changeValue(self, callback):
        value = self.getLocalValue()
        if value != self.getValue():
            self.processVehicleAutoRenewal(callback)
        else:
            callback(None)
        return

    def updateVehicle(self, vehicle):
        self._vehicle = vehicle

    @decorators.adisp_process('techMaintenance')
    def processVehicleAutoRenewal(self, callback):
        raise NotImplementedError


class BaseInteractor(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_item', '__autoRenewal')

    def __init__(self, item):
        self._item = None
        self.__autoRenewal = None
        self.setItem(item)
        self.__createAutoRenewal()
        return

    def getName(self):
        return None

    def getAutoRenewal(self):
        return self.__autoRenewal

    def getVehicleAfterInstall(self):
        currentVehicle = self.getItem()
        vehicle = self._itemsCache.items.getVehicleCopy(currentVehicle)
        return vehicle

    def getItem(self):
        return self._item.getItem()

    def setItem(self, item):
        self._item = item
        if self.__autoRenewal is not None:
            self.__autoRenewal.updateVehicle(self.getItem())
        return

    def getInstalledLayout(self):
        raise NotImplementedError

    def getCurrentLayout(self):
        raise NotImplementedError

    def getSetupLayout(self):
        raise NotImplementedError

    def getPlayerLayout(self):
        return self.getInstalledLayout()

    def hasChanged(self):
        return self.getInstalledLayout() != self.getCurrentLayout()

    def isPlayerLayout(self):
        return self.getPlayerLayout() == self.getCurrentLayout()

    def itemUpdated(self):
        self._item.onItemUpdated(self.getName())

    def onSlotAction(self, actionType, intCD=NONE_ID, slotID=NONE_ID, leftID=NONE_ID, rightID=NONE_ID, leftIntCD=NONE_ID, rightIntCD=NONE_ID):
        self._item.onSlotAction(self.getName(), actionType, intCD, slotID, leftID, rightID, leftIntCD, rightIntCD)

    def onAcceptComplete(self):
        self._item.onAcceptComplete()

    def revert(self):
        pass

    def confirm(self, skipDialog=False):
        pass

    def clear(self):
        self._item = None
        return

    def updateFrom(self, vehicle, onlyInstalled):
        pass

    def getChangedList(self):
        setOfPrevLayout = set((item.intCD for item in self.getInstalledLayout() if item is not None))
        currentItems = []
        for item in self.getCurrentLayout():
            if item and item.intCD not in setOfPrevLayout:
                currentItems.append(item)

        return currentItems

    def showExitConfirmDialog(self):
        pass

    def applyAutoRenewal(self, callback):
        autoRenewal = self.getAutoRenewal()
        if autoRenewal is not None and autoRenewal.getValue() != autoRenewal.getLocalValue():
            autoRenewal.changeValue(callback)
        else:
            callback(None)
        return

    def applyQuit(self, callback, skipApplyAutoRenewal):
        if skipApplyAutoRenewal:
            callback(None)
        else:
            self.applyAutoRenewal(callback)
        return

    def _createAutoRenewal(self):
        return None

    def __createAutoRenewal(self):
        self.__autoRenewal = self._createAutoRenewal()
