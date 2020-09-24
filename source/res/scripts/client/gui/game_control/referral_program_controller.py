# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/referral_program_controller.py
import logging
from Event import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import REFERRAL_COUNTER
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.referral_program.browser.web_handlers import createReferralWebHandlers
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL, isCurrentUserRecruit
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.wgnc.custom_actions_keeper import CustomActionsKeeper
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IReferralProgramController
from skeletons.gui.game_window_controller import GameWindowController
_logger = logging.getLogger(__name__)

class ReferralProgramController(GameWindowController, IReferralProgramController):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(ReferralProgramController, self).__init__()
        self.__referralDisabled = False
        self.onReferralProgramEnabled = Event()
        self.onReferralProgramDisabled = Event()
        self.onReferralProgramUpdated = Event()
        CustomActionsKeeper.registerAction('id_action', self.__processButtonPress)

    def showWindow(self, url=None, invokedFrom=None):
        self._showWindow(url, invokedFrom)

    def hideWindow(self):
        browserView = self.__getBrowserView()
        if browserView:
            browserView.onCloseView()

    def isFirstIndication(self):
        return not self.__settingsCore.serverSettings.getUIStorage().get(UI_STORAGE_KEYS.REFERRAL_BUTTON_CIRCLES_SHOWN) and isCurrentUserRecruit()

    def getBubbleCount(self):
        return AccountSettings.getCounters(REFERRAL_COUNTER)

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
         'allowRightClick': True}
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__resetBubbleCount()
        self.__setButtonCirclesShown()

    def _getUrl(self):
        return getReferralProgramURL()

    def _addListeners(self):
        g_eventBus.addListener(events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW, self.__onReferralProgramButtonClicked, scope=EVENT_BUS_SCOPE.LOBBY)
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _removeListeners(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        g_eventBus.removeListener(events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW, self.__onReferralProgramButtonClicked, scope=EVENT_BUS_SCOPE.LOBBY)

    def __getBrowserView(self):
        app = self.__appLoader.getApp()
        if app is not None and app.containerManager is not None:
            browserView = app.containerManager.getView(WindowLayer.SUB_VIEW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW})
            return browserView
        else:
            return

    def __onReferralProgramButtonClicked(self, _):
        self.showWindow()

    def __onServerSettingsChange(self, diff):
        if 'isReferralProgramEnabled' in diff:
            enabled = diff['isReferralProgramEnabled']
            if not enabled:
                self.__onReferralProgramDisabled()
            else:
                self.__onReferralProgramEnabled()

    def __resetBubbleCount(self):
        AccountSettings.setCounters(REFERRAL_COUNTER, 0)
        self.__updateBubbleEvent()

    def __updateBubbleEvent(self):
        self.onReferralProgramUpdated()

    def __onReferralProgramEnabled(self):
        self.__referralDisabled = False
        self.onReferralProgramEnabled()

    def __onReferralProgramDisabled(self):
        self.__referralDisabled = True
        self.hideWindow()
        self.onReferralProgramDisabled()

    def __setButtonCirclesShown(self):
        if isCurrentUserRecruit():
            self.__settingsCore.serverSettings.saveInUIStorage({UI_STORAGE_KEYS.REFERRAL_BUTTON_CIRCLES_SHOWN: True})

    def __processButtonPress(self, **_):
        self.showWindow()
