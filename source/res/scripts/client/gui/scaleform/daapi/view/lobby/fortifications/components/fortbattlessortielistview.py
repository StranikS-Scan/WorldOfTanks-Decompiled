# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortBattlesSortieListView.py
from ConnectionManager import connectionManager
from constants import PREBATTLE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.lobby.fortifications.components import sorties_dps
from gui.Scaleform.daapi.view.meta.FortListMeta import FortListMeta
from gui.Scaleform.framework import AppRef, ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.shared.fortifications.fort_hours_ctrlr import getForbiddenPeriods
from gui.prb_control.prb_helpers import UnitListener
from gui.shared.fortifications.fort_helpers import FortListener, adjustDefenceHourToLocal
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from helpers import int2roman
from messenger.proto.events import g_messengerEvents
from messenger.m_constants import USER_ACTION_ID
from predefined_hosts import g_preDefinedHosts

def formatGuiTimeLimitStr(startHour, endHour, useLocalTime = True):

    def _formatHour(hour):
        locHours = adjustDefenceHourToLocal(hour)[0] if useLocalTime else hour
        if locHours >= 10:
            return str(locHours)
        return '0%d' % locHours

    if endHour > 23:
        endHour = 0
    return {'startHour': _formatHour(startHour),
     'startMin': '00',
     'endHour': _formatHour(endHour),
     'endMin': '00'}


