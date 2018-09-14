# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/VehicleSelectorPopup.py
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view.lobby.cyberSport.VehicleSelectorBase import VehicleSelectorBase
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.VehicleSelectorPopupMeta import VehicleSelectorPopupMeta
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework.entities.View import View
from gui.shared.ItemsCache import g_itemsCache, REQ_CRITERIA
from gui.shared.events import CSVehicleSelectEvent, HideWindowEvent

class VehicleSelectorPopup(View, VehicleSelectorPopupMeta, AbstractWindowView, VehicleSelectorBase):

    def __init__(self, ctx = None):
        super(VehicleSelectorPopup, self).__init__()
        raise 'section' in ctx or AssertionError('Section is required to show selector popup')
        self.__isMultiSelect = ctx.get('isMultiSelect', False)
        self.__infoText = ctx.get('infoText', '')
        self.__section = ctx.get('section')
        self.__vehicles = ctx.get('vehicles')
        self.__selectedVehicles = ctx.get('selectedVehicles')
        self.__levelsRange = ctx.get('levelsRange', (1, 10))
        self.showNotReadyVehicles = ctx.get('showNotReady', True)

    def _populate(self):
        super(VehicleSelectorPopup, self)._populate()
        self.addListener(HideWindowEvent.HIDE_VEHICLE_SELECTOR_WINDOW, self.onWindowForceClose)
        self.initFilters()
        self.updateData()
        self.as_setListModeS(self.__isMultiSelect)
        self.as_setInfoTextS(self.__infoText)

    def _dispose(self):
        self.removeListener(HideWindowEvent.HIDE_VEHICLE_SELECTOR_WINDOW, self.onWindowForceClose)
        currentFilters = self.getFilters()
        if currentFilters:
            filters = {'nation': currentFilters['nation'],
             'vehicleType': currentFilters['vehicleType'],
             'isMain': currentFilters['isMain'],
             'level': currentFilters['level'],
             'compatibleOnly': currentFilters['compatibleOnly']}
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
        if not self.getFilters().get('compatibleOnly', True) or self.__vehicles is None:
            vehicles = self._updateData(g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY), self.__levelsRange)
        else:
            vehicles = self._updateData(self.__vehicles, self.__levelsRange)
        if self.__selectedVehicles is not None:
            vehicleGetter = g_itemsCache.items.getItemByCD
            selected = [ makeVehicleVO(vehicleGetter(int(item))) for item in self.__selectedVehicles ]
        else:
            selected = None
        self.as_setListDataS(vehicles, selected)
        return

    def selectClick(self):
        pass
