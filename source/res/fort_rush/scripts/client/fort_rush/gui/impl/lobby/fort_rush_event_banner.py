# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/fort_rush_event_banner.py
from __future__ import absolute_import
import logging
from fort_rush.account_helpers.account_settings import isBannerSeen, setBannerSeen
from fort_rush.gui.fort_rush_gui_constants import SELECTOR_BATTLE_TYPES, FORT_RUSH_HANGAR_ALIASES
from fort_rush.gui.impl.lobby.tooltips.fort_rush_event_banner_tooltip import FortRushEventBannerTooltipView
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.event_banners.standard_event_banner import StandardEventBanner
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.shared.utils.SelectorBattleTypesUtils import isKnownBattleType
from helpers import dependency
from helpers.time_utils import getTimestampFromUTC, utcToLocalDatetime
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

def isFortRushEntryPointAvailable():
    ctrl = dependency.instance(IFortRushBattleController)
    if ctrl is None:
        _logger.warning('[FORT_RUSH][FortRushEventBanner] Entry point: controller not available')
        return False
    else:
        isEnabled = ctrl.isAvailable()
        return isEnabled


class FortRushEventBanner(StandardEventBanner):
    NAME = FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_ENTRY_POINT
    __frCtrl = dependency.descriptor(IFortRushBattleController)
    __eventsService = dependency.descriptor(IEventsService)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(FortRushEventBanner, self).__init__()
        self._state = EventBannerState.INACTIVE
        self._timerValue = 0
        self._playAppearAnim = False

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
        return getTimestampFromUTC(utcToLocalDatetime(self.__frCtrl.getConfig().startDatetime).timetuple())

    @property
    def eventEndDate(self):
        return getTimestampFromUTC(utcToLocalDatetime(self.__frCtrl.getConfig().endDatetime).timetuple())

    @property
    def playAppearAnim(self):
        return self._playAppearAnim

    def createToolTipContent(self, event):
        return FortRushEventBannerTooltipView(self._state)

    def onClick(self):
        self.__frCtrl.selectBattle()

    def prepare(self):
        self._playAppearAnim = not isBannerSeen()
        self._timerValue = 0
        if not self.__frCtrl.isAvailable():
            self._state = EventBannerState.INACTIVE
            return
        if not isKnownBattleType(SELECTOR_BATTLE_TYPES.FORT_RUSH):
            self._state = EventBannerState.INTRO
            return
        self._timerValue = self.__frCtrl.getTimeLeft()
        self._state = EventBannerState.IN_PROGRESS

    def onAppear(self):
        if self._isVisible:
            return
        if not isBannerSeen():
            setBannerSeen()
        super(FortRushEventBanner, self).onAppear()
        self.__eventsCache.onSyncCompleted += self.__onUpdate
        self.__frCtrl.onConfigUpdated += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        super(FortRushEventBanner, self).onDisappear()
        self.__eventsCache.onSyncCompleted -= self.__onUpdate
        self.__frCtrl.onConfigUpdated -= self.__onUpdate

    def __onUpdate(self, *_):
        if self.__frCtrl.isAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()
