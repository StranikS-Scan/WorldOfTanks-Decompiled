# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rally/rally_dps.py
import weakref
import operator
import BigWorld
from helpers import html
from debug_utils import LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.AchievementsUtils import AchievementsUtils
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makePlayerVO, makeUnitShortVO, makeSortiePlayerVO, makeUserVO, makeStaticFormationPlayerVO
from gui.Scaleform.daapi.view.lobby.rally.data_providers import BaseRallyListDataProvider
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.clubs.formatters import getLeagueString, getDivisionString
from gui.clubs.settings import CLIENT_CLUB_STATE, getLadderChevron16x16, getLadderChevron128x128
from gui.prb_control.items.unit_items import getUnitCandidatesComparator
from gui.prb_control.prb_helpers import unitFunctionalProperty
from gui.shared.formatters import icons, text_styles
from gui.shared.view_helpers import UsersInfoHelper
from shared_utils import findFirst
from helpers import i18n
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter
from gui.shared.gui_items.dossier import dumpDossier

class CandidatesDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(CandidatesDataProvider, self).__init__()
        self.clear()

    def init(self, app, flashObject, candidates):
        self.seEnvironment(app)
        self.setFlashObject(flashObject)
        self.rebuild(candidates)

    def fini(self):
        self.clear()
        self._dispose()

    def clear(self):
        self._list = []
        self._mapping = {}

    @property
    def collection(self):
        return self._list

    def buildList(self, candidates):
        self.clear()
        self._buildData(candidates)

    def _buildData(self, candidates):
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
            self._mapping[dbID] = len(self._list)
            self._list.append(self._makePlayerVO(pInfo, user, colorGetter, isPlayerSpeaking(dbID)))

        return

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
            else:
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
            else:
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
                creatorVO = {}
            if unitItem.isClub:
                ladderIcon = getLadderChevron16x16(unitItem.extra.divisionID)
            else:
                ladderIcon = None
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
             'server': pNameGetter(unitItem.peripheryID),
             'ladderIcon': ladderIcon,
             'isStatic': unitItem.isClub})

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
             'inBattle': unitItem.flags.isInArena() or unitItem.flags.isInPreArena(),
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


