# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/rally_dps.py
import BigWorld
from gui.prb_control import prbEntityProperty
from helpers import dependency
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makePlayerVO, makeUnitShortVO, makeSortiePlayerVO, makeStaticFormationPlayerVO, makeClanBattlePlayerVO
from gui.Scaleform.daapi.view.lobby.rally.data_providers import BaseRallyListDataProvider
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.items.unit_items import getUnitCandidatesComparator
from gui.shared.formatters import icons, text_styles
from helpers import i18n
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE
from messenger.storage import storage_getter
from messenger.proto import proto_getter
from skeletons.gui.lobby_context import ILobbyContext

class CandidatesDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(CandidatesDataProvider, self).__init__()
        self.clear()

    def init(self, app, flashObject, candidates):
        self.setEnvironment(app)
        self.setFlashObject(flashObject)
        self.rebuild(candidates)

    def fini(self):
        self.clear()
        self.destroy()

    def clear(self):
        self._list = []
        self._mapping = {}

    @property
    def collection(self):
        return self._list

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def buildList(self, candidates):
        self.clear()
        self._buildData(candidates)

    def _buildData(self, candidates):
        isPlayerSpeaking = self.bwProto.voipController.isPlayerSpeaking
        userGetter = storage_getter('users')().getUser
        colorGetter = g_settings.getColorScheme('rosters').getColors
        mapping = map(lambda pInfo: (pInfo, userGetter(pInfo.dbID)), candidates.itervalues())
        sortedList = sorted(mapping, cmp=getUnitCandidatesComparator())
        for pInfo, user in sortedList:
            dbID = pInfo.dbID
            self._mapping[dbID] = len(self._list)
            self._list.append(self._makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking(dbID)))

    def _makePlayerVO(self, pInfo, user, colorGetter, isPlayerSpeaking):
        return makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)

    def emptyItem(self):
        return {}

    def hasCandidate(self, dbID):
        return dbID in self._mapping.keys()

    def rebuild(self, candidates):
        self.buildList(candidates)
        self.refresh()

    def setOnline(self, pInfo):
        dbID = pInfo.dbID
        if self.hasCandidate(dbID):
            self._list[self._mapping[dbID]]['isOffline'] = pInfo.isOffline()
            self.refresh()


class SortieCandidatesDP(CandidatesDataProvider):

    def _makePlayerVO(self, pInfo, user, colorGetter, isPlayerSpeaking):
        return makeSortiePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)


class ClanBattleCandidatesDP(CandidatesDataProvider):

    def _makePlayerVO(self, pInfo, user, colorGetter, isPlayerSpeaking):
        return makeClanBattlePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)


class SortieCandidatesLegionariesDP(SortieCandidatesDP):

    def __init__(self):
        super(SortieCandidatesDP, self).__init__()
        self.__legionariesCount = 0

    @property
    def legionariesCount(self):
        return self.__legionariesCount

    def buildList(self, candidates):
        self.clear()
        self.__legionariesCount = 0
        clanPlayers = {}
        legionaryPlayers = {}
        for key, value in candidates.iteritems():
            if value.isLegionary():
                legionaryPlayers[key] = value
            clanPlayers[key] = value

        self.__legionariesCount = len(legionaryPlayers)
        if clanPlayers:
            self._buildData(clanPlayers)
        self.__addAdditionalBlocks(len(clanPlayers), self.__legionariesCount)
        if legionaryPlayers:
            self._buildData(legionaryPlayers)

    def __addAdditionalBlocks(self, playersCount, legionariesCount):
        headerClanPlayers = {'headerText': text_styles.standard(i18n.makeString(FORTIFICATIONS.FORTBATTLEROOM_LISTHEADER_CLANPLAYERS))}
        emptyRenders = {'emptyRender': True}
        legionariesIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_LEGIONNAIRE, 16, 16, -4, 0)
        textResult = legionariesIcon + text_styles.standard(i18n.makeString(FORTIFICATIONS.FORTBATTLEROOM_LISTHEADER_LEGIONARIESPLAYERS))
        headerLegionasriesPlayers = {'headerText': textResult,
         'headerToolTip': TOOLTIPS.FORTIFICATION_BATTLEROOMLEGIONARIES}
        if playersCount > 0:
            self._list.insert(0, headerClanPlayers)
        if playersCount > 0 and legionariesCount > 0:
            self._list.append(emptyRenders)
        if legionariesCount > 0:
            self._list.append(headerLegionasriesPlayers)


