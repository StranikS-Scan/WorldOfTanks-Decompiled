# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/halloween_event_banner.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.event_banners.standard_event_banner import StandardEventBanner
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from halloween.gui.halloween_account_settings import AccountSettingsKeys, getSettings, setSettings
from halloween.gui.impl.lobby.tooltips.event_banner_tooltip import EventBannerTooltipView
from halloween.gui.scaleform.genConsts.HALLOWEEN_HANGAR_ALIASES import HALLOWEEN_HANGAR_ALIASES
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys
from helpers import dependency, time_utils
from halloween.skeletons.halloween_controller import IHalloweenController

@dependency.replace_none_kwargs(ctrl=IHalloweenController)
def isHalloweenEntryPointAvailable(ctrl=None):
    return ctrl.isAvailable()


class HalloweenEventBanner(StandardEventBanner):
    NAME = HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_ENTRY_POINT
    _halloweenCtrl = dependency.descriptor(IHalloweenController)
    _hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(HalloweenEventBanner, self).__init__()
        self._state = EventBannerState.IN_PROGRESS
        self._timerValue = 0
        self._playAppearAnim = False
        self.__uiLogger = HWMetricsLogger(HWLogKeys.RANDOM_LOBBY)

    @property
    def isMode(self):
        return True

    @property
    def inProgressDescription(self):
        res = R.strings.hangar_event_banners.event.HalloweenEntryPoint
        return backport.text(res.completed.description()) if self._hwArtefactsCtrl.isProgressCompleted() else backport.text(res.inProgress.description())

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
    def playAppearAnim(self):
        return self._playAppearAnim

    @property
    def showTimerBeforeEventEnd(self):
        return time_utils.ONE_DAY

    def createToolTipContent(self, event):
        return EventBannerTooltipView()

    def onClick(self):
        if self._halloweenCtrl.isAvailable():
            self._halloweenCtrl.selectBattle(source=HWLogKeys.UMG_BANNER)

    def prepare(self):
        self._state = self.__getState()
        self._playAppearAnim = False
        if not getSettings(AccountSettingsKeys.IS_BANNER_FIRST_APPEARANCE_SEEN):
            self._playAppearAnim = True
            setSettings(AccountSettingsKeys.IS_BANNER_FIRST_APPEARANCE_SEEN, True)
        self._timerValue = int(time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(self._halloweenCtrl.getModeSettings().endDate)))

    def onAppear(self):
        if self._isVisible:
            return
        super(HalloweenEventBanner, self).onAppear()
        self._halloweenCtrl.onSettingsUpdate += self.__onUpdate
        self._halloweenCtrl.onEventDisabled += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        super(HalloweenEventBanner, self).onDisappear()
        self._halloweenCtrl.onSettingsUpdate -= self.__onUpdate
        self._halloweenCtrl.onEventDisabled -= self.__onUpdate

    def __getState(self):
        if not self._halloweenCtrl.isAvailable():
            return EventBannerState.INACTIVE
        return EventBannerState.INTRO if getSettings(AccountSettingsKeys.IS_EVENT_NEW) else EventBannerState.IN_PROGRESS

    def __onUpdate(self, *_):
        if self._halloweenCtrl.isAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self._eventsService.updateEntries()
