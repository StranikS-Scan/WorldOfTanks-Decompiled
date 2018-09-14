# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/BaseTimedCustomizationInterface.py
import time
from abc import abstractmethod, ABCMeta
from datetime import timedelta
from math import ceil
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
import gui
from gui.Scaleform.daapi.view.lobby.customization import CustomizationHelper
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.locale.MENU import MENU
from helpers import i18n
from gui.Scaleform.daapi.view.lobby.customization.CustomizationInterface import CustomizationInterface

class BaseTimedCustomizationInterface(CustomizationInterface):
    ZOOM_FACTOR = 0.2
    __metaclass__ = ABCMeta

    def __init__(self, name, nationId, type, position = -1):
        super(BaseTimedCustomizationInterface, self).__init__(name, nationId, type, position)
        self._currentItemID = None
        self._currentLifeCycle = None
        self._newItemID = None
        self._rentalPackageDP = None
        self._groupsDP = None
        self._itemsDP = None
        self._flashObject = None
        self.__newIds = CustomizationHelper.getNewIdsByType(CUSTOMIZATION_ITEM_TYPE.CI_TYPES[type], nationId)
        return

    @abstractmethod
    def getRentalPackagesDP(self):
        pass

    @abstractmethod
    def getGroupsDP(self):
        pass

    @abstractmethod
    def getItemsDP(self):
        pass

    @abstractmethod
    def getItemPriceFactor(self, vehType):
        pass

    @abstractmethod
    def getItemDefaultPriceFactor(self, vehType):
        pass

    @abstractmethod
    def updateVehicleCustomization(self, itemID = None):
        pass

    @abstractmethod
    def fetchCurrentItem(self, vehDescr):
        pass

    @abstractmethod
    def change(self, vehInvID, section, isAlreadyPurchased):
        pass

    @abstractmethod
    def drop(self, vehInvID, kind):
        pass

    @abstractmethod
    def update(self, vehDescr):
        pass

    def getRealPosition(self):
        if not self.isTurret:
            return self._position - self._positionShift
        return 2 + self._position

    def getDrorStr(self, sectionName, kind):
        items = CustomizationHelper.getItemsOnVehicle(self._type)
        itemIdx = kind if self._type == CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE else self.getRealPosition()
        item = items[itemIdx]
        return 'customization/{0:>s}{1:>s}'.format(sectionName, 'Drop' if item[2] > 0 else 'Dismount')

    def updateSlotsPosition(self, vehDescr):
        pass

    def hasNewItems(self):
        type = CUSTOMIZATION_ITEM_TYPE.CI_TYPES[self._type]
        newItemIDs = CustomizationHelper.getNewIdsByType(type, self._nationID)
        return len(newItemIDs) > 0

    def getSlotsCount(self, descriptor, slotType):
        slots = descriptor.get('emblemSlots', [])
        resultingSlots = [ slot for slot in slots if slot.type == slotType ]
        return len(resultingSlots)

    def _populate(self):
        super(BaseTimedCustomizationInterface, self)._populate()
        self._rentalPackageDP = self.getRentalPackagesDP()
        self._groupsDP = self.getGroupsDP()
        self._itemsDP = self.getItemsDP()
        self._rentalPackageDP.onDataInited += self._onRentalPackagesDataInited
        self._rentalPackageDP.onRentalPackageChange += self.__handleRentalPackageChange

    def _dispose(self):
        CustomizationHelper.updateVisitedItems(CUSTOMIZATION_ITEM_TYPE.CI_TYPES[self._type], self.__newIds)
        self.__newIds = None
        if self._newItemID is not None:
            self.updateVehicleCustomization(self._currentItemID)
        self._rentalPackageDP.onDataInited -= self._onRentalPackagesDataInited
        self._rentalPackageDP.onRentalPackageChange -= self.__handleRentalPackageChange
        self._rentalPackageDP._dispose()
        self._groupsDP._dispose()
        self._itemsDP._dispose()
        self._rentalPackageDP = None
        self._groupsDP = None
        self._itemsDP = None
        self._eventManager.clear()
        LOG_DEBUG('BaseTimedCustomizationInterface _dispose', self._name)
        super(BaseTimedCustomizationInterface, self)._dispose()
        return

    def refreshViewData(self, vehType, refresh = False):
        if vehType is not None:
            self._groupsDP.buildList()
            self._itemsDP.setVehicleTypeParams(self.getItemPriceFactor(vehType), self.getItemDefaultPriceFactor(vehType), self._currentItemID)
        self._rentalPackageDP.refreshList()
        return

    def invalidateViewData(self, vehType, refresh = False):
        if vehType is not None:
            self._groupsDP.buildList()
            self._itemsDP.setVehicleTypeParams(self.getItemPriceFactor(vehType), self.getItemDefaultPriceFactor(vehType), self._currentItemID)
        self._rentalPackageDP.getRentalPackages(refresh)
        return

    def isNewItemSelected(self):
        return self._newItemID is not None

    def getNewItems(self):
        if self._newItemID is not None:
            return [self._itemsDP.makeItem(self._newItemID, False, None, None)]
        else:
            return
            return

    def getSelectedItemCost(self):
        return self._itemsDP.getCost(self._newItemID)

    def getItemCost(self, itemId, priceIndex):
        packageCost = self._rentalPackageDP.pyRequestItemAt(priceIndex)
        cost, isGold = self._itemsDP.getCostForPackagePrice(itemId, packageCost.get('cost', -1), packageCost.get('isGold', False))
        return {'cost': cost,
         'isGold': isGold}

    def isCurrentItemRemove(self):
        return self._currentItemID is not None and self._currentLifeCycle is not None and self._currentLifeCycle[1] > 0

    def getCurrentItemRemoveStr(self):
        removeStr = None
        if self._currentItemID is not None and self._currentLifeCycle is not None:
            if self._currentLifeCycle[1] > 0:
                removeStr = [gui.makeHtmlString('html_templates:lobby/customization', 'remove-{0:>s}'.format(self._name))]
            else:
                removeStr = [gui.makeHtmlString('html_templates:lobby/customization', 'store-{0:>s}'.format(self._name))]
        return removeStr

    def getCurrentItem(self):
        return self._itemsDP.makeItem(self._currentItemID, True, self._currentLifeCycle, self._makeTimeLeftString())

    def onSetID(self, itemID, kind, packageIdx):
        if self._currentItemID == itemID:
            self._newItemID = None
        else:
            self._newItemID = itemID
        self.updateVehicleCustomization(itemID)
        return

    def _makeTimeLeftString(self, **kwargs):
        if self._currentLifeCycle is None:
            return ''
        else:
            startTime, days = self._currentLifeCycle
            result = ''
            if days > 0:
                timeLeft = startTime + days * 86400 - time.time()
                if timeLeft > 0:
                    delta = timedelta(0, timeLeft)
                    if delta.days > 0:
                        result = i18n.makeString(MENU.CUSTOMIZATION_LABELS_TIMELEFT_DAYS, delta.days + 1 if delta.seconds > 0 else delta.days)
                    else:
                        result = i18n.makeString(MENU.CUSTOMIZATION_LABELS_TIMELEFT_HOURS, ceil(delta.seconds / 3600.0))
                else:
                    result = i18n.makeString(MENU.CUSTOMIZATION_LABELS_TIMELEFT_LASTMINUTE)
            return result

    def _onRentalPackagesDataInited(self, selectedPackage, refresh):
        if selectedPackage:
            self._itemsDP.setDefaultCost(selectedPackage.get('cost'), selectedPackage.get('defCost'), selectedPackage.get('isGold'), selectedPackage.get('isIGR'), selectedPackage.get('periodDays'))
        if refresh:
            self._newItemID = None
            self._rentalPackageDP.refresh()
            self._itemsDP.refresh()
        LOG_DEBUG('BaseTimedCustomizationInterface data inited', self._name)
        self.onDataInited(self._name)
        return

    def __handleRentalPackageChange(self, index):
        item = self._rentalPackageDP.selectedPackage
        raise item is not None and item.get('cost') > -1 or AssertionError
        self._itemsDP.setDefaultCost(item.get('cost'), item.get('defCost'), item.get('isGold'), item.get('isIGR'), item.get('periodDays'))
        self._itemsDP.refresh()
        return
