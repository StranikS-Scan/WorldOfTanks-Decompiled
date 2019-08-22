# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/battle_royale_page.py
import GUI
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR, BATTLE_ROYALE_INFO_COUNTER
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.battle_royale.battle_royale_sounds import BATTLE_ROYALE_PAGE_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.BattleRoyaleMainPageMeta import BattleRoyaleMainPageMeta
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.BATTLEROYALE_CONSTS import BATTLEROYALE_CONSTS
from gui.battle_royale.royale_builders import main_page_vos
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import time_utils, dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattleRoyaleController
_VIEW_TO_ITEM_ID = {BATTLEROYALE_ALIASES.BATTLE_ROYALE_PROGRESS_FINAL_UI: BATTLEROYALE_CONSTS.BATTLE_ROYALE_PROGRESS_ID,
 BATTLEROYALE_ALIASES.BATTLE_ROYALE_PROGRESS_UI: BATTLEROYALE_CONSTS.BATTLE_ROYALE_PROGRESS_ID,
 BATTLEROYALE_ALIASES.BATTLE_ROYALE_AWARDS_UI: BATTLEROYALE_CONSTS.BATTLE_ROYALE_AWARDS_ID,
 BATTLEROYALE_ALIASES.BATTLE_ROYALE_INFO_UI: BATTLEROYALE_CONSTS.BATTLE_ROYALE_INFO_ID}

class BattleRoyaleMainPage(LobbySubView, BattleRoyaleMainPageMeta):
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __background_alpha__ = 0.2
    _COMMON_SOUND_SPACE = BATTLE_ROYALE_PAGE_SOUND_SPACE

    def __init__(self, ctx):
        super(BattleRoyaleMainPage, self).__init__(ctx)
        self.__selectedItemID = BATTLEROYALE_CONSTS.BATTLE_ROYALE_PROGRESS_ID
        self.__processContext(ctx)
        self.__periodicNotifier = None
        self.__blur = GUI.WGUIBackgroundBlur()
        return

    def onClose(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def onPageChanged(self, viewId):
        newSelectedID = _VIEW_TO_ITEM_ID.get(viewId, self.__selectedItemID)
        if self.__selectedItemID != newSelectedID:
            self.__selectedItemID = newSelectedID
            self.__update()
            self.__resetCounters(newSelectedID)

    def _dispose(self):
        self.__periodicNotifier.stopNotification()
        self.__periodicNotifier.clear()
        self.__battleRoyale.onUpdated -= self.__update
        self.__blur.enable = False
        self.__blur = None
        super(BattleRoyaleMainPage, self)._dispose()
        return

    def _populate(self):
        super(BattleRoyaleMainPage, self)._populate()
        self.__periodicNotifier = PeriodicNotifier(self.__getTimeTillCurrentSeason, self.__updateHeader)
        self.__battleRoyale.onUpdated += self.__update
        self.__resetCounters(self.__selectedItemID)
        self.__update()
        self.__periodicNotifier.startNotification()
        self.__blur.enable = True

    def _invalidate(self, ctx=None):
        self.__processContext(ctx)
        self.__resetCounters(self.__selectedItemID)
        self.__update()

    def __getSelectedIdx(self, menuItems):
        for idx, item in enumerate(menuItems):
            if item['id'] == self.__selectedItemID:
                return idx

    def __processContext(self, ctx):
        self.__selectedItemID = ctx.get('selectedItemID', self.__selectedItemID)
        if self.__selectedItemID == BATTLEROYALE_CONSTS.BATTLE_ROYALE_INFO_ID and ctx.get('showedFromWeb', False):
            stateFlags = self.__getShowStateFlags()
            stateFlags['isBattleRoyaleWelcomeViewShowed'] = True
            self.__setShowStateFlags(stateFlags)

    def __update(self):
        isEnabled = self.__battleRoyale.isEnabled()
        if not isEnabled:
            self.onClose()
        self.__periodicNotifier.startNotification()
        self.__updateHeader()
        self.__updateMenuItems()

    def __updateHeader(self):
        currentSeason = self.__battleRoyale.getCurrentSeason()
        nextSeason = self.__battleRoyale.getNextSeason()
        self.as_setHeaderDataS(main_page_vos.getBattleRoyaleHeader(currentSeason, nextSeason))

    def __updateMenuItems(self):
        menuItems = main_page_vos.getTabsItems(self.__battleRoyale.isAccountMastered())
        self.as_setDataS({'menuItems': menuItems,
         'selectedIndex': self.__getSelectedIdx(menuItems)})

    def __getShowStateFlags(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        return self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)

    def __setShowStateFlags(self, filters):
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, filters)

    def __resetCounters(self, selectedItemID):
        if selectedItemID == BATTLEROYALE_CONSTS.BATTLE_ROYALE_INFO_ID:
            AccountSettings.setCounters(BATTLE_ROYALE_INFO_COUNTER, 0)
        self.__updateCounters()

    def __updateCounters(self):
        infoCounter = main_page_vos.getBubbleLabel(AccountSettings.getCounters(BATTLE_ROYALE_INFO_COUNTER))
        self.as_setCountersS(main_page_vos.getCounterData(infoCounter))

    def __getTimeTillCurrentSeason(self):
        if self.__battleRoyale.getCurrentSeason():
            return time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(self.__battleRoyale.getCurrentSeason().getEndDate()))
        return time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(self.__battleRoyale.getNextSeason().getStartDate())) if self.__battleRoyale.getNextSeason() else time_utils.ONE_MINUTE
