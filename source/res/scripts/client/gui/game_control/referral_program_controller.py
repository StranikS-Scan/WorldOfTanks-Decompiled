# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/referral_program_controller.py
import logging
import BigWorld
from Event import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import REFERRAL_COUNTER
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from constants import RP_PGB_POINT
from frameworks.wulf import WindowLayer
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.referral_program.browser.web_handlers import createReferralWebHandlers
from gui.Scaleform.daapi.view.lobby.referral_program.referral_program_helpers import getReferralProgramURL, isCurrentUserRecruit, REF_RPOGRAM_PDATA_KEY
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.wgnc.custom_actions_keeper import CustomActionsKeeper
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IReferralProgramController
from skeletons.gui.game_window_controller import GameWindowController
from gui.ClientUpdateManager import g_clientUpdateManager
from PlayerEvents import g_playerEvents
_logger = logging.getLogger(__name__)
USE_SERVER_RECRUIT_DELTA = True
REQUEST_INCREMENT_COOLDOWN = 1

class ReferralProgramController(GameWindowController, IReferralProgramController):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __appLoader = dependency.descriptor(IAppLoader)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(ReferralProgramController, self).__init__()
        self.__referralDisabled = False
        self.__updateBubbleTimeoutID = None
        self.__recruitDeltaInc = 0
        self.onReferralProgramEnabled = Event()
        self.onReferralProgramDisabled = Event()
        self.onReferralProgramUpdated = Event()
        self.onPointsChanged = Event()
        CustomActionsKeeper.registerAction('id_action', self.__processButtonPress)
        return

    def fini(self):
        self.__clearBubbleTimeout()
        super(ReferralProgramController, self).fini()

    def showWindow(self, url=None, invokedFrom=None):
        if not self.__referralDisabled:
            self._showWindow(url, invokedFrom)
        else:
            SystemMessages.pushMessage(backport.text(R.strings.system_messages.referral_program.disabled()), type=SM_TYPE.Error)

    def hideWindow(self):
        browserView = self.__getBrowserView()
        if browserView:
            browserView.onCloseView()

    def isFirstIndication(self):
        return not self.__settingsCore.serverSettings.getUIStorage().get(UI_STORAGE_KEYS.REFERRAL_BUTTON_CIRCLES_SHOWN) and isCurrentUserRecruit()

    def getBubbleCount(self):
        return self.__getServerBubbleCount() if USE_SERVER_RECRUIT_DELTA else self.__getClientBubbleCount()

    def updateBubble(self):
        browserView = self.__getBrowserView()
        if browserView:
            return
        if USE_SERVER_RECRUIT_DELTA:
            self.__updateServerBubble()
        else:
            self.__updateClientBubble()

    def isScoresLimitReached(self):
        points = self.__itemsCache.items.stats.entitlements.get(RP_PGB_POINT, 0)
        freePoints = self.__itemsCache.items.refProgram.getRPPgbPoints()
        return freePoints > 0 and points >= freePoints

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
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        g_clientUpdateManager.addCallbacks({'cache.entitlements': self.__onEntitlementsUpdated})

    def _removeListeners(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)
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

    def __onEntitlementsUpdated(self, diff):
        if not self.__referralDisabled:
            self.onPointsChanged()

    def __onClientUpdated(self, diff, _):
        if diff is not None and REF_RPOGRAM_PDATA_KEY in diff:
            self.onPointsChanged()
            self.onReferralProgramUpdated()
        return

    def __getServerBubbleCount(self):
        return self.__itemsCache.items.refProgram.getRecruitDelta()

    def __getClientBubbleCount(self):
        return AccountSettings.getCounters(REFERRAL_COUNTER)

    def __updateServerBubble(self):
        self.__recruitDeltaInc += 1
        self.__clearBubbleTimeout()
        self.__updateBubbleTimeoutID = BigWorld.callback(REQUEST_INCREMENT_COOLDOWN, self.__updateServerBubbleRequest)

    def __updateServerBubbleRequest(self):
        self.__updateBubbleTimeoutID = None
        if self.__recruitDeltaInc:
            BigWorld.player().referralProgram.incrementRecruitDelta(self.__recruitDeltaInc, None)
            self.__recruitDeltaInc = 0
        return

    def __clearBubbleTimeout(self):
        if self.__updateBubbleTimeoutID:
            BigWorld.cancelCallback(self.__updateBubbleTimeoutID)
            self.__updateBubbleTimeoutID = None
        return

    def __updateClientBubble(self):
        AccountSettings.setCounters(REFERRAL_COUNTER, self.getBubbleCount() + 1)
        self.onReferralProgramUpdated()

    def __resetBubbleCount(self):
        if USE_SERVER_RECRUIT_DELTA:
            self.__resetServerBubbleCount()
        else:
            self.__resetClientBubbleCount()

    def __resetServerBubbleCount(self):
        BigWorld.player().referralProgram.resetRecruitDelta(None)
        self.__clearBubbleTimeout()
        self.__recruitDeltaInc = 0
        return

    def __resetClientBubbleCount(self):
        AccountSettings.setCounters(REFERRAL_COUNTER, 0)
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
