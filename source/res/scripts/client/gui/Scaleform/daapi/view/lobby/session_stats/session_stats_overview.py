# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/session_stats_overview.py
import time
from collections import namedtuple
import Event
import SoundGroups
from account_helpers.AccountSettings import AccountSettings, SESSION_STATS_SECTION, SESSION_STATS_PREV_BATTLE_COUNT, BATTLE_EFFICIENCY_SECTION_EXPANDED_FIELD
from account_helpers.settings_core.settings_constants import SESSION_STATS
from adisp import process
from async import async, await
from constants import ARENA_BONUS_TYPE
from frameworks.wulf import WindowLayer
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hof.hof_helpers import getHofAchievementsStatisticUrl, getHofVehiclesStatisticUrl, isHofEnabled
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_settings_controller import SessionStatsSettingsController
from gui.Scaleform.daapi.view.lobby.session_stats.session_stats_views import SessionBattleStatsView, SessionVehicleStatsView
from gui.Scaleform.daapi.view.lobby.session_stats.shared import toIntegral
from gui.Scaleform.daapi.view.meta.SessionStatsOverviewMeta import SessionStatsOverviewMeta
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import ResSimpleDialogBuilder, ResPureDialogBuilder
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from gui.prb_control import prbDispatcherProperty
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.gui_items.processors.session_stats import ResetSessionStatsProcessor
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, time_utils
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_TabData = namedtuple('_TabData', ('alias', 'linkage', 'tooltip', 'label'))
_TABS_DATA_ORDERED = [_TabData(SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS, SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_LINKAGE, backport.text(R.strings.session_stats.tooltip.tabBattle()), backport.text(R.strings.session_stats.label.tabBattle())), _TabData(SESSION_STATS_CONSTANTS.SESSION_VEHICLE_STATS_VIEW_PY_ALIAS, SESSION_STATS_CONSTANTS.SESSION_VEHICLE_STATS_VIEW_LINKAGE, backport.text(R.strings.session_stats.tooltip.tabVehicle()), backport.text(R.strings.session_stats.label.tabVehicle()))]
_TABS_ID = {SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS: SESSION_STATS.BATTLES_TAB,
 SESSION_STATS_CONSTANTS.SESSION_VEHICLE_STATS_VIEW_PY_ALIAS: SESSION_STATS.VEHICLES_TAB}
_HOF_URL_BY_TAB_ALIAS = {SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS: getHofAchievementsStatisticUrl,
 SESSION_STATS_CONSTANTS.SESSION_VEHICLE_STATS_VIEW_PY_ALIAS: getHofVehiclesStatisticUrl}

