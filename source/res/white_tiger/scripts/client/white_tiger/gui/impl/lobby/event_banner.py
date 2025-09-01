# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/event_banner.py
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.shared.utils.SelectorBattleTypesUtils import isKnownBattleType
from gui.shared.utils.scheduled_notifications import Notifiable, AcyclicNotifier
from helpers import dependency, time_utils
from white_tiger.gui.game_control.white_tiger_controller import WhiteTigerController
from white_tiger.gui.impl.lobby.tooltips.banner_tooltip import EventBannerTooltipView
from white_tiger.gui.white_tiger_account_settings import isBannerSeen, setBannerSeen
from white_tiger.gui.white_tiger_gui_constants import SELECTOR_BATTLE_TYPES
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.gui.shared.event_dispatcher import showWelcomeScreen

class WhiteTigerEventBanner(BaseEventBanner, Notifiable):
    NAME = 'WhiteTigerEntryPoint'
    _wtController = dependency.descriptor(IWhiteTigerController)
    _wtEconomicsController = dependency.descriptor(IEconomicsController)

    def __init__(self):
        self._isVisible = True
        super(WhiteTigerEventBanner, self).__init__()
        self._state = EventBannerState.INACTIVE
        self._timerValue = 0
        self._playAppearAnim = False
        self._isAnnouncement = False

    @property
    def bannerState(self):
        return self._state

    @property
    def isMode(self):
        return True

    @property
    def borderColor(self):
        pass

    @property
    def timerValue(self):
        return self._timerValue

    @property
    def eventStartDate(self):
        return self._wtController.getStartDate()

    @property
    def eventEndDate(self):
        return self._wtController.getEndDate()

    @property
    def playAppearAnim(self):
        return self._playAppearAnim

    def createToolTipContent(self, event):
        return EventBannerTooltipView(self._state, self._isAnnouncement)

    def onClick(self):
        if self._state == EventBannerState.ANNOUNCE or self._isAnnouncement:
            showWelcomeScreen()
            return
        if self._state == EventBannerState.INACTIVE:
            if not self._timerValue:
                showWelcomeScreen()
                return
        self._wtController.selectBattle()

    def prepare(self):
        self._playAppearAnim = not isBannerSeen()
        self._timerValue = 0
        self._isAnnouncement = False
        isAnnouncement = self._wtController.isInAnnouncement()
        if self._wtController.isEnabled() and not self._wtController.isFrozen() and isAnnouncement:
            timeToStart = self._wtController.getStartDate()
            now = time_utils.getCurrentLocalServerTimestamp()
            deltaToStart = timeToStart - now
            if deltaToStart <= time_utils.ONE_DAY:
                self._timerValue = deltaToStart
                self._state = EventBannerState.INACTIVE
                self._isAnnouncement = True
                return
            self._state = EventBannerState.ANNOUNCE
            self.clearNotification()
            self.addNotificator(AcyclicNotifier(lambda : deltaToStart - time_utils.ONE_DAY, self._onUpdate))
            self.startNotification()
            return
        if not self._wtController.isAvailable():
            self._state = EventBannerState.INACTIVE
            return
        if not isKnownBattleType(SELECTOR_BATTLE_TYPES.WHITE_TIGER):
            self._state = EventBannerState.INTRO
            return
        _, _, isPrimeNow = self._wtController.getPrimeTimeStatus()
        if not isPrimeNow:
            self._state = EventBannerState.INACTIVE
            self._timerValue = self._wtController.getLeftTimeToPrimeTimesEnd()
            return
        self._timerValue = self._wtController.getTimeLeft()
        self._state = EventBannerState.IN_PROGRESS

    def onAppear(self):
        if self._isVisible:
            return
        if not isBannerSeen():
            setBannerSeen()
        super(WhiteTigerEventBanner, self).onAppear()
        self._wtController.onPrimeTimeStatusUpdated += self._onUpdate

    def _onUpdate(self, *args, **kwargs):
        self.clearNotification()
        EventBannersContainer().onBannerUpdate(self)

    def onDisappear(self):
        if not self._isVisible:
            return
        super(WhiteTigerEventBanner, self).onDisappear()
        self._wtController.onPrimeTimeStatusUpdated -= self._onUpdate
        self.clearNotification()
