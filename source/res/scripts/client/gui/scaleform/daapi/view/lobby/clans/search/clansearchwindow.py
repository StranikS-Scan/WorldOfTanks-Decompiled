# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/search/ClanSearchWindow.py
import BigWorld
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.clans.clan_helpers import ClanListener, ClanFinder
from gui.clans.items import ClanCommonData, formatField
from gui.clans import formatters as clans_fmts
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE, CLIENT_CLAN_RESTRICTIONS as _CCR
from gui.Scaleform.daapi.view.meta.ClanSearchWindowMeta import ClanSearchWindowMeta
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.WAITING import WAITING
from gui.shared.events import CoolDownEvent
from gui.shared.formatters import text_styles
from gui.shared.view_helpers import CooldownHelper
from gui.shared.view_helpers import ClanEmblemsHelper
from gui.clans.clan_controller import g_clanCtrl
from helpers.i18n import makeString as _ms
_SEARCH_LIMIT = 18
_SEARCH_MAX_CHARS = 70

def _packHeaderColumnData(columnID, label, buttonWidth, tooltip, showSeparator=True, textAlign='center'):
    return {'id': columnID,
     'label': _ms(label),
     'buttonWidth': buttonWidth,
     'toolTip': tooltip,
     'defaultSortDirection': 'ascending',
     'buttonHeight': 34,
     'showSeparator': showSeparator,
     'enabled': False,
     'textAlign': textAlign}


