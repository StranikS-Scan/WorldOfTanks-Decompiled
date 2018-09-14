# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/profile/ClanProfilePersonnelView.py
import BigWorld
from adisp import process
from constants import CLAN_MEMBER_FLAGS
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.shared.utils import sortByFields, weightedAvg
from helpers import i18n
from account_helpers import getAccountDatabaseID
from gui.Scaleform.daapi.view.lobby.clans.profile import MAX_MEMBERS_IN_CLAN
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import HeaderItemsTypes, ProfileUtils
from gui.Scaleform.daapi.view.meta.ClanProfilePersonnelViewMeta import ClanProfilePersonnelViewMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.event_dispatcher import showClanInvitesWindow
from gui.shared.view_helpers import UsersInfoHelper
from gui.clans.settings import CLIENT_CLAN_RESTRICTIONS as RES
from gui.clans import items
from gui.clans import formatters as clans_fmts
from gui.clans.clan_controller import SYNC_KEYS
from helpers.i18n import makeString as _ms
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter
from messenger.m_constants import USER_ACTION_ID
from messenger.proto.bw.find_criteria import BWClanChannelFindCriteria
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
OPEN_INVITES_ACTION_ID = 'openInvites'
OPEN_CLAN_CHANNEL_ACTION_ID = 'openClanChannel'
_UNAVAILABLE_EFFICIENCY_VALUE = -1
_CLAN_MEMBERS_SORT_INDEXES = (CLAN_MEMBER_FLAGS.RESERVIST,
 CLAN_MEMBER_FLAGS.RECRUIT,
 CLAN_MEMBER_FLAGS.PRIVATE,
 CLAN_MEMBER_FLAGS.JUNIOR,
 CLAN_MEMBER_FLAGS.RECRUITER,
 CLAN_MEMBER_FLAGS.TREASURER,
 CLAN_MEMBER_FLAGS.DIPLOMAT,
 CLAN_MEMBER_FLAGS.COMMANDER,
 CLAN_MEMBER_FLAGS.STAFF,
 CLAN_MEMBER_FLAGS.VICE_LEADER,
 CLAN_MEMBER_FLAGS.LEADER)

class _SORT_IDS:
    USER_NAME = 'userName'
    POST = 'post'
    RATING = 'rating'
    BATTLES_COUNT = 'battlesCount'
    BATTLES_PERFORMANCE = 'battlesPerformance'
    AWG_XP = 'awgXP'
    DAYS_IN_CLAN = 'daysInClan'


def _packStat(description, tooltip, icon, isEnabled, text):
    return {'type': HeaderItemsTypes.COMMON,
     'text': text,
     'description': _ms(description),
     'iconPath': ProfileUtils.getIconPath(icon),
     'tooltip': tooltip,
     'enabled': isEnabled}


def _packColumn(columdID, label, buttonWidth, tooltip, icon='', sortOrder=-1, showSeparator=True, defaultSortDirection='descending'):
    return {'id': columdID,
     'label': _ms(label),
     'iconSource': icon,
     'buttonWidth': buttonWidth,
     'toolTip': tooltip,
     'sortOrder': sortOrder,
     'defaultSortDirection': defaultSortDirection,
     'buttonHeight': 34,
     'showSeparator': showSeparator}


def _getAvgStringValue(dataList, key, formatter=None):
    count = 0
    total = 0
    for item in dataList:
        getter = getattr(item, key)
        if items.isValueAvailable(getter):
            count += 1
            total += getter()
        return (False, clans_fmts.DUMMY_UNAVAILABLE_DATA)

    if count > 0:
        value = float(total) / count
        return (True, formatter(value) if formatter else value)
    else:
        return (False, clans_fmts.DUMMY_UNAVAILABLE_DATA)


def _getWeighedAvgStringValue(dataList, key, weightKey, formatter=None):
    vals = []
    weights = []
    weightsSum = 0
    for item in dataList:
        valueGetter = getattr(item, key)
        weightGetter = getattr(item, weightKey)
        if items.isValueAvailable(valueGetter) and items.isValueAvailable(weightGetter):
            weight = weightGetter()
            vals.append(valueGetter())
            weights.append(weight)
            weightsSum += weight
        return (False, clans_fmts.DUMMY_UNAVAILABLE_DATA)

    if weightsSum == 0:
        return (False, clans_fmts.DUMMY_UNAVAILABLE_DATA)
    outcome = weightedAvg(vals, weights)
    return (True, formatter(outcome) if formatter else outcome)


