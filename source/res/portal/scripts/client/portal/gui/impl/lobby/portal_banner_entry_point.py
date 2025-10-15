# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/portal_banner_entry_point.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.utils.scheduled_notifications import Notifiable
from helpers import dependency, time_utils
from portal.gui.impl.gen.view_models.views.lobby.banner_entry_point.portal_banner_entry_point_model import PortalBannerEntryPointModel, State
from portal.skeletons.portal_event_controller import IPortalEventController
from shared_utils import nextTick
from portal.gui.impl.lobby.tooltips.banner_tooltip import BannerTooltip
from portal_account_settings import setEventEntrypointIsNew
from gui.Scaleform.Waiting import Waiting
from helpers.CallbackDelayer import CallbackDelayer
from Event import Event, EventManager

@dependency.replace_none_kwargs(portalCtrl=IPortalEventController)
def isPortalBannerEntryPointAvailable(portalCtrl=None):
    return portalCtrl.isEnabled()


class PortalBannerEntryPointView(ViewImpl, Notifiable):
    __END_NOTIFICATIONS_PERIOD_LENGTH = time_utils.ONE_DAY
    __portalController = dependency.descriptor(IPortalEventController)
    _BANNER_WAIT_TICK = 0.2

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(layoutID=R.views.portal.lobby.PortalBannerEntryPoint(), flags=flags, model=PortalBannerEntryPointModel())
        self._em = EventManager()
        self.onAnimationFinished = Event(self._em)
        super(PortalBannerEntryPointView, self).__init__(settings)

    def createToolTipContent(self, event, contentID):
        return BannerTooltip() if contentID == R.views.portal.lobby.tooltips.BannerTooltip() else super(PortalBannerEntryPointView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def viewModel(self):
        return super(PortalBannerEntryPointView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PortalBannerEntryPointView, self)._initialize(*args, **kwargs)
        self.viewModel.onShowingAnimationFinish += self.onAnimationFinished
        self.viewModel.onOpen += self.__onClick
        self.__portalController.onPrimeTimeStatusUpdated += self.__onStatusUpdated

    def _finalize(self):
        if self.__callbackDelayer:
            self.__callbackDelayer.clearCallbacks()
        self.viewModel.onOpen -= self.__onClick
        self.viewModel.onShowingAnimationFinish -= self.onAnimationFinished
        self.__portalController.onPrimeTimeStatusUpdated -= self.__onStatusUpdated
        super(PortalBannerEntryPointView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(PortalBannerEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def _onLoaded(self, *args, **kwargs):
        super(PortalBannerEntryPointView, self)._onLoaded(*args, **kwargs)
        self.__callbackDelayer = CallbackDelayer()
        self.__callbackDelayer.delayCallback(self._BANNER_WAIT_TICK, self.__setBannerReady)

    def __onStatusUpdated(self, _):
        self.__updateState()

    def __onStatusTick(self):
        self.__updateState()

    def __onConfigChanged(self):
        self.__updateState()

    def __updateState(self):
        if isPortalBannerEntryPointAvailable():
            with self.viewModel.transaction() as tx:
                state, actualTime = self.__getPeriodStateAndActualTime()
                tx.setState(state)
                tx.setTimestamp(actualTime or 0)
                tx.setPerformance(self.__portalController.getPerformanceGroup())
        else:
            nextTick(self.destroy)()

    def __getPeriodStateAndActualTime(self):
        if not self.__portalController.isAvailable():
            return (State.DISABLED, 0)
        currentSeason = self.__portalController.getCurrentSeason()
        return (State.ACTIVE, currentSeason.getEndDate())

    def __onClick(self):
        setEventEntrypointIsNew(False)
        self.__portalController.selectPortal()

    def __setBannerReady(self):
        if not Waiting.isVisible():
            self.viewModel.setIsAnimated(True)
            return None
        else:
            return self._BANNER_WAIT_TICK
