# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inventory/filters/filter_by_vehicle.py
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.daapi.view.meta.ItemsWithVehicleFilterTabViewMeta import ItemsWithVehicleFilterTabViewMeta
from gui.shared import events, EVENT_BUS_SCOPE

class FiltrableInventoryCategoryByVehicleTabView(ItemsWithVehicleFilterTabViewMeta):

    def __init__(self):
        super(FiltrableInventoryCategoryByVehicleTabView, self).__init__()
        self._selectedVehicle = None
        return

    def resetFilter(self):
        self._selectedVehicle = None
        self.as_updateVehicleFilterButtonS(self.__makeVehicleVO(self._selectedVehicle))
        super(FiltrableInventoryCategoryByVehicleTabView, self).resetFilter()
        return

    def resetVehicleFilter(self):
        self._selectedVehicle = None
        self.as_updateVehicleFilterButtonS(self.__makeVehicleVO(self._selectedVehicle))
        self._buildItems()
        return

    def _populate(self):
        super(FiltrableInventoryCategoryByVehicleTabView, self)._populate()
        self.addListener(events.StorageEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(events.StorageEvent.VEHICLE_SELECTED, self.__onVehicleSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        super(FiltrableInventoryCategoryByVehicleTabView, self)._dispose()

    def _parseLoadedFilters(self, filterDict):
        vehicleCD = filterDict['vehicleCD']
        self._selectedVehicle = self._itemsCache.items.getItemByCD(vehicleCD) if vehicleCD else None
        super(FiltrableInventoryCategoryByVehicleTabView, self)._parseLoadedFilters(filterDict)
        return

    def _prepareDataForFilterSaving(self):
        data = super(FiltrableInventoryCategoryByVehicleTabView, self)._prepareDataForFilterSaving()
        data['vehicleCD'] = self._selectedVehicle.intCD if self._selectedVehicle else None
        return data

    def _initFilter(self):
        super(FiltrableInventoryCategoryByVehicleTabView, self)._initFilter()
        self.as_initVehicleFilterS(self.__makeVehicleVO(self._selectedVehicle))

    def _shouldShowCounter(self):
        return super(FiltrableInventoryCategoryByVehicleTabView, self)._shouldShowCounter() or bool(self._selectedVehicle)

    def __onVehicleSelected(self, event):
        if event.ctx and event.ctx.get('vehicleId') and self.getActive():
            self._selectedVehicle = vehicle = self._itemsCache.items.getItemByCD(event.ctx['vehicleId'])
            self.as_updateVehicleFilterButtonS(self.__makeVehicleVO(vehicle))
            self._buildItems()

    @staticmethod
    def __makeVehicleVO(vehicle):
        if vehicle is None:
            return
        else:
            vo = makeVehicleVO(vehicle)
            vo.update({'type': '{}_elite'.format(vehicle.type) if vehicle.isPremium else vehicle.type})
            return vo
