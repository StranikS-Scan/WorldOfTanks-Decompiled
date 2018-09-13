# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/rally_dps.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makePlayerVO, makeUnitShortVO, makeSortiePlayerVO
from gui.Scaleform.daapi.view.lobby.rally.data_providers import BaseRallyListDataProvider
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.prb_control.items.unit_items import getUnitCandidatesComparator
from gui.prb_control.prb_helpers import unitFunctionalProperty
from messenger import g_settings
from messenger.storage import storage_getter

class CandidatesDataProvider(DAAPIDataProvider, AppRef):

    def __init__(self):
        super(CandidatesDataProvider, self).__init__()
        self.clear()

    def init(self, flashObject, candidates):
        self.setFlashObject(flashObject)
        self.rebuild(candidates)

    def fini(self):
        self.clear()
        self._dispose()

    def clear(self):
        self.__list = []
        self.__mapping = {}

    @property
    def collection(self):
        return self.__list

    def buildList(self, candidates):
        self.clear()
        if self.app is not None:
            isPlayerSpeaking = self.app.voiceChatManager.isPlayerSpeaking
        else:
            isPlayerSpeaking = lambda dbID: False
        userGetter = storage_getter('users')().getUser
        colorGetter = g_settings.getColorScheme('rosters').getColors
        mapping = map(lambda pInfo: (pInfo, userGetter(pInfo.dbID)), candidates.itervalues())
        sortedList = sorted(mapping, cmp=getUnitCandidatesComparator())
        for pInfo, user in sortedList:
            dbID = pInfo.dbID
            self.__mapping[dbID] = len(self.__list)
            self.__list.append(self._makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking(dbID)))

        return

    def _makePlayerVO(self, pInfo, user, colorGetter, isPlayerSpeaking):
        return makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)

    def emptyItem(self):
        return {}

    def hasCandidate(self, dbID):
        return dbID in self.__mapping.keys()

    def rebuild(self, candidates):
        self.buildList(candidates)
        self.refresh()

    def setOnline(self, pInfo):
        dbID = pInfo.dbID
        if self.hasCandidate(dbID):
            self.__list[self.__mapping[dbID]]['isOffline'] = pInfo.isOffline()
            self.refresh()


class SortieCandidatesDP(CandidatesDataProvider):

    def __init__(self):
        super(SortieCandidatesDP, self).__init__()

    def _makePlayerVO(self, pInfo, user, colorGetter, isPlayerSpeaking):
        return makeSortiePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)


class ManualSearchDataProvider(BaseRallyListDataProvider):

    def __init__(self):
        super(ManualSearchDataProvider, self).__init__()

    @unitFunctionalProperty
    def unitFunctional(self):
        return None

    def getVO(self, unitIndex = None):
        return makeUnitShortVO(self.unitFunctional, unitIndex)

    def buildList(self, selectedID, result):
        self.clear()
        userGetter = storage_getter('users')().getUser
        colorGetter = g_settings.getColorScheme('rosters').getColors
        pNameGetter = g_lobbyContext.getPeripheryName
        ratingFormatter = BigWorld.wg_getIntegralFormat
        self._selectedIdx = -1
        for unitItem in result:
            creator = unitItem.creator
            if creator:
                dbID = creator.dbID
                creatorVO = makePlayerVO(creator, userGetter(dbID), colorGetter)
            else:
                creatorVO = None
            cfdUnitID = unitItem.cfdUnitID
            index = len(self.collection)
            if cfdUnitID == selectedID:
                self._selectedIdx = index
            self.mapping[cfdUnitID] = index
            self.collection.append({'cfdUnitID': cfdUnitID,
             'unitMgrID': unitItem.unitMgrID,
             'creator': creatorVO,
             'creatorName': creatorVO.get('userName', ''),
             'rating': ratingFormatter(unitItem.rating),
             'playersCount': unitItem.playersCount,
             'commandSize': unitItem.commandSize,
             'inBattle': unitItem.state.isInArena(),
             'isFreezed': unitItem.state.isLocked(),
             'isRestricted': unitItem.isRosterSet,
             'description': unitItem.description,
             'peripheryID': unitItem.peripheryID,
             'server': pNameGetter(unitItem.peripheryID)})

        return self._selectedIdx

    def updateList(self, selectedID, result):
        isFullUpdate, diff = False, []
        self._selectedIdx = None
        userGetter = storage_getter('users')().getUser
        colorGetter = g_settings.getColorScheme('rosters').getColors
        ratingFormatter = BigWorld.wg_getIntegralFormat
        result = set(result)
        removed = set(filter(lambda item: item[1] is None, result))
        isFullUpdate = len(removed)
        for cfdUnitID, unitItem in removed:
            index = self.mapping.pop(cfdUnitID, None)
            if index is not None:
                self.collection.pop(index)
                if cfdUnitID == selectedID:
                    self._selectedIdx = -1
                self.rebuildIndexes()

        if isFullUpdate:
            updated = result.difference(removed)
        else:
            updated = result
        for cfdUnitID, unitItem in updated:
            try:
                index = self.mapping[cfdUnitID]
                item = self.collection[index]
            except (KeyError, IndexError):
                LOG_ERROR('Item not found', unitItem)
                continue

            creator = unitItem.creator
            if creator:
                dbID = creator.dbID
                creatorVO = makePlayerVO(creator, userGetter(dbID), colorGetter)
            else:
                creatorVO = None
            item.update({'creator': creatorVO,
             'rating': ratingFormatter(unitItem.rating),
             'playersCount': unitItem.playersCount,
             'commandSize': unitItem.commandSize,
             'inBattle': unitItem.state.isInArena(),
             'isFreezed': unitItem.state.isLocked(),
             'isRestricted': unitItem.isRosterSet,
             'description': unitItem.description})
            diff.append(index)

        if self._selectedIdx is None and selectedID in self.mapping:
            self._selectedIdx = self.mapping[selectedID]
        if isFullUpdate:
            self.refresh()
        elif len(diff):
            self.updateItems(diff)
        return self._selectedIdx