class SessionStatsOverview(SessionStatsOverviewMeta):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(SessionStatsOverview, self).__init__()
        self.__settingsController = SessionStatsSettingsController()
        self._currentTabAlias = self.__getSavedTab()
        self.onShowSettings = Event.Event()
        self.__sessionVehicleStatsView = None
        self.__sessionBattleStatsView = None
        return

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def onClickMoreBtn(self):
        self._showHof()

    def onClickResetBtn(self):
        self._showStatsResetDialog()

    def onClickSettingsBtn(self):
        self.onShowSettings()

    def onExpanded(self, expanded):
        sessStatSett = AccountSettings.getSettings(SESSION_STATS_SECTION)
        sessStatSett[BATTLE_EFFICIENCY_SECTION_EXPANDED_FIELD] = expanded
        AccountSettings.setSettings(SESSION_STATS_SECTION, sessStatSett)

    def onTabSelected(self, tabAlias):
        self._currentTabAlias = tabAlias
        self.as_setButtonsStateS(self.__getButtonStates())
        self.__saveCurrentTab(tabAlias)

    def _populate(self):
        super(SessionStatsOverview, self)._populate()
        self._itemsCache.onSyncCompleted += self.__updateViewHandler
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__settingsController.start()
        self.updateData()

    def _dispose(self):
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self._itemsCache.onSyncCompleted -= self.__updateViewHandler
        self.__sessionVehicleStatsView = None
        self.__sessionBattleStatsView = None
        self.__settingsController.stop()
        self.__settingsController = None
        super(SessionStatsOverview, self)._dispose()
        return

    @process
    def _showHof(self):
        urlParser = URLMacros()
        url = yield urlParser.parse(url=_HOF_URL_BY_TAB_ALIAS[self._currentTabAlias]())
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_PROFILE), ctx={'hofPageUrl': url}), scope=EVENT_BUS_SCOPE.LOBBY)

    @async
    def _showStatsResetDialog(self):
        container = self.app.containerManager.getContainer(WindowLayer.VIEW)
        lobby = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY})
        timeToClear = time.gmtime(time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay())
        manualResetEnabled = self.__settingsController.getSettings()[SESSION_STATS.IS_NOT_NEEDED_RESET_STATS_EVERY_DAY]
        if manualResetEnabled:
            builder = ResPureDialogBuilder()
        else:
            builder = ResSimpleDialogBuilder()
            builder.setMessageArgs([self.__timeToClearText(timeToClear)])
        builder.setMessagesAndButtons(R.strings.dialogs.sessionStats.confirmReset, btnDownSounds={DialogButtons.SUBMIT: R.sounds.session_stats_clear()})
        result = yield await(dialogs.showSimple(builder.build(lobby)))
        if result:
            self.__resetStats()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(SessionStatsOverview, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, SessionVehicleStatsView):
            self.__sessionVehicleStatsView = viewPy
        if isinstance(viewPy, SessionBattleStatsView):
            self.__sessionBattleStatsView = viewPy

    @process
    def __resetStats(self):
        resetResult = yield ResetSessionStatsProcessor().request()
        AccountSettings.setSessionSettings(SESSION_STATS_PREV_BATTLE_COUNT, 0)
        if resetResult and resetResult.userMsg:
            SystemMessages.pushI18nMessage(resetResult.userMsg, type=resetResult.sysMsgType)

    def __updateViewHandler(self, reason, *_):
        if reason in (CACHE_SYNC_REASON.DOSSIER_RESYNC,):
            self.as_setDataS(self.__makeInitVO())
        if reason in (CACHE_SYNC_REASON.CLIENT_UPDATE,):
            self.updateData()

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
            SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.session_stats_numbers()))
        returnVal = {'battleCount': battleCnt,
         'lastBattleCount': prevBattleCnt,
         'title': self.__getTitle(battleCnt),
         'headerImg': self.__getHeaderImg(),
         'tabs': tabsData,
         'isExpanded': isExpanded}
        AccountSettings.setSessionSettings(SESSION_STATS_PREV_BATTLE_COUNT, battleCnt)
        return returnVal

    def __updateHeaderTooltip(self):
        battleCnt = self._itemsCache.items.sessionStats.getAccountStats(ARENA_BONUS_TYPE.REGULAR).battleCnt
        dontResetStatsDaily = self.__settingsController.getSettings()[SESSION_STATS.IS_NOT_NEEDED_RESET_STATS_EVERY_DAY]
        battleType = backport.text(R.strings.profile.profile.dropdown.labels.random())
        header = backport.text(R.strings.session_stats.tooltip.battleType.header(), battleType=battleType)
        if battleCnt:
            if dontResetStatsDaily:
                body = backport.text(R.strings.session_stats.tooltip.battleType.hasBattles.body(), value=battleCnt)
            else:
                body = backport.text(R.strings.session_stats.tooltip.battleType.hasBattles.daily.body(), value=battleCnt)
        elif dontResetStatsDaily:
            body = backport.text(R.strings.session_stats.tooltip.battleType.noBattles.body())
        else:
            body = backport.text(R.strings.session_stats.tooltip.battleType.noBattles.daily.body())
        self.as_setHeaderTooltipS(makeTooltip(header, body))

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
        dontResetStatsDaily = self.__settingsController.getSettings()[SESSION_STATS.IS_NOT_NEEDED_RESET_STATS_EVERY_DAY]
        clearBtnTooltipHeader = backport.text(R.strings.session_stats.tooltip.clearButton.header())
        if clearBtnEnabled:
            if dontResetStatsDaily:
                clearBtnTooltipBody = backport.text(R.strings.session_stats.tooltip.clearButton.available.body())
            else:
                timeToClear = time.gmtime(time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay())
                clearBtnTooltipBody = backport.text(R.strings.session_stats.tooltip.clearButton.available.daily.body(), time=self.__timeToClearText(timeToClear))
        elif dontResetStatsDaily:
            clearBtnTooltipBody = backport.text(R.strings.session_stats.tooltip.clearButton.unavailable.body())
        else:
            clearBtnTooltipBody = backport.text(R.strings.session_stats.tooltip.clearButton.unavailable.daily.body())
        clearBtnTooltip = makeTooltip(header=clearBtnTooltipHeader, body=clearBtnTooltipBody)
        return [{'btnLabel': label,
          'btnTooltip': moreBtnTooltip,
          'btnEnabled': isHofBtnUnlocked}, {'btnLabel': backport.text(R.strings.menu.tankmanPersonalCase.dropSkillsButtonLabel()),
          'btnTooltip': clearBtnTooltip,
          'btnEnabled': clearBtnEnabled}, {'btnIcon': RES_ICONS.MAPS_ICONS_MESSENGER_ICONSETTINGS,
          'btnTooltip': makeTooltip(header=backport.text(R.strings.session_stats.tooltip.settingsBtn.header()), body=backport.text(R.strings.session_stats.tooltip.settingsBtn.body())),
          'btnEnabled': True}]

    def __timeToClearText(self, timeToClear):
        if timeToClear.tm_hour == 0 and timeToClear.tm_min == 0:
            result = ' ' + backport.text(R.strings.tooltips.template.time.lessThenMinute())
        else:
            result = backport.text(R.strings.dialogs.sessionStats.confirmReset.time(), hours=toIntegral(timeToClear.tm_hour), minutes=toIntegral(timeToClear.tm_min))
        return result

    def __saveCurrentTab(self, alias):
        settings = self.__settingsController.getSettings()
        if settings[SESSION_STATS.IS_NEEDED_SAVE_CURRENT_TAB]:
            settings[SESSION_STATS.CURRENT_TAB] = _TABS_ID[alias]
            self.__settingsController.setSettings(settings)

    def __getSavedTab(self):
        settings = self.__settingsController.getSettings()
        if settings[SESSION_STATS.IS_NEEDED_SAVE_CURRENT_TAB]:
            savedTabs = settings[SESSION_STATS.CURRENT_TAB]
            for alias, idTab in _TABS_ID.iteritems():
                if idTab == savedTabs:
                    return alias

        return SESSION_STATS_CONSTANTS.SESSION_BATTLE_STATS_VIEW_PY_ALIAS

    def updateData(self):
        self._currentTabAlias = self.__getSavedTab()
        if self.__sessionVehicleStatsView:
            self.__sessionVehicleStatsView.updateData()
        if self.__sessionBattleStatsView:
            self.__sessionBattleStatsView.updateData()
        self.__updateHeaderTooltip()
        self.as_setDataS(self.__makeInitVO())
        self._isHofAccessible = isHofEnabled() and self._lobbyContext.getServerSettings().isLinkWithHoFEnabled()
        self.as_setButtonsStateS(self.__getButtonStates())
