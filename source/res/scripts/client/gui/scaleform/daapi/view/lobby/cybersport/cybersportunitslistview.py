# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportUnitsListView.py
from debug_utils import LOG_DEBUG
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.rally.rally_dps import ManualSearchDataProvider
from gui.Scaleform.daapi.view.meta.CyberSportUnitsListMeta import CyberSportUnitsListMeta
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.prb_control.functional import unit_ext
from gui.prb_control.prb_helpers import unitFunctionalProperty
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared import events, g_itemsCache, REQ_CRITERIA
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import CSVehicleSelectEvent
from helpers import i18n
__author__ = 'd_dichkovsky'

class CyberSportUnitsListView(CyberSportUnitsListMeta):

    def __init__(self):
        super(CyberSportUnitsListView, self).__init__()
        self._isBackButtonClicked = False
        self._section = 'selectedListVehicles'
        self._selectedVehicles = self.unitFunctional.getSelectedVehicles(self._section)

    def getPyDataProvider(self):
        return ManualSearchDataProvider()

    def getCoolDownRequests(self):
        return [REQUEST_TYPE.UNITS_LIST]

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    def canBeClosed(self, callback):
        self._isBackButtonClicked = True
        callback(True)

    def _populate(self):
        super(CyberSportUnitsListView, self)._populate()
        self.addListener(CSVehicleSelectEvent.VEHICLE_SELECTED, self.__onVehiclesSelectedTeams)
        self.updateSelectedVehicles()
        unit_ext.initListReq(self._selectedVehicles).start(self.__onUnitsListUpdated)
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onVehiclesChanged})
        self.as_setSearchResultTextS(i18n.makeString(CYBERSPORT.WINDOW_UNITLISTVIEW_FOUNDTEAMS))
        self._updateVehiclesLabel('I', 'VIII')

    def _dispose(self):
        super(CyberSportUnitsListView, self)._dispose()
        if self._isBackButtonClicked:
            unit_ext.destroyListReq()
            self._isBackButtonClicked = False
        else:
            listReq = unit_ext.getListReq()
            if listReq:
                listReq.stop()
        self.removeListener(CSVehicleSelectEvent.VEHICLE_SELECTED, self.__onVehiclesSelectedTeams)
        g_clientUpdateManager.removeObjectCallbacks(self)

    def updateSelectedVehicles(self):
        maxLevel = self.unitFunctional.getRosterSettings().getMaxLevel()
        vehiclesCount = len(self._selectedVehicles)
        availableVehiclesCount = len([ k for k, v in g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).items() if v.level <= maxLevel ])
        if vehiclesCount > 0 and vehiclesCount != availableVehiclesCount:
            infoText = makeHtmlString('html_templates:lobby/cyberSport/vehicle', 'selectedValid', {'count': vehiclesCount})
        else:
            infoText = CYBERSPORT.BUTTON_CHOOSEVEHICLES_SELECT
        self.as_setSelectedVehiclesInfoS(infoText, vehiclesCount)

    def filterVehicles(self):
        maxLevel = self.unitFunctional.getRosterSettings().getMaxLevel()
        if self._selectedVehicles is not None and len(self._selectedVehicles) > 0:
            selectedVehicles = self._selectedVehicles
        else:
            selectedVehicles = [ k for k, v in g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).items() if v.level <= maxLevel ]
        self.fireEvent(events.ShowViewEvent(events.ShowWindowEvent.SHOW_VEHICLE_SELECTOR_WINDOW, {'isMultiSelect': True,
         'infoText': CYBERSPORT.WINDOW_VEHICLESELECTOR_INFO_SEARCH,
         'selectedVehicles': selectedVehicles,
         'section': 'cs_list_view_vehicle',
         'maxLevel': maxLevel}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __onUnitsListUpdated(self, selectedID, isFullUpdate, isReqInCoolDown, units):
        if isFullUpdate:
            selectedIdx = self._searchDP.rebuildList(selectedID, units)
            navigationData = {'previousVisible': True,
             'previousEnabled': not isReqInCoolDown,
             'nextVisible': True,
             'nextEnabled': not isReqInCoolDown}
            self.as_updateNavigationBlockS(navigationData)
        else:
            selectedIdx = self._searchDP.updateList(selectedID, units)
        if selectedIdx is not None:
            self.as_selectByIndexS(selectedIdx)
        return

    def loadPrevious(self):
        LOG_DEBUG('load Previous click')
        listReq = unit_ext.getListReq()
        if listReq:
            listReq.request(req=REQUEST_TYPE.UNITS_NAV_LEFT)

    def loadNext(self):
        LOG_DEBUG('load Next click')
        listReq = unit_ext.getListReq()
        if listReq:
            listReq.request(req=REQUEST_TYPE.UNITS_NAV_RIGHT)

    def refreshTeams(self):
        listReq = unit_ext.getListReq()
        if listReq:
            listReq.request(req=REQUEST_TYPE.UNITS_REFRESH)

    def __onVehiclesSelectedTeams(self, event):
        self._selectedVehicles = event.ctx
        self.updateSelectedVehicles()
        self.unitFunctional.setSelectedVehicles(self._section, self._selectedVehicles)
        listReq = unit_ext.getListReq()
        if listReq:
            listReq.request(req=REQUEST_TYPE.UNITS_RECENTER, vehTypes=event.ctx)

    def getRallyDetails(self, index):
        cfdUnitID, vo = self._searchDP.getRally(index)
        listReq = unit_ext.getListReq()
        if listReq:
            listReq.setSelectedID(cfdUnitID)
        return vo

    def __onVehiclesChanged(self, *args):
        self._selectedVehicles = self.unitFunctional.getSelectedVehicles(self._section)
        self.updateSelectedVehicles()
        self.unitFunctional.setSelectedVehicles(self._section, self._selectedVehicles)