class ClanProfilePersonnelView(ClanProfilePersonnelViewMeta):

    def __init__(self):
        super(ClanProfilePersonnelView, self).__init__()
        self.__membersDP = None
        return

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    @process
    def setClanDossier(self, clanDossier):
        super(ClanProfilePersonnelView, self).setClanDossier(clanDossier)
        self._showWaiting()
        clanInfo = yield clanDossier.requestClanInfo()
        if not clanInfo.isValid():
            self._dummyMustBeShown = True
            self._updateDummy()
            self._hideWaiting()
            return
        members = yield clanDossier.requestMembers()
        if self.isDisposed():
            return
        self.__membersDP = _ClanMembersDataProvider()
        self.__membersDP.setFlashObject(self.as_getMembersDPS())
        self._updateClanInfo(clanInfo)
        membersCount = len(members)
        self.__membersDP.buildList(members, syncUserInfo=True)
        statistics = [_packStat(CLANS.PERSONNELVIEW_CLANSTATS_AVGPERSONALRATING, CLANS.PERSONNELVIEW_CLANSTATS_AVGPERSONALRATING_TOOLTIP, 'avgPersonalRating40x32.png', *self.__membersDP.getAvgGlobalRating()),
         _packStat(CLANS.PERSONNELVIEW_CLANSTATS_AVGBATTLESCOUNT, CLANS.PERSONNELVIEW_CLANSTATS_AVGBATTLESCOUNT_TOOLTIP, 'avgBattlesCount40x32.png', *self.__membersDP.getAvgBattlesCount()),
         _packStat(CLANS.PERSONNELVIEW_CLANSTATS_AVGWINS, CLANS.PERSONNELVIEW_CLANSTATS_AVGWINS_TOOLTIP, 'avgWins40x32.png', *self.__membersDP.getAvgPerformanceBattles()),
         _packStat(CLANS.PERSONNELVIEW_CLANSTATS_AVGEXP, CLANS.PERSONNELVIEW_CLANSTATS_AVGEXP_TOOLTIP, 'avgExp40x32.png', *self.__membersDP.getAvgXp())]
        headers = [_packColumn(_SORT_IDS.USER_NAME, _ms(CLANS.PERSONNELVIEW_TABLE_PLAYER, count=text_styles.stats(str(membersCount)), max=str(MAX_MEMBERS_IN_CLAN)), 223, CLANS.PERSONNELVIEW_TABLE_PLAYER_TOOLTIP, defaultSortDirection='ascending'),
         _packColumn(_SORT_IDS.POST, CLANS.PERSONNELVIEW_TABLE_POST, 275, CLANS.PERSONNELVIEW_TABLE_POST_TOOLTIP),
         _packColumn(_SORT_IDS.RATING, '', 100, CLANS.PERSONNELVIEW_TABLE_PERSONALRATING_TOOLTIP, RES_ICONS.MAPS_ICONS_STATISTIC_RATING24),
         _packColumn(_SORT_IDS.BATTLES_COUNT, '', 100, CLANS.PERSONNELVIEW_TABLE_BATTLESCOUNT_TOOLTIP, RES_ICONS.MAPS_ICONS_STATISTIC_BATTLES24),
         _packColumn(_SORT_IDS.BATTLES_PERFORMANCE, '', 100, CLANS.PERSONNELVIEW_TABLE_WINS_TOOLTIP, RES_ICONS.MAPS_ICONS_STATISTIC_WINS24),
         _packColumn(_SORT_IDS.AWG_XP, '', 100, CLANS.PERSONNELVIEW_TABLE_AVGEXP_TOOLTIP, RES_ICONS.MAPS_ICONS_STATISTIC_AVGEXP24),
         _packColumn(_SORT_IDS.DAYS_IN_CLAN, '', 100, CLANS.PERSONNELVIEW_TABLE_DAYSINCLAN_TOOLTIP, RES_ICONS.MAPS_ICONS_STATISTIC_DAYSINCLAN24, showSeparator=False)]
        self.as_setDataS({'title': text_styles.standard(CLANS.PERSONNELVIEW_TITLE),
         'tableHeaders': headers,
         'statistics': statistics,
         'defaultSortField': _SORT_IDS.POST,
         'defaultSortDirection': 'descending'})
        self._updateHeaderState()
        self._hideWaiting()

    def onHeaderButtonClick(self, actionID):
        if actionID == OPEN_CLAN_CHANNEL_ACTION_ID:
            channel = self.channelsStorage.getChannelByCriteria(BWClanChannelFindCriteria())
            if channel is not None:
                g_messengerEvents.channels.onPlayerEnterChannelByAction(channel)
            else:
                LOG_WARNING("Clan channel couldn't find!")
        elif actionID == OPEN_INVITES_ACTION_ID:
            showClanInvitesWindow()
        else:
            super(ClanProfilePersonnelView, self).onHeaderButtonClick(actionID)
        return

    def onAccountClanProfileChanged(self, profile):
        self._updateHeaderState()

    def onClanAppsCountReceived(self, clanDbID, appsCount):
        if self._clanDossier.getDbID() == clanDbID:
            self._updateHeaderState()

    def _dispose(self):
        if self.__membersDP:
            self.__membersDP.fini()
            self.__membersDP = None
        super(ClanProfilePersonnelView, self)._dispose()
        return

    def _updateHeaderState(self):
        limits = self.clansCtrl.getLimits()
        if limits.canAcceptApplication(self._clanDossier).success or limits.canDeclineApplication(self._clanDossier).success:
            vo = self._getHeaderButtonStateVO(False, None, True, True, False, OPEN_INVITES_ACTION_ID, topTF=i18n.makeString(CLANS.CLAN_HEADER_INVITESANDREQUESTS))
            if self._clanDossier.isSynced(SYNC_KEYS.APPS) and self._clanDossier.getAppsCount() == 0:
                envelopeIcon = RES_ICONS.MAPS_ICONS_BUTTONS_ENVELOPEOPENED
            else:
                envelopeIcon = RES_ICONS.MAPS_ICONS_BUTTONS_ENVELOPE
            vo['iconBtnIcon'] = envelopeIcon
            self.as_setHeaderStateS(vo)
        else:
            super(ClanProfilePersonnelView, self)._updateHeaderState()
        return

    def _initHeaderBtnStates(self):
        states = super(ClanProfilePersonnelView, self)._initHeaderBtnStates()
        states[RES.OWN_CLAN] = self._getHeaderButtonStateVO(True, i18n.makeString(CLANS.CLAN_HEADER_CHATCHANNELBTN), actionId=OPEN_CLAN_CHANNEL_ACTION_ID, actionBtnTooltip=CLANS.CLAN_HEADER_CHATCHANNELBTN_TOOLTIP)
        return states


