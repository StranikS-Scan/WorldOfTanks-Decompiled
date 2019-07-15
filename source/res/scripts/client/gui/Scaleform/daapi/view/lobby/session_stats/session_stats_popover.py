# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/session_stats_popover.py
import time
from collections import namedtuple
from async import async, await
from adisp import process
from account_helpers.AccountSettings import AccountSettings, SESSION_STATS_SECTION, SESSION_STATS_PREV_BATTLE_COUNT, BATTLE_EFFICIENCY_SECTION_EXPANDED_FIELD
from constants import ARENA_BONUS_TYPE
from gui.game_control.links import URLMacros
from gui.prb_control import prbDispatcherProperty
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import ResSimpleDialogBuilder
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getHofAchievementsStatisticUrl, getHofVehiclesStatisticUrl, isHofEnabled
from gui.Scaleform.daapi.view.lobby.session_stats.shared import toIntegral
from gui.Scaleform.daapi.view.meta.SessionStatsPopoverMeta import SessionStatsPopoverMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.session_stats_requester import SessionStatsRequester
from helpers import dependency, time_utils
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
_TabData = namedtuple('_TabData', ('alias', 'linkage', 'tooltip', 'label'))
_TABS_DATA_ORDERED = [_TabData(SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS, SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_LINKAGE, backport.text(R.strings.session_stats.tooltip.tabBattle()), backport.text(R.strings.session_stats.label.tabBattle())), _TabData(SESSION_STATS_CONSTANTS.SESSION_VEHICLE_STATS_VIEW_PY_ALIAS, SESSION_STATS_CONSTANTS.SESSION_VEHICLE_STATS_VIEW_LINKAGE, backport.text(R.strings.session_stats.tooltip.tabVehicle()), backport.text(R.strings.session_stats.label.tabVehicle()))]
_HOF_URL_BY_TAB_ALIAS = {SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS: getHofAchievementsStatisticUrl,
 SESSION_STATS_CONSTANTS.SESSION_VEHICLE_STATS_VIEW_PY_ALIAS: getHofVehiclesStatisticUrl}