class StaticFormationCandidatesDP(CandidatesDataProvider):

    def buildList(self, candidates):
        self.clear()
        teamPlayers = {}
        legionaryPlayers = {}
        for key, value in candidates.iteritems():
            if value.isLegionary():
                legionaryPlayers[key] = value
            teamPlayers[key] = value

        if teamPlayers:
            self._buildData(teamPlayers)
        self.__addAdditionalBlocks(len(teamPlayers), len(legionaryPlayers))
        if legionaryPlayers:
            self._buildData(legionaryPlayers)

    def _makePlayerVO(self, pInfo, user, colorGetter, isPlayerSpeaking):
        return makeStaticFormationPlayerVO(pInfo, user, colorGetter, isPlayerSpeaking)

    def __addAdditionalBlocks(self, playersCount, legionariesCount):
        if playersCount > 0:
            self._list.insert(0, {'headerText': text_styles.standard(i18n.makeString(CYBERSPORT.WINDOW_UNIT_CANDIDATES_TEAM))})
        if playersCount > 0 and legionariesCount > 0:
            self._list.append({'emptyRender': True})
        if legionariesCount > 0:
            self._list.append({'headerText': '%s%s' % (icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_LEGIONNAIRE, 16, 16, -4, 0), text_styles.standard(i18n.makeString(CYBERSPORT.WINDOW_UNIT_CANDIDATES_LEGIONARIES))),
             'headerToolTip': TOOLTIPS.CYBERSPORT_STATICFORMATION_WAITLIST_LEGIONNAIRES})


class ManualSearchDataProvider(BaseRallyListDataProvider):
    lobbyContext = dependency.descriptor(ILobbyContext)

    @prbEntityProperty
    def prbEntity(self):
        return None

    def getVO(self, unitIndex=None):
        return makeUnitShortVO(self.prbEntity, unitIndex)

    def buildList(self, selectedID, result):
        self.clear()
        userGetter = storage_getter('users')().getUser
        colorGetter = g_settings.getColorScheme('rosters').getColors
        pNameGetter = self.lobbyContext.getPeripheryName
        ratingFormatter = BigWorld.wg_getIntegralFormat
        self._selectedIdx = -1
        for unitItem in result:
            creator = unitItem.creator
            if creator:
                dbID = creator.dbID
                creatorVO = makePlayerVO(creator, userGetter(dbID), colorGetter)
            else:
                creatorVO = {}
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
             'inBattle': unitItem.flags.isInArena(),
             'isFreezed': unitItem.flags.isLocked(),
             'isRestricted': unitItem.isRosterSet,
             'description': unitItem.description,
             'peripheryID': unitItem.peripheryID,
             'server': pNameGetter(unitItem.peripheryID)})

        return self._selectedIdx

    def updateListItem(self, userDBID):
        for item in self.collection:
            creator = item.get('creator', None)
            if creator is None:
                return
            creatorDBID = creator.get('dbID', None)
            if userDBID == creatorDBID:
                userGetter = storage_getter('users')().getUser
                colorGetter = g_settings.getColorScheme('rosters').getColors
                colors = colorGetter(userGetter(creatorDBID).getGuiType())
                creator['colors'] = colors
                self.refresh()
                return

        return

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
             'creatorName': creatorVO.get('userName', ''),
             'rating': ratingFormatter(unitItem.rating),
             'playersCount': unitItem.playersCount,
             'commandSize': unitItem.commandSize,
             'inBattle': unitItem.flags.isInArena(),
             'isFreezed': unitItem.flags.isLocked(),
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