class ClubsDataProvider(BaseRallyListDataProvider, UsersInfoHelper):

    class _UserEntityAdapter(object):

        def __init__(self, userID, clubItem, user, proxy):
            self.__userID = userID
            self.__proxy = weakref.proxy(proxy)
            self.__clubName = clubItem.getClubName()
            self.__userEntity = user

        def getGuiType(self):
            if self.__userEntity is not None:
                return self.__userEntity.getGuiType()
            else:
                return USER_GUI_TYPE.OTHER

        def getTags(self):
            if self.__userEntity is not None:
                return self.__userEntity.getTags()
            else:
                return []

        def getID(self):
            return self.__userID

        def getName(self):
            if self.__proxy.isUseCreatorName():
                return self.__proxy.getUserName(self.__userID)
            else:
                return self.__clubName

        def getFullName(self):
            if self.__proxy.isUseCreatorName():
                return self.__proxy.getUserFullName(self.__userID)
            else:
                return self.__clubName

        def getClanAbbrev(self):
            return self.__proxy.getUserClanAbbrev(self.__userID)

        def isOnline(self):
            if self.__userEntity is not None:
                return self.__userEntity.isOnline()
            else:
                return False

    def __init__(self):
        super(ClubsDataProvider, self).__init__()
        self._lastResult = []
        self._useCreatorName = True

    def useClubName(self):
        self._useCreatorName = False

    def useCreatorName(self):
        self._useCreatorName = True

    def isUseCreatorName(self):
        return self._useCreatorName

    def getVO(self, club = None, currentState = None, profile = None):
        if club is None or currentState is None or profile is None:
            return
        else:
            _ms = i18n.makeString
            ladderInfo = club.getLadderInfo()
            if ladderInfo.isInLadder():
                ladderLeagueStr = getLeagueString(ladderInfo.getLeague())
                ladderDivStr = getDivisionString(ladderInfo.getDivision())
                ladderInfoStr = text_styles.middleTitle(_ms(CYBERSPORT.WINDOW_STATICRALLYINFO_LADDERINFO, league=ladderLeagueStr, division=ladderDivStr))
            else:
                ladderInfoStr = ''
            dossier = club.getTotalDossier()
            clubTotalStats = dossier.getTotalStats()
            isButtonDisabled = False
            buttonLabel = '#cyberSport:window/staticRallyInfo/joinBtnLabel'
            buttonTooltip = '#tooltips:cyberSport/staticRallyInfo/joinBtn/join'
            buttonInfo = '#cyberSport:window/staticRallyInfo/joinInfo/join'
            limits = currentState.getLimits()
            canSendApp, appReason = limits.canSendApplication(profile, club)
            if currentState.getStateID() == CLIENT_CLUB_STATE.SENT_APP:
                if currentState.getClubDbID() == club.getClubDbID():
                    buttonLabel = '#cyberSport:window/staticRallyInfo/cancelBtnLabel'
                    buttonTooltip = '#tooltips:cyberSport/staticRallyInfo/joinBtn/inProcess'
                    buttonInfo = '#cyberSport:window/staticRallyInfo/joinInfo/inProcess'
                else:
                    isButtonDisabled = True
                    buttonTooltip = '#tooltips:cyberSport/staticRallyInfo/joinBtn/inProcessOther'
                    buttonInfo = '#cyberSport:window/staticRallyInfo/joinInfo/inProcessOther'
            elif currentState.getStateID() == CLIENT_CLUB_STATE.HAS_CLUB:
                isButtonDisabled = True
                buttonTooltip = '#tooltips:cyberSport/staticRallyInfo/joinBtn/alreadyJoined'
                buttonInfo = '#cyberSport:window/staticRallyInfo/joinInfo/alreadyJoined'
            elif not canSendApp:
                isButtonDisabled = True
                buttonTooltip = '#tooltips:cyberSport/staticRallyInfo/joinBtn/applicationCooldown'
                buttonInfo = '#cyberSport:window/staticRallyInfo/joinInfo/applicationCooldown'
            return {'battlesCount': self.__getIndicatorData(clubTotalStats.getBattlesCount(), BigWorld.wg_getIntegralFormat, _ms(CYBERSPORT.WINDOW_STATICRALLYINFO_STATSBATTLESCOUNT), RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_BATTLES40X32, TOOLTIPS.CYBERSPORT_STATICRALLYINFO_STATSBATTLESCOUNT),
             'winsPercent': self.__getIndicatorData(clubTotalStats.getWinsEfficiency(), ProfileUtils.formatFloatPercent, _ms(CYBERSPORT.WINDOW_STATICRALLYINFO_STATICRALLY_STATSWINSPERCENT), RES_ICONS.MAPS_ICONS_LIBRARY_DOSSIER_WINS40X32, TOOLTIPS.CYBERSPORT_STATICRALLYINFO_STATSWINSPERCENT),
             'ladderIcon': getLadderChevron128x128(ladderInfo.getDivision()),
             'ladderInfo': ladderInfoStr,
             'joinInfo': text_styles.main(_ms(buttonInfo)),
             'joinBtnLabel': _ms(buttonLabel),
             'joinBtnTooltip': buttonTooltip,
             'joinBtnDisabled': isButtonDisabled,
             'noAwardsText': CYBERSPORT.WINDOW_STATICRALLYINFO_NOAWARDS,
             'achievements': AchievementsUtils.packAchievementList(clubTotalStats.getSignificantAchievements(), dossier.getDossierType(), dumpDossier(dossier), False, False),
             'rallyInfo': {'icon': None,
                           'name': text_styles.highTitle(club.getUserName()),
                           'profileBtnLabel': CYBERSPORT.RALLYINFO_PROFILEBTN_LABEL,
                           'profileBtnTooltip': TOOLTIPS.RALLYINFO_PROFILEBTN,
                           'description': text_styles.main(html.escape(club.getUserShortDescription())),
                           'ladderIcon': None,
                           'id': club.getClubDbID(),
                           'showLadder': False}}

    def buildList(self, selectedID, result, syncUserInfo = True):
        self.clear()
        userGetter = storage_getter('users')().getUser
        colorGetter = g_settings.getColorScheme('rosters').getColors
        ratingFormatter = BigWorld.wg_getIntegralFormat
        self._selectedIdx = -1
        self._lastResult = result
        data = []
        for clubItem in result:
            cfdUnitID = clubItem.getID()
            creatorID = clubItem.getCreatorID()
            rating = self.getUserRating(creatorID)
            creator = self._UserEntityAdapter(creatorID, clubItem, userGetter(creatorID), self)
            creatorName = creator.getName()
            creatorVO = makeUserVO(creator, colorGetter)
            index = len(self.collection)
            if cfdUnitID == selectedID:
                self._selectedIdx = index
            self.mapping[cfdUnitID] = index
            data.append((rating, {'cfdUnitID': cfdUnitID,
              'unitMgrID': cfdUnitID,
              'creator': creatorVO,
              'creatorName': creatorName,
              'rating': self.getGuiUserRating(creatorID),
              'playersCount': clubItem.getMembersCount(),
              'commandSize': clubItem.getCommandSize(),
              'inBattle': False,
              'isFreezed': False,
              'isRestricted': False,
              'description': html.escape(clubItem.getShortDescription()),
              'peripheryID': -1,
              'server': None,
              'ladderIcon': getLadderChevron16x16(clubItem.getDivision()),
              'isStatic': True}))

        self.collection.extend(map(lambda (r, c): c, sorted(data, reverse=True, key=operator.itemgetter(0))))
        if syncUserInfo:
            self.syncUsersInfo()
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
        result = set(result)
        for clubItem in result:
            try:
                index = self.mapping[clubItem.getID()]
                item = self.collection[index]
            except (KeyError, IndexError):
                LOG_ERROR('Item not found', clubItem)
                continue

            item.update({'rating': self.getGuiUserRating(clubItem.getCreatorID()),
             'playersCount': clubItem.getMembersCount(),
             'commandSize': clubItem.getCommandSize(),
             'description': clubItem.getDescription(),
             'ladderIcon': getLadderChevron16x16(clubItem.getDivision())})
            diff.append(index)

        if self._selectedIdx is None and selectedID in self.mapping:
            self._selectedIdx = self.mapping[selectedID]
        if isFullUpdate:
            self.refresh()
        elif len(diff):
            self.updateItems(diff)
        return self._selectedIdx

    def onUserRatingsReceived(self, ratings):
        self.buildList(self._selectedIdx, self._lastResult, syncUserInfo=False)
        self.refresh()

    def onUserNamesReceived(self, names):
        self.__updateUsersData(names.keys())

    def onUserClanAbbrevsReceived(self, abbrevs):
        self.__updateUsersData(abbrevs.keys())

    def __updateUsersData(self, userDBIDs):
        diff = []
        userGetter = storage_getter('users')().getUser
        colorGetter = g_settings.getColorScheme('rosters').getColors
        for userDBID in userDBIDs:
            data = findFirst(lambda d: d['creator'].get('dbID') == userDBID, self.collection)
            if data is not None:
                clubDBID = data['cfdUnitID']
                try:
                    index = self.mapping[clubDBID]
                    item = self.collection[index]
                except (KeyError, IndexError):
                    LOG_ERROR('Item not found', clubDBID)
                    continue

                creator = userGetter(userDBID)
                creatorVO = makeUserVO(creator, colorGetter)
                creatorName = creator.getName()
                item.update({'creatorName': creatorName,
                 'rating': self.getGuiUserRating(userDBID)})
                if creator.hasValidName():
                    item['creator'] = creatorVO
                diff.append(index)

        if len(diff):
            self.updateItems(diff)
        return

    def __getIndicatorData(self, value, formater, description, icon, tooltip):
        val = ProfileUtils.getValueOrUnavailable(value)
        return {'value': formater(val),
         'description': description,
         'iconSource': icon,
         'tooltip': tooltip,
         'enabled': val != ProfileUtils.UNAVAILABLE_VALUE}