class ClanSearchWindow(ClanSearchWindowMeta, ClanListener):
    __coolDownRequests = [CLAN_REQUESTED_DATA_TYPE.CLAN_RATINGS, CLAN_REQUESTED_DATA_TYPE.SEARCH_CLANS, CLAN_REQUESTED_DATA_TYPE.GET_RECOMMENDED_CLANS]
    MIN_CHARS_FOR_SEARCH = 2

    def __init__(self, ctx):
        super(ClanSearchWindow, self).__init__()
        self.__clanFinder = ClanFinder(g_clanCtrl, None, _SEARCH_LIMIT)
        self.__clanFinder.init()
        self._cooldown = CooldownHelper(self.__coolDownRequests, self._onCooldownHandle, CoolDownEvent.CLAN)
        self.__isFirstPageRequested = False
        self.__invitesLimitReached = False
        return

    def onWindowClose(self):
        self.destroy()

    def onClanStateChanged(self, oldStateID, newStateID):
        if not self.clansCtrl.isEnabled():
            self.onWindowClose()
        if not self.clansCtrl.isAvailable():
            pass

    def search(self, text):
        if len(text) < self.MIN_CHARS_FOR_SEARCH:
            self._showDummy(True)
            self._setDummyData(CLANS.SEARCH_REQUESTTOOSHORT_HEADER, CLANS.SEARCH_REQUESTTOOSHORT_BODY, None, self.__clanFinder.hasSuccessRequest(), _ms(CLANS.SEARCH_REQUESTTOOSHORT_BUTTON), CLANS.SEARCH_REQUESTTOOSHORT_BUTTON_TOOLTIP_HEADER)
        else:
            self.__clanFinder.setRecommended(False)
            self.__doSearch(text)
        return

    def previousPage(self):
        self.as_showWaitingS(WAITING.PREBATTLE_AUTO_SEARCH, {})
        self.__clanFinder.left()

    def nextPage(self):
        self.as_showWaitingS(WAITING.PREBATTLE_AUTO_SEARCH, {})
        self.__clanFinder.right()

    def isInvitesLimitReached(self):
        return self.__invitesLimitReached

    def setInvitesLimitReached(self):
        return self.__invitesLimitReached

    def _populate(self):
        super(ClanSearchWindow, self)._populate()
        self._searchDP = _ClanSearchDataProvider()
        self._searchDP.setFlashObject(self.as_getDPS())
        self.startClanListening()
        self.__clanFinder.onListUpdated += self._onClansListUpdated
        self.__initControls()
        self._updateControlsState()
        self._cooldown.start()
        if not g_clanCtrl.getAccountProfile().isSynced():
            g_clanCtrl.getAccountProfile().resync()
        self.__clanFinder.setRecommended(True)
        self.__doSearch('')

    def _dispose(self):
        self._cooldown.stop()
        self._cooldown = None
        self.stopClanListening()
        self.__clanFinder.onListUpdated -= self._onClansListUpdated
        g_clanCtrl.clearClanCommonDataCache()
        self._searchDP.fini()
        self._searchDP = None
        super(ClanSearchWindow, self)._dispose()
        return

    def getClanInfo(self, clanID):
        return self.__clanFinder.getItemByID(clanID)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ClanSearchWindow, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == CLANS_ALIASES.CLAN_SEARCH_INFO_PY:
            viewPy.bindDataProvider(self)

    def dummyButtonPress(self):
        self.as_showWaitingS(WAITING.PREBATTLE_AUTO_SEARCH, {})
        self._searchDP.rebuildList(None)
        self.__clanFinder.requestLastSuccess()
        return

    def _onCooldownHandle(self, isInCooldown):
        self._updateControlsState()

    def _onClansListUpdated(self, selectedID, isFullUpdate, isReqInCoolDown, result):
        status, data = result
        self._processSearchResponse(status, data, self.__isFirstPageRequested)
        self.__isFirstPageRequested = False
        self.as_hideWaitingS()

    def _processSearchResponse(self, status, data, isInitial=False):
        if status:
            if len(data) > 0:
                self.__applyFoundData(data)
            elif isInitial:
                self._searchDP.rebuildList(None)
                self._showDummy(True)
                self._setDummyData(CLANS.SEARCH_EMPTYRESULT_HEADER, CLANS.SEARCH_EMPTYRESULT_BODY, None, self.__clanFinder.hasSuccessRequest(), _ms(CLANS.SEARCH_EMPTYRESULT_BUTTON), CLANS.SEARCH_EMPTYRESULT_BUTTON_TOOLTIP)
        else:
            self._showErrorDummy()
        self._updateControlsState()
        return

    def _updateControlsState(self):
        isNotInCooldown = not self._cooldown.isInCooldown()
        foundClans = clans_fmts.formatDataToString(self.__clanFinder.getTotalCount())
        self.as_setStateDataS({'foundClans': text_styles.highTitle(_ms(CLANS.SEARCH_CLANSLIST if self.__clanFinder.isRecommended() else CLANS.SEARCH_FOUNDCLANS, value=foundClans)),
         'nextBtnEnabled': self.__clanFinder.canMoveRight() and isNotInCooldown,
         'previousBtnEnabled': self.__clanFinder.canMoveLeft() and isNotInCooldown,
         'searchBtnEnabled': isNotInCooldown,
         'searchInputEnabled': isNotInCooldown})

    def _showErrorDummy(self):
        self._searchDP.rebuildList(None)
        self._showDummy(True)
        self._setDummyData(CLANS.SEARCH_SERVERUNAVAILABLE_HEADER, CLANS.SEARCH_SERVERUNAVAILABLE_BODY, RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON)
        return

    def _showDummy(self, isVisible):
        self.as_setDummyVisibleS(isVisible)

    def _setDummyData(self, header, body, icon=None, btnVisible=False, btnLabel='', btnTooltip=''):
        self.as_setDummyS({'iconSource': icon,
         'htmlText': str().join((text_styles.middleTitle(header), clans_fmts.getHtmlLineDivider(3), text_styles.main(body))),
         'alignCenter': False,
         'btnVisible': btnVisible,
         'btnLabel': btnLabel,
         'btnTooltip': btnTooltip})

    def __initControls(self):
        headers = [_packHeaderColumnData('clan', CLANS.SEARCH_TABLE_CLAN, 244, CLANS.SEARCH_TABLE_CLAN_TOOLTIP, textAlign='left'),
         _packHeaderColumnData('players', CLANS.SEARCH_TABLE_PLAYERS, 107, CLANS.SEARCH_TABLE_PLAYERS_TOOLTIP),
         _packHeaderColumnData('creationDate', CLANS.SEARCH_TABLE_CREATIONDATE, 125, CLANS.SEARCH_TABLE_CREATIONDATE_TOOLTIP),
         _packHeaderColumnData('rating', CLANS.SEARCH_TABLE_RATING, 90, CLANS.SEARCH_TABLE_RATING_TOOLTIP, False, 'right')]
        self.as_setInitDataS({'windowTitle': CLANS.SEARCH_WINDOWTITLE,
         'title': text_styles.promoTitle(_ms(CLANS.SEARCH_TITLE)),
         'titleDescription': text_styles.main(_ms(CLANS.SEARCH_TITLEDESCRIPTION)),
         'searchBtnLabel': CLANS.SEARCH_SEARCHBTN,
         'searchBtnTooltip': CLANS.SEARCH_SEARCHBTN_TOOLTIP,
         'searchInputPrompt': CLANS.SEARCH_SEARCHINPUTPROMPT,
         'searchInputMaxChars': _SEARCH_MAX_CHARS,
         'nextBtnLabel': CLANS.SEARCH_NEXTBTN,
         'nextBtnTooltip': CLANS.SEARCH_NEXTBTN_TOOLTIP,
         'previousBtnLabel': CLANS.SEARCH_PREVIOUSBTN,
         'previousBtnTooltip': CLANS.SEARCH_PREVIOUSBTN_TOOLTIP,
         'tableHeaders': headers})
        self._showDummy(True)
        self._setDummyData(CLANS.SEARCH_PROMOTEXT_HEADER, CLANS.SEARCH_PROMOTEXT_BODY, None)
        return

    def __applyFoundData(self, data):
        self._showDummy(False)
        g_clanCtrl.updateClanCommonDataCache([ ClanCommonData.fromClanSearchData(item) for item in data ])
        self._searchDP.rebuildList(data)
        self.__lastSuccessfullyFoundClans = data

    def __doSearch(self, text):
        """
        :param text: - search criteria
        :param getRecommended: - flag determines is need to get recommended clans
        :type text: str
        :type getRecommended: bool
        """
        self.as_showWaitingS(WAITING.PREBATTLE_AUTO_SEARCH, {})
        self._searchDP.rebuildList(None)
        isValid, reason = g_clanCtrl.getLimits().canSearchClans(text)
        if self.__clanFinder.isRecommended() or isValid:
            self._showDummy(False)
            self.__isFirstPageRequested = True
            self.__clanFinder.setPattern(text)
            self.__clanFinder.reset()
        else:
            if reason == _CCR.SEARCH_PATTERN_INVALID:
                self._processSearchResponse(True, list(), True)
            else:
                self._processSearchResponse(False, list(), True)
            self.as_hideWaitingS()
        return


