# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/VehicleSelectorPopup.py
from account_helpers.AccountSettings import AccountSettings
from constants import VEHICLE_CLASSES
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.VehicleSelectorPopupMeta import VehicleSelectorPopupMeta
from gui.Scaleform.genConsts.VEHICLE_SELECTOR_CONSTANTS import VEHICLE_SELECTOR_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.events import CSVehicleSelectEvent, HideWindowEvent
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class VehicleSelectorPopup(VehicleSelectorPopupMeta, VehicleSelectorBase):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(VehicleSelectorPopup, self).__init__()
        self._levelsRange = ctx.get('levelsRange', self._levelsRange)
        self.__isMultiSelect = ctx.get('isMultiSelect', False)
        self._infoText = ctx.get('infoText', '')
        self.__componentsOffset = ctx.get('componentsOffset', 0)
        self._titleText = ctx.get('titleText', '')
        self._selectButton = ctx.get('selectButton', '')
        self._cancelButton = ctx.get('cancelButton', '')
        self._compatibleOnlyLabel = ctx.get('compatibleOnlyLabel', '')
        self.__section = ctx['section']
        self._vehicles = ctx.get('vehicles')
        self.__selectedVehicles = ctx.get('selectedVehicles')
        self.__vehicleTypes = ctx.get('vehicleTypes', VEHICLE_CLASSES)
        self._filterVisibility = ctx.get('filterVisibility', VEHICLE_SELECTOR_CONSTANTS.VISIBLE_ALL)
        self.showNotReadyVehicles = ctx.get('showNotReady', True)

    def _populate(self):
        super(VehicleSelectorPopup, self)._populate()
        self.addListener(HideWindowEvent.HIDE_VEHICLE_SELECTOR_WINDOW, self.onWindowForceClose)
        self.initFilters()
        self.as_setListModeS(self.__isMultiSelect)
        self.as_setTextsS(self._titleText, self._infoText, self._selectButton, self._cancelButton)

    def _dispose(self):
        self.removeListener(HideWindowEvent.HIDE_VEHICLE_SELECTOR_WINDOW, self.onWindowForceClose)
        currentFilters = self.getFilters()
        if currentFilters:
            self.only_ = {'nation': currentFilters['nation'],
             'vehicleType': currentFilters['vehicleType'],
             'isMain': currentFilters['isMain'],
             'level': currentFilters['level'],
             'compatibleOnly': currentFilters['compatibleOnly']}
            filters = self.only_
            AccountSettings.setFilter(self.__section, filters)
        super(VehicleSelectorPopup, self)._dispose()

    def onWindowForceClose(self, _):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def onSelectVehicles(self, items):
        self.fireEvent(CSVehicleSelectEvent(CSVehicleSelectEvent.VEHICLE_SELECTED, items))
        self.onWindowClose()

    def onFiltersUpdate(self, nation, vehicleType, isMain, level, compatibleOnly):
        self._updateFilter(nation, vehicleType, isMain, level, compatibleOnly)
        self.updateData()

    def initFilters(self):
        filters = AccountSettings.getFilter(self.__section)
        filters = self._initFilter(**filters)
        self._updateFilter(filters['nation'], filters['vehicleType'], filters['isMain'], filters['level'], filters['compatibleOnly'])
        self.as_setFiltersDataS(filters)

    def updateData(self):
        if not self.getFilters().get('compatibleOnly', True) or self._vehicles is None:
            vehicleVOs = self._updateData(self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE))
        else:
            vehicleVOs = self._updateData(self._vehicles)
        if self.__selectedVehicles is not None:
            vehicleGetter = self.itemsCache.items.getItemByCD
            selected = [ makeVehicleVO(vehicleGetter(int(item))) for item in self.__selectedVehicles ]
        else:
            selected = None
        for vehicleVO in vehicleVOs:
            if self._vehicles is not None and vehicleVO['intCD'] not in self._vehicles.keys() and vehicleVO['enabled']:
                vehicleVO['tooltip'] = TOOLTIPS.CYBERSPORT_VEHICLESELECTOR_BADVEHICLE
                vehicleVO['enabled'] = False
                vehicleVO['showAlert'] = True
                vehicleVO['alertSource'] = RES_ICONS.MAPS_ICONS_LIBRARY_GEAR
                vehicleVO['isReadyToFight'] = True

        self.setListData(vehicleVOs, selected)
        return

    def setListData(self, vehicleVOs, selected):
        self.as_setListDataS(vehicleVOs, selected)

    def selectClick(self):
        pass

    def _makeVehicleVOAction(self, vehicle):
        vehicleVO = makeVehicleVO(vehicle, self._levelsRange, self.__vehicleTypes)
        if vehicle.isOnlyForEpicBattles or vehicle.isOnlyForWeekendBrawlBattles or vehicle.isOnlyForBob:
            vehicleVO['enabled'], vehicleVO['tooltip'] = False, TOOLTIPS.CYBERSPORT_UNIT_FIGHTBTN_EVENTVEHICLEWRONGMODE
        return vehicleVO
