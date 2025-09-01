# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/ls_entry_point.py
import typing
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from helpers import dependency, time_utils
from last_stand_common.last_stand_constants import DailyMissionsSettings
from last_stand.gui.impl.lobby.ls_helpers import isQuestCompleted
from last_stand.gui.impl.lobby.tooltips.event_banner_tooltip import EventBannerTooltipView
from last_stand.gui.ls_account_settings import AccountSettingsKeys, getSettings, setSettings
from last_stand.gui.scaleform.genConsts.LAST_STAND_HANGAR_ALIASES import LAST_STAND_HANGAR_ALIASES
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf import View, ViewEvent

@dependency.replace_none_kwargs(ctrl=ILSController)
def isLSEntryPointAvailable(ctrl=None):
    return ctrl.isAvailable()


class LSEventBanner(BaseEventBanner):
    NAME = LAST_STAND_HANGAR_ALIASES.LS_ENTRY_POINT
    _lsCtrl = dependency.descriptor(ILSController)
    _lsArtefactsCtrl = dependency.descriptor(ILSArtefactsController)
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(LSEventBanner, self).__init__()
        self._state = EventBannerState.IN_PROGRESS
        self._timerValue = 0
        self._playAppearAnim = False

    @property
    def isMode(self):
        return True

    @property
    def introDescription(self):
        res = R.strings.hangar_event_banners.event.LSEntryPoint
        return backport.text(res.intro.description())

    @property
    def inProgressDescription(self):
        res = R.strings.hangar_event_banners.event.LSEntryPoint
        return backport.text(res.completed.description()) if self._lsArtefactsCtrl.isProgressCompleted() and isQuestCompleted(DailyMissionsSettings.BADGE_MISSION_QUEST) else backport.text(res.inProgress.description())

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
        if self._lsCtrl.isAvailable():
            self._lsCtrl.selectBattle()

    def prepare(self):
        self._state = self.__getState()
        self._playAppearAnim = False
        if not getSettings(AccountSettingsKeys.IS_BANNER_FIRST_APPEARANCE_SEEN):
            self._playAppearAnim = True
            setSettings(AccountSettingsKeys.IS_BANNER_FIRST_APPEARANCE_SEEN, True)
        self._timerValue = int(time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(self._lsCtrl.getModeSettings().endDate)))

    def onAppear(self):
        if self._isVisible:
            return
        super(LSEventBanner, self).onAppear()
        self._lsCtrl.onSettingsUpdate += self.__onUpdate
        self._lsCtrl.onEventDisabled += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        super(LSEventBanner, self).onDisappear()
        self._lsCtrl.onSettingsUpdate -= self.__onUpdate
        self._lsCtrl.onEventDisabled -= self.__onUpdate

    def __getState(self):
        if not self._lsCtrl.isAvailable():
            return EventBannerState.INACTIVE
        return EventBannerState.INTRO if getSettings(AccountSettingsKeys.IS_EVENT_NEW) else EventBannerState.IN_PROGRESS

    def __onUpdate(self, *_):
        if self._lsCtrl.isAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()
