# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortListView.py
from constants import PREBATTLE_TYPE
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.lobby.fortifications.components import sorties_dps
from gui.Scaleform.daapi.view.meta.FortListMeta import FortListMeta
from gui.Scaleform.framework import AppRef, ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.prb_control.prb_helpers import UnitListener
from gui.shared.fortifications.fort_helpers import FortListener
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from helpers import int2roman

class FortListView(FortListMeta, FortListener, UnitListener, AppRef):

    def __init__(self):
        super(FortListView, self).__init__()
        self._divisionsDP = None
        self._isBackButtonClicked = False
        self.__clientIdx = None
        return

    def onClientStateChanged(self, state):
        self.__updateSearchDP(state)
        self.__validateCreation()
        if state.getStateID() != CLIENT_FORT_STATE.HAS_FORT:
            self.as_selectByIndexS(-1)
            self._searchDP.setSelectedID(None)
            self.as_setDetailsS(None)
            cache = self.fortCtrl.getSortiesCache()
            if cache:
                cache.clearSelectedID()
        return

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
        Waiting.hide('fort/sortie/get')
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
        super(FortListView, self).canBeClosed(callback)

    def _populate(self):
        super(FortListView, self)._populate()
        self.startFortListening()
        self.unitFunctional.setPrbType(PREBATTLE_TYPE.SORTIE)
        self._divisionsDP = sorties_dps.DivisionsDataProvider()
        self._divisionsDP.init(self.as_getDivisionsDPS())
        self.__updateSearchDP(self.fortProvider.getState())
        self.__validateCreation()

    def _dispose(self):
        self.stopFortListening()
        self.__clientIdx = None
        if self._divisionsDP:
            self._divisionsDP.fini()
            self._divisionsDP = None
        if self._isBackButtonClicked:
            self.fortCtrl.removeSortiesCache()
            self._isBackButtonClicked = False
        super(FortListView, self)._dispose()
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
                    Waiting.show('fort/sortie/get')
                    self._searchDP.setSelectedID(vo['sortieID'])
            return

    def __updateSearchDP(self, state):
        self.as_setSelectedDivisionS(0)
        if state.getStateID() != CLIENT_FORT_STATE.HAS_FORT:
            self._searchDP.clear()
            self._searchDP.refresh()
            return
        cache = self.fortCtrl.getSortiesCache()
        if cache:
            self.as_setSelectedDivisionS(self._divisionsDP.getIndexByTypeID(cache.getRosterTypeID()))
            self._searchDP.rebuildList(cache)
            self.as_selectByIndexS(self._searchDP.getSelectedIdx())

    def _onUserRosterChanged(self, _, user):
        if self.__clientIdx is not None:
            self.getRallyDetails(self.__clientIdx)
        return

    def __validateCreation(self):
        isValid, _ = self.fortCtrl.getLimits().isSortieCreationValid()
        if isValid:
            self.as_setCreationEnabledS(True)
        else:
            self.as_setCreationEnabledS(False)
            view = self.app.containerManager.getView(ViewTypes.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: FORTIFICATION_ALIASES.FORT_CHOICE_DIVISION_WINDOW})
            if view is not None:
                view.destroy()
        return