class _ClanMembersDataProvider(SortableDAAPIDataProvider, UsersInfoHelper):

    def __init__(self):
        super(_ClanMembersDataProvider, self).__init__()
        self._list = []
        self.__mapping = {}
        self.__selectedID = None
        self.__accountsList = []
        self.__sortMapping = {_SORT_IDS.USER_NAME: lambda memberData: self.__getMemberName(memberData).lower(),
         _SORT_IDS.POST: self.__getMemberRole,
         _SORT_IDS.RATING: self.__getMemberRating,
         _SORT_IDS.BATTLES_COUNT: self.__getMemberBattlesCount,
         _SORT_IDS.BATTLES_PERFORMANCE: self.__getMemberBattlesPerformance,
         _SORT_IDS.AWG_XP: self.__getMemberAwgExp,
         _SORT_IDS.DAYS_IN_CLAN: self.__getMemberDaysInClan}
        return

    def setFlashObject(self, movieClip, autoPopulate=True, setScript=True):
        super(_ClanMembersDataProvider, self).setFlashObject(movieClip, autoPopulate, setScript)
        usersEvents = g_messengerEvents.users
        usersEvents.onUserActionReceived += self.__me_onUserActionReceived
        usersEvents.onClanMembersListChanged += self.__me_onClanMembersListChanged
        usersEvents.onUserStatusUpdated += self.__me_onUserStatusUpdated

    @storage_getter('users')
    def userStorage(self):
        return None

    @property
    def collection(self):
        return self._list

    @property
    def sortedCollection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []
        self.__accountsList = []
        self.__mapping.clear()
        self.__selectedID = None
        return

    def fini(self):
        self.clear()
        self._dispose()

    def getSelectedIdx(self):
        return self.__mapping[self.__selectedID] if self.__selectedID in self.__mapping else -1

    def setSelectedID(self, id):
        self.__selectedID = id

    def getVO(self, index):
        vo = None
        if index > -1:
            try:
                vo = self.sortedCollection[index]
            except IndexError:
                LOG_ERROR('Item not found', index)

        return vo

    def buildList(self, accounts, syncUserInfo=False):
        self.clear()
        self.__accountsList = accounts
        self._list = list((self._makeVO(acc) for acc in accounts))
        if syncUserInfo:
            self.syncUsersInfo()

    def refreshItem(self, cache, clanDBID):
        isSelected = self.__selectedID == clanDBID
        self.buildList(cache)
        return True if isSelected and clanDBID not in self.__mapping else False

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def onUserNamesReceived(self, names):
        if self.__accountsList and len(names):
            self.buildList(self.__accountsList)
            self.refresh()

    def pySortOn(self, fields, order):
        super(_ClanMembersDataProvider, self).pySortOn(fields, order)
        if self.__accountsList:
            self.__accountsList = sortByFields(self._sort, self.__accountsList, valueGetter=self.__sortingMethod)
            self.buildList(self.__accountsList)
            self.refresh()

    def getAvgGlobalRating(self):
        return _getAvgStringValue(self.__accountsList, 'getGlobalRating', formatter=BigWorld.wg_getIntegralFormat)

    def getAvgBattlesCount(self):
        return _getAvgStringValue(self.__accountsList, 'getBattlesCount', formatter=BigWorld.wg_getIntegralFormat)

    def getAvgPerformanceBattles(self):
        return _getWeighedAvgStringValue(self.__accountsList, 'getBattlesPerformanceAvg', 'getBattlesCount', formatter=lambda v: BigWorld.wg_getNiceNumberFormat(v) + '%')

    def getAvgXp(self):
        return _getWeighedAvgStringValue(self.__accountsList, 'getBattleXpAvg', 'getBattlesCount', formatter=BigWorld.wg_getIntegralFormat)

    def _makeVO(self, memberData):
        memberDBID = memberData.getDbID()
        contactEntity = self.userStorage.getUser(memberDBID)
        if contactEntity:
            userVO = ContactConverter().makeVO(contactEntity)
            userVO['userProps']['clanAbbrev'] = ''
        else:
            userVO = {'userProps': {'userName': self.__getMemberName(memberData)}}
        return {'dbID': memberDBID,
         'userName': self.__getMemberName(memberData),
         'post': items.formatField(getter=memberData.getRoleString),
         'postIcon': memberData.getRoleIcon(),
         'personalRating': items.formatField(getter=memberData.getGlobalRating, formatter=BigWorld.wg_getIntegralFormat),
         'battlesCount': items.formatField(getter=memberData.getBattlesCount, formatter=BigWorld.wg_getIntegralFormat),
         'wins': items.formatField(getter=memberData.getBattlesPerformanceAvg, formatter=lambda x: BigWorld.wg_getNiceNumberFormat(x) + '%'),
         'awgExp': items.formatField(getter=memberData.getBattleXpAvg, formatter=BigWorld.wg_getIntegralFormat),
         'daysInClan': items.formatField(getter=memberData.getDaysInClan, formatter=BigWorld.wg_getIntegralFormat),
         'canShowContextMenu': memberDBID != getAccountDatabaseID(),
         'contactItem': userVO}

    def _dispose(self):
        usersEvents = g_messengerEvents.users
        usersEvents.onUserActionReceived -= self.__me_onUserActionReceived
        usersEvents.onClanMembersListChanged -= self.__me_onClanMembersListChanged
        usersEvents.onUserStatusUpdated -= self.__me_onUserStatusUpdated
        self.__sortMapping.clear()
        super(_ClanMembersDataProvider, self)._dispose()

    def __me_onUserActionReceived(self, actionID, contact):
        if actionID == USER_ACTION_ID.FRIEND_REMOVED or actionID == USER_ACTION_ID.FRIEND_ADDED or actionID == USER_ACTION_ID.MUTE_SET or actionID == USER_ACTION_ID.MUTE_UNSET or actionID == USER_ACTION_ID.NOTE_CHANGED or actionID == USER_ACTION_ID.IGNORED_ADDED or actionID == USER_ACTION_ID.IGNORED_REMOVED or actionID == USER_ACTION_ID.TMP_IGNORED_ADDED or actionID == USER_ACTION_ID.TMP_IGNORED_REMOVED:
            self.buildList(self.__accountsList)
            self.refresh()

    def __me_onClanMembersListChanged(self):
        self.buildList(self.__accountsList)
        self.refresh()

    def __me_onUserStatusUpdated(self, _):
        self.buildList(self.__accountsList)
        self.refresh()

    def __sortingMethod(self, item, field):
        valueGetter = self.__sortMapping[field]
        return valueGetter(item)

    def __getMemberName(self, memberData):
        return items.formatField(getter=memberData.getDbID, formatter=self.getUserName)

    def __getMemberRole(self, memberData):
        return len(_CLAN_MEMBERS_SORT_INDEXES) if not items.isValueAvailable(memberData.getRole) else _CLAN_MEMBERS_SORT_INDEXES.index(memberData.getRole())

    def __getMemberRating(self, memberData):
        return memberData.getGlobalRating()

    def __getMemberBattlesCount(self, memberData):
        return memberData.getBattlesCount()

    def __getMemberBattlesPerformance(self, memberData):
        if memberData.getBattlesCount() > 0:
            return memberData.getBattlesPerformanceAvg()
        else:
            return _UNAVAILABLE_EFFICIENCY_VALUE

    def __getMemberAwgExp(self, memberData):
        if memberData.getBattlesCount() > 0:
            return memberData.getBattleXpAvg()
        else:
            return _UNAVAILABLE_EFFICIENCY_VALUE

    def __getMemberDaysInClan(self, memberData):
        return memberData.getDaysInClan()
