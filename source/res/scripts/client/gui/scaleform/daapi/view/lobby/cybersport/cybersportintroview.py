# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportIntroView.py
from CurrentVehicle import g_currentVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.prb_control.prb_helpers import unitFunctionalProperty
from gui.shared.events import CSVehicleSelectEvent
from gui.Scaleform.daapi.view.meta.CyberSportIntroMeta import CyberSportIntroMeta
from gui.shared import events
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui import makeHtmlString
__author__ = 'd_dichkovsky'

class CyberSportIntroView(CyberSportIntroMeta):

    def __init__(self):
        super(CyberSportIntroView, self).__init__()
        self.autoMatchIDs = [g_currentVehicle.item.inventoryID]
        self._section = 'selectedIntroVehicles'
        self._selectedVehicles = self.unitFunctional.getSelectedVehicles(self._section, False)

    def _populate(self):
        super(CyberSportIntroView, self)._populate()
        self.addListener(CSVehicleSelectEvent.VEHICLE_SELECTED, self.__updateSelectedVehicles)
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onVehiclesChanged})

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    def setData(self, initialData):
        self.__updateVehicles(self._selectedVehicles)

    def __updateSelectedVehicles(self, event):
        self.__updateVehicles(event.ctx)

    def __updateVehicles(self, compDescr = None):
        maxLevel = self.unitFunctional.getRosterSettings().getMaxLevel()
        if compDescr is not None and len(compDescr) > 0:
            vehicles = compDescr
        else:
            item = g_currentVehicle.item
            isAllowed = g_itemsCache.items.getItemByCD(int(item.intCD)).level <= maxLevel
            vehicles = [item.intCD] if isAllowed else []
        self._selectedVehicles = vehicles
        hasReadyVehicles = False
        for descriptor in vehicles:
            vehicleItem = g_itemsCache.items.getItemByCD(int(descriptor))
            hasReadyVehicles = vehicleItem.isReadyToPrebattle
            if hasReadyVehicles:
                break

        infoText = self.__buildInfoText(len(vehicles), hasReadyVehicles)
        self.unitFunctional.setSelectedVehicles(self._section, vehicles)
        self.as_setSelectedVehiclesS(vehicles, infoText, hasReadyVehicles)
        return

    def __buildInfoText(self, vehiclesCount, hasReadyVehicles):
        templateName = 'selectedValid' if vehiclesCount > 0 and hasReadyVehicles else 'selectedNotValid'
        result = makeHtmlString('html_templates:lobby/cyberSport/vehicle', templateName, {'count': vehiclesCount})
        return result

    def _dispose(self):
        super(CyberSportIntroView, self)._dispose()
        self.removeListener(CSVehicleSelectEvent.VEHICLE_SELECTED, self.__updateSelectedVehicles)
        g_clientUpdateManager.removeObjectCallbacks(self)

    def showSelectorPopup(self):
        rosterSettings = self.unitFunctional.getRosterSettings()
        self.fireEvent(events.ShowViewEvent(events.ShowWindowEvent.SHOW_VEHICLE_SELECTOR_WINDOW, {'isMultiSelect': True,
         'infoText': CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_INTRO,
         'selectedVehicles': self._selectedVehicles,
         'section': 'cs_intro_view_vehicle',
         'maxLevel': rosterSettings.getMaxLevel()}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onVehiclesChanged(self, *args):
        self.__updateVehicles(self.unitFunctional.getSelectedVehicles(self._section))
