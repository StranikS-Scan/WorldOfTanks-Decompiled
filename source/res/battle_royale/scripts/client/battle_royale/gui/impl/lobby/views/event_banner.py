# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/event_banner.py
from account_helpers.AccountSettings import AccountSettings, BATTLE_ROYALE_BANNER_FIRST_APPEARANCE_TIMESTAMP
from helpers import dependency
from helpers.time_utils import getCurrentLocalServerTimestamp
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.utils.SelectorBattleTypesUtils import isKnownBattleType
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from skeletons.gui.game_control import IBattleRoyaleController
from battle_royale.gui.constants import BattleRoyaleModeState
from battle_royale.gui.impl.lobby.tooltips.banner_tooltip_view import BannerTooltipView

@dependency.replace_none_kwargs(battleRoyaleController=IBattleRoyaleController)
def isBattleRoyaleEntryPointAvailable(battleRoyaleController=None):
    return battleRoyaleController.isActive()


class BattleRoyaleEventBanner(BaseEventBanner):
    NAME = 'BattleRoyaleEntryPoint'
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(BattleRoyaleEventBanner, self).__init__()
        self.__state = ''
        self.__timerValue = 0
        self.__playAppearAnim = False

    @property
    def bannerState(self):
        return self.__state

    @property
    def isMode(self):
        return True

    @property
    def borderColor(self):
        pass

    @property
    def introDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.BattleRoyaleEntryPoint.intro.description())

    @property
    def inProgressDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.BattleRoyaleEntryPoint.inProgress.description())

    @property
    def timerValue(self):
        return self.__timerValue

    @property
    def playAppearAnim(self):
        return self.__playAppearAnim

    def prepare(self):
        self.__playAppearAnim = False
        periodInfo = self.__battleRoyaleController.getPeriodInfo()
        if not self.__battleRoyaleController.isActive() or self.__battleRoyaleController.getModeState() != BattleRoyaleModeState.Regular:
            self.__state = EventBannerState.INACTIVE
            self.__timerValue = int(periodInfo.primeDelta)
        elif isKnownBattleType(SELECTOR_BATTLE_TYPES.BATTLE_ROYALE):
            self.__state = EventBannerState.IN_PROGRESS
            self.__timerValue = max(0, int(periodInfo.cycleBorderRight.timestamp - getCurrentLocalServerTimestamp()))
        else:
            self.__state = EventBannerState.INTRO
            self.__timerValue = 0
        savedAppearTime = AccountSettings.getSettings(BATTLE_ROYALE_BANNER_FIRST_APPEARANCE_TIMESTAMP)
        cycleStartDate = periodInfo.cycleBorderLeft.timestamp
        if savedAppearTime != cycleStartDate:
            self.__playAppearAnim = True
            AccountSettings.setSettings(BATTLE_ROYALE_BANNER_FIRST_APPEARANCE_TIMESTAMP, cycleStartDate)

    def createToolTipContent(self, event):
        return BannerTooltipView(modeState=self.bannerState)

    def onClick(self):
        self.__battleRoyaleController.selectRoyaleBattle()
        if self.__battleRoyaleController.getModeState() == BattleRoyaleModeState.Regular:
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.BATTLE_ROYALE)

    def onAppear(self):
        if self._isVisible:
            return
        super(BattleRoyaleEventBanner, self).onAppear()
        self.__battleRoyaleController.onEntryPointUpdated += self.__onUpdate

    def onDisappear(self):
        if not self._isVisible:
            return
        super(BattleRoyaleEventBanner, self).onDisappear()
        self.__battleRoyaleController.onEntryPointUpdated -= self.__onUpdate

    def __onUpdate(self, *_):
        if isBattleRoyaleEntryPointAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()
