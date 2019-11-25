# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportUnitsListView.py
from UnitBase import UNIT_BROWSER_TYPE
from gui.Scaleform.daapi.view.lobby.rally.rally_dps import ManualSearchDataProvider
from gui.Scaleform.daapi.view.meta.CyberSportUnitsListMeta import CyberSportUnitsListMeta
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control.settings import REQUEST_TYPE
from gui.shared import events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.view_helpers import CooldownHelper
from helpers import int2roman, dependency
from gui.shared.formatters import text_styles
from skeletons.gui.shared import IItemsCache

class CyberSportUnitsListView(CyberSportUnitsListMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(CyberSportUnitsListView, self).__init__()
        self._unitTypeFlags = UNIT_BROWSER_TYPE.ALL
        self._cooldown = CooldownHelper(self.getCoolDownRequests(), self._onCooldownHandle, events.CoolDownEvent.PREBATTLE)
        self.__currentEmblem = None
        return

    def getPyDataProvider(self):
        return ManualSearchDataProvider()

    def getCoolDownRequests(self):
        return [REQUEST_TYPE.UNITS_LIST]

    def loadPrevious(self):
        listReq = self.prbEntity.getBrowser()
        if listReq:
            listReq.request(req=REQUEST_TYPE.UNITS_NAV_LEFT)

    def loadNext(self):
        listReq = self.prbEntity.getBrowser()
        if listReq:
            listReq.request(req=REQUEST_TYPE.UNITS_NAV_RIGHT)

    def refreshTeams(self):
        listReq = self.prbEntity.getBrowser()
        if listReq:
            listReq.request(req=REQUEST_TYPE.UNITS_REFRESH)

    def getRallyDetails(self, index):
        if index != self._searchDP.selectedRallyIndex:
            self.__currentEmblem = None
        cfdUnitID, vo = self._searchDP.getRally(index)
        listReq = self.prbEntity.getBrowser()
        if listReq:
            listReq.setSelectedID(cfdUnitID)
        self.__setDetails(vo)
        return

    def onPrbEntitySwitching(self):
        browser = self.prbEntity.getBrowser()
        if browser:
            browser.stop()

    def _populate(self):
        super(CyberSportUnitsListView, self)._populate()
        self._cooldown.start()
        self.prbEntity.getBrowser().start(self.__onUnitsListUpdated)
        self.as_setHeaderS({'title': text_styles.promoTitle(CYBERSPORT.WINDOW_UNITLISTVIEW_TITLE),
         'createBtnLabel': CYBERSPORT.WINDOW_UNITLISTVIEW_CREATE_BTN,
         'createBtnTooltip': None,
         'createBtnEnabled': True,
         'columnHeaders': self.__getColumnHeaders()})
        self.itemsCache.onSyncCompleted += self.__refreshData
        return

    def _dispose(self):
        self._cooldown.stop()
        self._cooldown = None
        self.itemsCache.onSyncCompleted -= self.__refreshData
        super(CyberSportUnitsListView, self)._dispose()
        return

    def _onUserActionReceived(self, _, user, shadowMode):
        self.__updateView(user)

    def _doEnableNavButtons(self, isEnabled):
        self.as_updateNavigationBlockS({'previousVisible': True,
         'previousEnabled': isEnabled,
         'nextVisible': True,
         'nextEnabled': isEnabled})

    def _onCooldownHandle(self, isInCooldown):
        self._doEnableNavButtons(not isInCooldown)

    def __refreshData(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                vehDiff = diff[GUI_ITEM_TYPE.VEHICLE]
                for changedVehCD in vehDiff:
                    vehicle = self.itemsCache.items.getItemByCD(changedVehCD)
                    if not vehicle.activeInNationGroup:
                        self.__refreshDetails(self._searchDP.selectedRallyIndex)

            return

    def __getColumnHeaders(self):
        return [self.__createHedader('', 82, 'center', RES_ICONS.MAPS_ICONS_STATISTIC_RATING24),
         self.__createHedader(CYBERSPORT.WINDOW_UNIT_UNITLISTVIEW_COMMANDER, 152),
         self.__createHedader(CYBERSPORT.WINDOW_UNIT_UNITLISTVIEW_DESCRIPTION, 220),
         self.__createHedader(CYBERSPORT.WINDOW_UNIT_UNITLISTVIEW_PLAYERS, 76)]

    def __createHedader(self, label, buttonWidth, position='left', iconSource=None):
        return {'label': label,
         'buttonWidth': buttonWidth,
         'iconSource': iconSource,
         'enabled': False,
         'textAlign': position}

    def __updateVehicleLabel(self):
        settings = self.prbEntity.getRosterSettings()
        self._updateVehiclesLabel(int2roman(settings.getMinLevel()), int2roman(settings.getMaxLevel()))

    def __onUnitsListUpdated(self, selectedID, isFullUpdate, isReqInCoolDown, units):
        if isFullUpdate:
            selectedIdx = self._searchDP.rebuildList(selectedID, units)
            self._doEnableNavButtons(not isReqInCoolDown)
        else:
            selectedIdx = self._searchDP.updateList(selectedID, units)
            self.__refreshDetails(selectedIdx)
        if selectedIdx is not None:
            self.as_selectByIndexS(selectedIdx)
        if self._searchDP.collection:
            self.as_setDummyVisibleS(False)
        else:
            self.as_setDummyVisibleS(True)
            self.as_setDummyS({'htmlText': text_styles.main(CYBERSPORT.WINDOW_UNITLISTVIEW_NOITEMS),
             'alignCenter': True})
        return

    def __setDetails(self, vo):
        linkage = CYBER_SPORT_ALIASES.COMMNAD_DETAILS_LINKAGE_JOIN_TO_NONSTATIC
        self.as_setDetailsS({'viewLinkage': linkage,
         'data': vo})
        self.__updateVehicleLabel()

    def __refreshDetails(self, idx):
        _, vo = self._searchDP.getRally(idx)
        self.__setDetails(vo)

    def __updateView(self, user):
        self._searchDP.updateListItem(user.getID())
        self.__refreshDetails(self._searchDP.selectedRallyIndex)

    def __recenterList(self):
        listReq = self.prbEntity.getBrowser()
        if listReq:
            listReq.request(req=REQUEST_TYPE.UNITS_RECENTER, unitTypeFlags=self._unitTypeFlags)
