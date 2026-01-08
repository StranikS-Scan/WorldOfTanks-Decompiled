# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/event_banner.py
from __future__ import absolute_import
from account_helpers.AccountSettings import ResourceWell
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from resource_well.gui.feature.constants import PurchaseMode
from resource_well.gui.feature.resource_well_helpers import isBannerSettingSet, setBannerSettings
from resource_well.gui.impl.lobby.feature.tooltips.event_banner_tooltip import EventBannerTooltip
from resource_well.gui.shared.event_dispatcher import showMainWindow
from shared_utils import first
from skeletons.gui.resource_well import IResourceWellController

@dependency.replace_none_kwargs(resourceWell=IResourceWellController)
def isResourceWellEventBannerAvailable(resourceWell=None):
    return resourceWell.isEnabled()


class ResourceWellEventBanner(BaseEventBanner):
    NAME = HANGAR_ALIASES.RESOURCE_WELL_EVENT_BANNER
    __resourceWell = dependency.descriptor(IResourceWellController)
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(ResourceWellEventBanner, self).__init__()
        self._state = ''
        self._eventStartDate = 0
        self._eventEndDate = 0
        self._timerValue = 0
        self._playAppearAnim = False
        self._callbackDelayer = None
        return

    @property
    def isMode(self):
        return False

    @property
    def introDescription(self):
        return self.__getDescriptionText()

    @property
    def inProgressDescription(self):
        return self.__getDescriptionText()

    @property
    def borderColor(self):
        pass

    @property
    def bannerState(self):
        return self._state

    @property
    def timerValue(self):
        return self._timerValue

    @property
    def eventStartDate(self):
        return self._eventStartDate

    @property
    def eventEndDate(self):
        return self._eventEndDate

    @property
    def playAppearAnim(self):
        return self._playAppearAnim

    @property
    def showTimerBeforeEventEnd(self):
        return time_utils.ONE_DAY

    def createToolTipContent(self, event):
        return EventBannerTooltip()

    def onClick(self):
        if not self.__resourceWell.isStarted() or self.__resourceWell.isFinished():
            return
        if not isBannerSettingSet(ResourceWell.FIRST_BANNER_ENTERING_MADE):
            setBannerSettings(ResourceWell.FIRST_BANNER_ENTERING_MADE)
        showMainWindow()

    def prepare(self):
        self._state = self.__getState()
        self._eventStartDate = 0
        self._eventEndDate = 0
        self._timerValue = 0
        self._playAppearAnim = False
        if not isBannerSettingSet(ResourceWell.IS_BANNER_FIRST_APPEARANCE_SEEN):
            self._playAppearAnim = True
            setBannerSettings(ResourceWell.IS_BANNER_FIRST_APPEARANCE_SEEN)
        if self._state == EventBannerState.ANNOUNCE:
            self._eventStartDate = self.__resourceWell.config.startTime
            self._eventEndDate = self.__resourceWell.config.finishTime
            self._callbackDelayer = self._callbackDelayer or CallbackDelayer()
            self._callbackDelayer.delayCallback(self.__resourceWell.config.startTime - self.showTimerBeforeEventEnd - time_utils.getServerUTCTime(), self.__onUpdate)
        elif self._state == EventBannerState.INACTIVE:
            self._timerValue = self.__resourceWell.config.startTime - time_utils.getServerUTCTime()
        else:
            self._timerValue = max(self.__resourceWell.config.finishTime - time_utils.getServerUTCTime(), 1)

    def onAppear(self):
        if self._isVisible:
            return
        super(ResourceWellEventBanner, self).onAppear()
        self.__resourceWell.onSettingsChanged += self.__onUpdate
        self.__resourceWell.onEventUpdated += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        else:
            super(ResourceWellEventBanner, self).onDisappear()
            if self._callbackDelayer is not None:
                self._callbackDelayer.destroy()
                self._callbackDelayer = None
            self.__resourceWell.onSettingsChanged -= self.__onUpdate
            self.__resourceWell.onEventUpdated -= self.__onUpdate
            return

    def __getState(self):
        if self.__resourceWell.isNotStarted() and not self.__resourceWell.isActive():
            timeBeforeStart = self.__resourceWell.config.startTime - time_utils.getServerUTCTime()
            if timeBeforeStart > time_utils.ONE_DAY:
                return EventBannerState.ANNOUNCE
            return EventBannerState.INACTIVE
        return EventBannerState.INTRO if not isBannerSettingSet(ResourceWell.FIRST_BANNER_ENTERING_MADE) else EventBannerState.IN_PROGRESS

    def __onUpdate(self, *_):
        if self.__resourceWell.isEnabled():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()

    def __getDescriptionText(self):
        res = R.strings.hangar_event_banners.event.resourceWellEventBanner
        if self.__resourceWell.getPurchaseMode() != PurchaseMode.TWO_PARALLEL_PRODUCTS:
            rewardID, _ = first(self.__resourceWell.config.getSortedRewardsByOrder(), (None,))
            if rewardID is not None:
                vehicleReward = self.__resourceWell.getRewardVehicle(rewardID)
                if vehicleReward is not None:
                    return backport.text(res.description.singleVehicle(), vehicleName=vehicleReward.shortUserName)
        return backport.text(res.description.severalVehicles())
