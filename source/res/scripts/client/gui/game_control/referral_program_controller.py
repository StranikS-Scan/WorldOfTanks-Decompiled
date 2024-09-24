# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/referral_program_controller.py
import logging
from Event import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import REFERRAL_COUNTER
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from constants import Configs
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.referral_program.browser.web_handlers import createReferralWebHandlers
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL, isCurrentUserRecruit
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.lobby.common.sound_constants import SUBVIEW_SOUND_SPACE
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.wgnc.custom_actions_keeper import CustomActionsKeeper
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IReferralProgramController, ILimitedUIController
from skeletons.gui.game_window_controller import GameWindowController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class ReferralProgramController(GameWindowController, IReferralProgramController):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __appLoader = dependency.descriptor(IAppLoader)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(ReferralProgramController, self).__init__()
        self.__isReferralEnabled = False
        self.__isEnabled = False
        self.__isReferralHardDisabled = False
        self.__serverSettings = None
        self.__referralConfig = None
        self.onReferralStateChanged = Event()
        self.onReferralProgramUpdated = Event()
        CustomActionsKeeper.registerAction('id_action', self.__processButtonPress)
        return

    @property
    def isEnabled(self):
        return self.__isEnabled and not self.__isReferralHardDisabled

    def setReferralHardDisabled(self, isDisabled=True):
        self.__isReferralHardDisabled = isDisabled
        self.__updateReferralState(hardStateChange=True)

    def onAccountBecomePlayer(self):
        super(ReferralProgramController, self).onAccountBecomePlayer()
        self.__checkReferralState()

    @property
    def isNewReferralSeason(self):
        return False if not self.__isEnabled or not self.__referralConfig.periodNumber else self.__referralConfig.periodNumber != self.__settingsCore.serverSettings.getViewedReferralProgramSeason()

    def showWindow(self, url=None, invokedFrom=None):
        self._showWindow(url, invokedFrom)

    def hideWindow(self):
        browserView = self.__getBrowserView()
        if browserView:
            browserView.onCloseView()

    def isFirstIndication(self):
        return not self.__settingsCore.serverSettings.getUIStorage().get(UI_STORAGE_KEYS.REFERRAL_BUTTON_CIRCLES_SHOWN) and isCurrentUserRecruit()

    def getBubbleCount(self):
        if not self.__isEnabled:
            return 0
        else:
            count = AccountSettings.getCounters(REFERRAL_COUNTER)
            if not self.__limitedUIController.isRuleCompleted(LUI_RULES.referralButtonCounter) and not self.isFirstIndication():
                return 0
            if count is not None and self.isNewReferralSeason:
                count += 1
            return count

    def updateBubble(self):
        browserView = self.__getBrowserView()
        if browserView:
            return
        AccountSettings.setCounters(REFERRAL_COUNTER, self.getBubbleCount() + 1)
        self.__updateBubbleEvent()

    def _openWindow(self, url, _=None):
        browserView = self.__getBrowserView()
        if browserView:
            return
        ctx = {'url': url,
         'webHandlers': createReferralWebHandlers(),
         'browser_alias': VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW,
         'showCloseBtn': True,
         'useSpecialKeys': True,
         'showWaiting': True,
         'showActionBtn': False,
         'allowRightClick': True,
         'soundSpaceID': SUBVIEW_SOUND_SPACE.name}
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__setViewedSeason()
        self.__resetBubbleCount()
        self.__setButtonCirclesShown()

    def _getUrl(self):
        return getReferralProgramURL()

    def __updateReferralState(self, hardStateChange=False):
        if self.__isEnabled != self.__isReferralEnabled or hardStateChange:
            self.__isEnabled = self.__isReferralEnabled
            if not self.__isEnabled:
                self.hideWindow()
            self.onReferralStateChanged()
        if self.__isEnabled:
            self.__updateBubbleEvent()

    def __checkReferralState(self):
        self.__isReferralEnabled = self.__lobbyContext.getServerSettings().isReferralProgramEnabled()
        self.__referralConfig = self.__lobbyContext.getServerSettings().referralProgramConfig
        self.__updateReferralState()

    def _addListeners(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        g_eventBus.addListener(events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW, self.__onReferralProgramButtonClicked, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__limitedUIController.startObserve(LUI_RULES.referralButtonCounter, self.__updateBubbleVisibility)

    def _removeListeners(self):
        self.__limitedUIController.stopObserve(LUI_RULES.referralButtonCounter, self.__updateBubbleVisibility)
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        g_eventBus.removeListener(events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW, self.__onReferralProgramButtonClicked, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onReferralConfigChanged
        return

    def __getBrowserView(self):
        app = self.__appLoader.getApp()
        if app is not None and app.containerManager is not None:
            browserView = app.containerManager.getView(WindowLayer.SUB_VIEW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW})
            return browserView
        else:
            return

    def __onReferralProgramButtonClicked(self, _):
        self.showWindow()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onReferralConfigChanged
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onReferralConfigChanged
        self.__checkReferralState()
        return

    def __onReferralConfigChanged(self, diff):
        if 'isReferralProgramEnabled' in diff:
            self.__isReferralEnabled = diff['isReferralProgramEnabled']
            self.__updateReferralState()
        if Configs.REFERRAL_PROGRAM_CONFIG.value in diff:
            self.__referralConfig = self.__serverSettings.referralProgramConfig
            self.__updateReferralState()

    def __setViewedSeason(self):
        if self.__referralConfig.periodNumber:
            self.__settingsCore.serverSettings.setViewedReferralProgramSeason(self.__referralConfig.periodNumber)

    def __resetBubbleCount(self):
        AccountSettings.setCounters(REFERRAL_COUNTER, 0)
        self.__limitedUIController.completeRule(LUI_RULES.referralButtonCounter)
        self.__updateBubbleEvent()

    def __updateBubbleEvent(self):
        self.onReferralProgramUpdated()

    def __setButtonCirclesShown(self):
        if isCurrentUserRecruit():
            self.__settingsCore.serverSettings.saveInUIStorage({UI_STORAGE_KEYS.REFERRAL_BUTTON_CIRCLES_SHOWN: True})

    def __processButtonPress(self, **_):
        self.showWindow()

    def __updateBubbleVisibility(self, *_):
        self.__updateBubbleEvent()

    def onDisconnected(self):
        super(ReferralProgramController, self).onDisconnected()
        self.__serverSettings = None
        self.__referralConfig = None
        self.__isEnabled = False
        self.__isReferralEnabled = False
        return