class FortBattlesSortieListView(FortListMeta, FortListener, UnitListener, AppRef):

    def __init__(self):
        super(FortBattlesSortieListView, self).__init__()
        self._divisionsDP = None
        self._isBackButtonClicked = False
        self.__clientIdx = None
        self.__sortiesCurfewCtrl = None
        return

    def onContactsUpdated(self, type, contacts):
        if type in (USER_ACTION_ID.FRIEND_ADDED,
         USER_ACTION_ID.FRIEND_REMOVED,
         USER_ACTION_ID.IGNORED_REMOVED,
         USER_ACTION_ID.IGNORED_ADDED,
         USER_ACTION_ID.SUBSCRIPTION_CHANGED):
            unitMgrID = self.unitFunctional.getID()
            if unitMgrID <= 0:
                self.__updateSearchDP(self.fortProvider.getState())

    def onClientStateChanged(self, state):
        self.__updateSearchDP(state)
        self.__validateCreation()
        self.__registerSortiesCurfewController()
        if state.getStateID() not in (CLIENT_FORT_STATE.HAS_FORT, CLIENT_FORT_STATE.CENTER_UNAVAILABLE):
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            self.as_setDetailsS(None)
            cache = self.fortCtrl.getSortiesCache()
            if cache:
                cache.clearSelectedID()
        return

    def onUnitFunctionalInited(self):
        self.unitFunctional.setPrbType(PREBATTLE_TYPE.SORTIE)

    def onSortieChanged(self, cache, item):
        prevIdx = self._searchDP.getSelectedIdx()
        nextIdx = self._searchDP.updateItem(cache, item)
        if nextIdx is not None and nextIdx != -1 and nextIdx != prevIdx:
            self.as_selectByIndexS(nextIdx)
        elif nextIdx is None or nextIdx == -1:
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            self.as_setDetailsS(None)
            cache.clearSelectedID()
        self.__validateCreation()
        self._searchDP.refresh()
        return

    def onSortieRemoved(self, cache, sortieID):
        dropSelection = self._searchDP.removeItem(cache, sortieID)
        if dropSelection:
            self.as_selectByIndexS(-1)
            cache.clearSelectedID()
            self.as_setDetailsS(None)
        self.__validateCreation()
        return

    def onSortieUnitReceived(self, clientIdx):
        result = self._searchDP.getUnitVO(clientIdx)
        self._searchDP.refresh()
        self.as_setDetailsS(result)
        self._updateVehiclesLabel(int2roman(1), int2roman(self._searchDP.getUnitMaxLevel(clientIdx)))

    def changeDivisionIndex(self, index):
        rosterTypeID = self._divisionsDP.getTypeIDByIndex(index)
        self.as_selectByIndexS(-1)
        self._searchDP.setSelectedID(None)
        self.as_setDetailsS(None)
        cache = self.fortCtrl.getSortiesCache()
        if cache:
            cache.clearSelectedID()
            if cache.setRosterTypeID(rosterTypeID):
                self._searchDP.rebuildList(cache)
        return

    def canBeClosed(self, callback):
        self._isBackButtonClicked = True
        super(FortBattlesSortieListView, self).canBeClosed(callback)

    def _populate(self):
        super(FortBattlesSortieListView, self)._populate()
        self.startFortListening()
        if self.unitFunctional.getPrbType() != PREBATTLE_TYPE.NONE:
            self.unitFunctional.setPrbType(PREBATTLE_TYPE.SORTIE)
        self._divisionsDP = sorties_dps.DivisionsDataProvider()
        self._divisionsDP.init(self.as_getDivisionsDPS())
        self.__updateSearchDP(self.fortProvider.getState())
        self.__validateCreation()
        g_messengerEvents.users.onUserActionReceived += self.onContactsUpdated
        self.__registerSortiesCurfewController()

    def _dispose(self):
        self.stopFortListening()
        self.__clientIdx = None
        if self._divisionsDP:
            self._divisionsDP.fini()
            self._divisionsDP = None
        if self._isBackButtonClicked:
            self.fortCtrl.removeSortiesCache()
            self._isBackButtonClicked = False
        g_messengerEvents.users.onUserActionReceived -= self.onContactsUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__sortiesCurfewCtrl:
            self.__sortiesCurfewCtrl.onStatusChanged -= self.__onSortieStatusChanged
        super(FortBattlesSortieListView, self)._dispose()
        return

    def getPyDataProvider(self):
        return sorties_dps.SortiesDataProvider()

    def getCoolDownRequests(self):
        return []

    def getRallyDetails(self, index):
        vo = self._searchDP.getVO(index)
        if vo is None:
            return
        else:
            self.__clientIdx = index
            cache = self.fortCtrl.getSortiesCache()
            if cache and not cache.isRequestInProcess:
                if not cache.setSelectedID(vo['sortieID']):
                    self.as_selectByIndexS(-1)
                    self._searchDP.setSelectedID(None)
                    cache.clearSelectedID()
                    self.as_setDetailsS(None)
                else:
                    self._searchDP.setSelectedID(vo['sortieID'])
            return

    def __updateSearchDP(self, state):
        self.as_setSelectedDivisionS(0)
        if state.getStateID() not in (CLIENT_FORT_STATE.HAS_FORT, CLIENT_FORT_STATE.CENTER_UNAVAILABLE):
            self._searchDP.clear()
            self._searchDP.refresh()
            return
        cache = self.fortCtrl.getSortiesCache()
        if cache:
            self.as_setSelectedDivisionS(self._divisionsDP.getIndexByTypeID(cache.getRosterTypeID()))
            self._searchDP.rebuildList(cache)
            self.as_selectByIndexS(self._searchDP.getSelectedIdx())

    def _onUserActionReceived(self, _, user):
        if self.__clientIdx is not None:
            self.getRallyDetails(self.__clientIdx)
        return

    def __validateCreation(self):
        isValid, reason = self.fortCtrl.getLimits().isSortieCreationValid()
        self.as_tryShowTextMessageS()
        sortiesAvailable, _ = self.__getSortieCurfewStatus()
        if isValid and sortiesAvailable:
            self.as_setCreationEnabledS(True)
        else:
            self.as_setCreationEnabledS(False)
            view = self.app.containerManager.getView(ViewTypes.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW})
            if view is not None:
                view.destroy()
        return

    def __updateForbiddenSortiesData(self):
        sortiesAvailable, servAvailable = self.__getSortieCurfewStatus()
        settings = g_lobbyContext.getServerSettings()
        guiData = {'timeLimits': getForbiddenPeriods(settings.getForbiddenSortieHours(), formatGuiTimeLimitStr)}
        pIds = settings.getForbiddenSortiePeripheryIDs()
        if pIds:
            namesList = []
            for pId in pIds:
                periphery = g_preDefinedHosts.periphery(pId)
                if periphery:
                    namesList.append(periphery.name)

            guiData['serverName'] = ', '.join(namesList)
        self.as_setRegulationInfoS(guiData)
        self.as_setCurfewEnabledS(not sortiesAvailable or not servAvailable)

    def __onSortieStatusChanged(self):
        self.__updateForbiddenSortiesData()
        self.__validateCreation()

    def __registerSortiesCurfewController(self):
        if not self.__sortiesCurfewCtrl:
            self.__sortiesCurfewCtrl = self.fortProvider.getController().getSortiesCurfewCtrl()
            if self.__sortiesCurfewCtrl:
                self.__sortiesCurfewCtrl.onStatusChanged += self.__onSortieStatusChanged
                self.__validateCreation()
                self.__updateForbiddenSortiesData()
        return self.__sortiesCurfewCtrl

    def __getSortieCurfewStatus(self):
        controller = self.__registerSortiesCurfewController()
        if controller is None:
            return (True, True)
        else:
            return controller.getStatus()
