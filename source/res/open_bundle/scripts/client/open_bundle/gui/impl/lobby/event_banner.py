# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/event_banner.py
from __future__ import absolute_import
from account_helpers import AccountSettings
from account_helpers.AccountSettings import OPEN_BUNDLE_ENTRY_POINT_SHOWN, OPEN_BUNDLE_ENTRY_POINT_ANIMATION_SHOWN
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from helpers import dependency, time_utils
from open_bundle.gui.constants import OPEN_BUNDLE_ENTRY_POINT_NAME
from open_bundle.gui.impl.lobby.tooltips.event_banner_tooltip import EventBannerTooltip
from open_bundle.gui.shared.event_dispatcher import showOpenBundleMainView
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from shared_utils import findFirst

@dependency.replace_none_kwargs(openBundle=IOpenBundleController)
def isOpenBundleEntryPointAvailable(openBundle=None):
    bundleID = findFirst(openBundle.isBundleActive, openBundle.bundleIDs)
    return bundleID is not None and not openBundle.isAllBundleCellsReceived(bundleID)


class OpenBundleEventBanner(BaseEventBanner):
    NAME = OPEN_BUNDLE_ENTRY_POINT_NAME
    __eventsService = dependency.descriptor(IEventsService)
    __openBundle = dependency.descriptor(IOpenBundleController)

    def __init__(self):
        super(OpenBundleEventBanner, self).__init__()
        self.__state = EventBannerState.IN_PROGRESS
        self.__timerValue = 0
        self.__bundleID = None
        self.__playAppearAnim = False
        return

    @property
    def bannerState(self):
        return self.__state

    @property
    def borderColor(self):
        pass

    def prepare(self):
        self.__bundleID = findFirst(self.__openBundle.isBundleActive, self.__openBundle.bundleIDs)
        self.__state = self.__getState()
        self.__timerValue = self.__openBundle.getBundleTimeLeft(self.__bundleID)
        self.__playAppearAnim = False
        settings = AccountSettings.getSettings(OPEN_BUNDLE_ENTRY_POINT_ANIMATION_SHOWN)
        if self.__bundleID not in settings:
            self.__playAppearAnim = True
            settings.add(self.__bundleID)
            AccountSettings.setSettings(OPEN_BUNDLE_ENTRY_POINT_ANIMATION_SHOWN, settings)

    @property
    def showTimerBeforeEventEnd(self):
        hoursBeforeEnd = 24
        return hoursBeforeEnd * time_utils.ONE_HOUR

    @property
    def timerValue(self):
        return self.__timerValue

    @property
    def playAppearAnim(self):
        return self.__playAppearAnim

    def createToolTipContent(self, event):
        return EventBannerTooltip(bundleID=self.__bundleID)

    def onClick(self):
        if self.__openBundle.isBundleActive(bundleID=self.__bundleID):
            settings = AccountSettings.getSettings(OPEN_BUNDLE_ENTRY_POINT_SHOWN)
            if self.__bundleID not in settings:
                settings.add(self.__bundleID)
                AccountSettings.setSettings(OPEN_BUNDLE_ENTRY_POINT_SHOWN, settings)
            showOpenBundleMainView(bundleID=self.__bundleID)

    def onAppear(self):
        if self._isVisible:
            return
        super(OpenBundleEventBanner, self).onAppear()
        self.__openBundle.onSettingsChanged += self.__onUpdate
        self.__openBundle.onStatusChanged += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        super(OpenBundleEventBanner, self).onDisappear()
        self.__openBundle.onSettingsChanged -= self.__onUpdate
        self.__openBundle.onStatusChanged -= self.__onUpdate

    def __onUpdate(self, *_):
        if isOpenBundleEntryPointAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()

    def __getState(self):
        if not self.__openBundle.isBundleActive(self.__bundleID):
            return EventBannerState.INACTIVE
        return EventBannerState.INTRO if self.__bundleID not in AccountSettings.getSettings(OPEN_BUNDLE_ENTRY_POINT_SHOWN) else EventBannerState.IN_PROGRESS
