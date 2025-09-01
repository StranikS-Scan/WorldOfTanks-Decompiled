# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/event_banner.py
from account_helpers.AccountSettings import AccountSettings
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_shared
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from helpers.time_utils import getCurrentLocalServerTimestamp
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from helpers import int2roman, dependency

class Comp7CoreEventBanner(BaseEventBanner):
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(Comp7CoreEventBanner, self).__init__()
        self._state = ''
        self._eventStartDate = 0
        self._eventEndDate = 0
        self._timerValue = 0
        self._playAppearAnim = False

    @property
    def _modeController(self):
        raise NotImplementedError

    @property
    def _seasonStateClazz(self):
        raise NotImplementedError

    @property
    def _accountSettingsTimestampFlag(self):
        raise NotImplementedError

    @property
    def _selectorBattleType(self):
        raise NotImplementedError

    @staticmethod
    def _selectMode():
        raise NotImplementedError

    @property
    def _vehicleLevel(self):
        return int2roman(self._modeController.getModeSettings().levels[0])

    @property
    def isMode(self):
        return True

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

    @staticmethod
    def isEntryPointAvailable(modeCtrl=None):
        return NotImplementedError

    def prepare(self):
        self._eventStartDate = 0
        self._eventEndDate = 0
        self._timerValue = 0
        self._playAppearAnim = False
        self._state = comp7_core_shared.getEventBannerState(self._modeController, self._seasonStateClazz, self._selectorBattleType)
        season = self._modeController.getCurrentSeason(includePreannounced=True) or self._modeController.getNextSeason()
        if season is None:
            return
        else:
            seasonState = comp7_core_shared.getModeSeasonState(self._modeController, self._seasonStateClazz)
            seasonStartDate = season.getStartDate()
            if seasonState == seasonState.NOTSTARTED:
                self._eventStartDate = seasonStartDate
                self._eventEndDate = season.getEndDate()
            if seasonState == seasonState.ENDSOON:
                self._timerValue = int(season.getEndDate() - getCurrentLocalServerTimestamp())
            if self._state == EventBannerState.INACTIVE:
                self._timerValue = int(self._modeController.getPeriodInfo().primeDelta)
            savedAppearTime = AccountSettings.getSettings(self._accountSettingsTimestampFlag)
            if savedAppearTime != seasonStartDate:
                self._playAppearAnim = True
                AccountSettings.setSettings(self._accountSettingsTimestampFlag, seasonStartDate)
            return

    def onClick(self):
        if self._modeController.isAvailable():
            self._selectMode()
            if self._modeController.getCurrentSeason() is not None:
                selectorUtils.setBattleTypeAsKnown(self._selectorBattleType)
        return

    def onAppear(self):
        if self._isVisible:
            return
        super(Comp7CoreEventBanner, self).onAppear()
        self._modeController.onModeConfigChanged += self.__onUpdate
        self._modeController.onStatusUpdated += self.__onUpdate
        self._modeController.onStatusTick += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        super(Comp7CoreEventBanner, self).onDisappear()
        self._modeController.onModeConfigChanged -= self.__onUpdate
        self._modeController.onStatusUpdated -= self.__onUpdate
        self._modeController.onStatusTick -= self.__onUpdate

    def createToolTipContent(self, event):
        super(Comp7CoreEventBanner, self).createToolTipContent(event)
        self.prepare()

    def __onUpdate(self, *_):
        if self.isEntryPointAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()