class SessionStatsPopover(SessionStatsPopoverMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, ctx=None):
        super(SessionStatsPopover, self).__init__(ctx)
        self._currentTabAlias = SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def onClickMoreBtn(self):
        self._showHof()

    def onClickResetBtn(self):
        self._showStatsResetDialog()

    def onExpanded(self, expanded):
        sessStatSett = AccountSettings.getSettings(SESSION_STATS_SECTION)
        sessStatSett[BATTLE_EFFICIENCY_SECTION_EXPANDED_FIELD] = expanded
        AccountSettings.setSettings(SESSION_STATS_SECTION, sessStatSett)

    def onTabSelected(self, tabAlias):
        self._currentTabAlias = tabAlias
        self.as_setButtonsStateS(self.__getButtonStates())

    def _populate(self):
        super(SessionStatsPopover, self)._populate()
        self._itemsCache.onSyncCompleted += self.__updateViewHandler
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._currentTabAlias = SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS
        self.as_setDataS(self.__makeInitVO())
        self._isHofAccessible = isHofEnabled() and self._lobbyContext.getServerSettings().isLinkWithHoFEnabled()
        self.as_setButtonsStateS(self.__getButtonStates())

    def _dispose(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self._itemsCache.onSyncCompleted -= self.__updateViewHandler
        super(SessionStatsPopover, self)._dispose()

    @process
    def _showHof(self):
        urlParser = URLMacros()
        url = yield urlParser.parse(url=_HOF_URL_BY_TAB_ALIAS[self._currentTabAlias]())
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_PROFILE, ctx={'hofPageUrl': url}), scope=EVENT_BUS_SCOPE.LOBBY)

    @async
    def _showStatsResetDialog(self):
        container = self.app.containerManager.getContainer(ViewTypes.VIEW)
        lobby = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY})
        timeToClear = time.gmtime(time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay())
        builder = ResSimpleDialogBuilder()
        builder.setMessagesAndButtons(R.strings.dialogs.sessionStats.confirmReset, btnDownSounds={DialogButtons.SUBMIT: R.sounds.session_stats_clear()})
        builder.setMessageArgs([toIntegral(timeToClear.tm_hour), toIntegral(timeToClear.tm_min)])
        result = yield await(dialogs.showSimple(builder.build(lobby)))
        if result:
            AccountSettings.setSessionSettings(SESSION_STATS_PREV_BATTLE_COUNT, 0)
            SessionStatsRequester.resetStats()

    def __updateViewHandler(self, reason, _):
        if reason in (CACHE_SYNC_REASON.DOSSIER_RESYNC,):
            self.as_setDataS(self.__makeInitVO())

    def __makeInitVO(self):
        battleCnt = self._itemsCache.items.sessionStats.getAccountStats(ARENA_BONUS_TYPE.REGULAR).battleCnt
        tabsData = []
        for tabData in _TABS_DATA_ORDERED:
            tabsData.append({'alias': tabData.alias,
             'linkage': tabData.linkage,
             'selected': tabData.alias == self._currentTabAlias,
             'tooltip': tabData.tooltip,
             'label': tabData.label})

        sessStatSett = AccountSettings.getSettings(SESSION_STATS_SECTION)
        isExpanded = sessStatSett.get(BATTLE_EFFICIENCY_SECTION_EXPANDED_FIELD, False)
        prevBattleCnt = AccountSettings.getSessionSettings(SESSION_STATS_PREV_BATTLE_COUNT)
        hasBattleCountDifference = battleCnt and battleCnt > prevBattleCnt
        if hasBattleCountDifference:
            self.soundManager.playSound(backport.sound(R.sounds.session_stats_numbers()))
        returnVal = {'battleCount': battleCnt,
         'lastBattleCount': prevBattleCnt,
         'title': self.__getTitle(battleCnt),
         'titleTooltip': self.__getTitleTooltipData(battleCnt),
         'headerImg': self.__getHeaderImg(),
         'tabs': tabsData,
         'isExpanded': isExpanded}
        AccountSettings.setSessionSettings(SESSION_STATS_PREV_BATTLE_COUNT, battleCnt)
        return returnVal

    def __getTitleTooltipData(self, battleCnt):
        battleType = backport.text(R.strings.profile.profile.dropdown.labels.random())
        header = backport.text(R.strings.session_stats.tooltip.battleType.header(), battleType=battleType)
        if battleCnt:
            body = backport.text(R.strings.session_stats.tooltip.battleType.hasBattles.body(), value=battleCnt)
        else:
            body = backport.text(R.strings.session_stats.tooltip.battleType.noBattles.body())
        return makeTooltip(header, body)

    def __getTitle(self, battleCnt):
        return text_styles.promoSubTitle(backport.text(R.strings.session_stats.label.playBattle())) if not battleCnt else text_styles.promoSubTitle(backport.text(R.strings.profile.profile.dropdown.labels.random()))

    def __getHeaderImg(self):
        return RES_ICONS.MAPS_ICONS_BATTLETYPES_BACKGROUNDS_RANDOM

    def __onServerSettingChanged(self, diff):
        if 'hallOfFame' in diff:
            self._isHofAccessible = isHofEnabled() and self._lobbyContext.getServerSettings().isLinkWithHoFEnabled()
            self.as_setButtonsStateS(self.__getButtonStates())
        if 'sessionStats' in diff or ('sessionStats', '_r') in diff:
            isSessionStatsEnabled = diff['sessionStats'].get('isSessionStatsEnabled', False)
            if not isSessionStatsEnabled:
                self.fireEvent(events.HidePopoverEvent(events.HidePopoverEvent.HIDE_POPOVER))
                return
            isLinkWithHoFEnabled = diff['sessionStats'].get('isLinkWithHoFEnabled', False)
            self._isHofAccessible = isSessionStatsEnabled and isLinkWithHoFEnabled
            self.as_setButtonsStateS(self.__getButtonStates())

    def __getButtonStates(self):
        stats = self._itemsCache.items.sessionStats.getAccountStats(ARENA_BONUS_TYPE.REGULAR)
        clearBtnEnabled = stats.battleCnt > 0 or stats.xp > 0 or stats.freeXP > 0
        label = backport.text(R.strings.session_stats.moreBtn.label())
        isHofBtnUnlocked = not self.prbDispatcher.getFunctionalState().isNavigationDisabled() and self._isHofAccessible
        if isHofBtnUnlocked:
            moreBtnTooltip = makeTooltip(header=backport.text(R.strings.session_stats.tooltip.moreBtn.header()), body=backport.text(R.strings.session_stats.tooltip.moreBtn.available.body()))
        else:
            moreBtnTooltip = makeTooltip(header=backport.text(R.strings.session_stats.tooltip.moreBtn.header()), body=backport.text(R.strings.session_stats.tooltip.moreBtn.unavailable.body()))
        if clearBtnEnabled:
            timeToClear = time.gmtime(time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay())
            dropSkillsBtnTooltip = makeTooltip(header=backport.text(R.strings.session_stats.tooltip.dropSkillsButton.header()), body=backport.text(R.strings.session_stats.tooltip.dropSkillsButton.available.body(), hours=toIntegral(timeToClear.tm_hour), minutes=toIntegral(timeToClear.tm_min)))
        else:
            dropSkillsBtnTooltip = makeTooltip(header=backport.text(R.strings.session_stats.tooltip.dropSkillsButton.header()), body=backport.text(R.strings.session_stats.tooltip.dropSkillsButton.unavailable.body()))
        return [{'btnLabel': label,
          'btnTooltip': moreBtnTooltip,
          'btnEnabled': isHofBtnUnlocked}, {'btnLabel': backport.text(R.strings.menu.tankmanPersonalCase.dropSkillsButtonLabel()),
          'btnTooltip': dropSkillsBtnTooltip,
          'btnEnabled': clearBtnEnabled}]