class _ClanSearchDataProvider(SortableDAAPIDataProvider, ClanEmblemsHelper):

    def __init__(self):
        super(_ClanSearchDataProvider, self).__init__()
        self._list = []
        self._listMapping = {}
        self.__mapping = {}
        self.__selectedID = None
        return

    @property
    def collection(self):
        return self._list

    def emptyItem(self):
        return None

    def clear(self):
        self._list = []
        self._listMapping.clear()
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

    def buildList(self, cache):
        self.clear()
        if cache:
            for index, item in enumerate(cache):
                self._list.append(self._makeVO(item))
                self._listMapping[item.getClanDbID()] = index

            self._rebuildMapping()
            self._requestIcons()

    def rebuildList(self, cache):
        self.buildList(cache)
        self.refresh()

    def refreshItem(self, cache, clanDBID):
        isSelected = self.__selectedID == clanDBID
        self.buildList(cache)
        return True if isSelected and clanDBID not in self.__mapping else False

    def pyGetSelectedIdx(self):
        return self.getSelectedIdx()

    def onClanEmblem16x16Received(self, clanDbID, emblem):
        if emblem:
            index = self._listMapping.get(clanDbID, -1)
            if index >= 0:
                item = self._list[index]
                item['clanInfo']['iconSource'] = 'img://' + self.getMemoryTexturePath(emblem)
                self.refreshSingleItem(index, item)

    def refreshRandomItems(self, indexes, items):
        self.flashObject.invalidateItems(indexes, items)

    def refreshSingleItem(self, index, item):
        self.flashObject.invalidateItem(index, item)

    def _rebuildMapping(self):
        pass

    def _makeVO(self, item):
        vo = {'players': text_styles.main(str(item.getMembersCount())),
         'creationDate': text_styles.main(formatField(getter=item.getCreationDate, formatter=BigWorld.wg_getShortDateFormat)),
         'rating': text_styles.stats(formatField(getter=item.getPersonalRating, formatter=BigWorld.wg_getIntegralFormat)),
         'arrowIcon': RES_ICONS.MAPS_ICONS_LIBRARY_ARROWORANGERIGHTICON8X8,
         'clanInfo': {'dbID': item.getClanDbID(),
                      'clanAbbrev': formatField(getter=item.getClanAbbrev),
                      'clanName': formatField(getter=item.getClanName),
                      'fullName': formatField(getter=item.getClanFullName),
                      'isActive': item.isClanActive(),
                      'showIcon': True,
                      'iconSource': None}}
        return vo

    def requestItemAtHandler(self, idx):
        item = super(_ClanSearchDataProvider, self).requestItemAtHandler(idx)
        if item is None:
            LOG_DEBUG(idx, item)
        return item

    def _requestIcons(self):
        for clanID in self._listMapping:
            self.requestClanEmblem16x16(clanID)
