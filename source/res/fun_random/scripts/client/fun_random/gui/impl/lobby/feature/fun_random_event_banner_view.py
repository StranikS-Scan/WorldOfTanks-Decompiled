# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_event_banner_view.py
from __future__ import absolute_import
import typing
from account_helpers.AccountSettings import AccountSettings, FUN_RANDOM_BANNER_INTRO_CLICK_TIMESTAMP
from adisp import adisp_process
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin, FunSubModesWatcher
from skeletons.gui.game_control import IFunRandomController
from fun_random.gui.impl.lobby.tooltips.fun_random_entry_point_tooltip_view import FunRandomEntryPointTooltipView
from fun_random.gui.impl.lobby.common.fun_view_helpers import getFunRandomEventState
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.hangar_widget.event_banners.event_banners_container import EventBannersContainer
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from helpers import dependency
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf import View, ViewEvent

@dependency.replace_none_kwargs(funRandomCtrl=IFunRandomController)
def isFunRandomEntryPointAvailable(funRandomCtrl=None):
    return funRandomCtrl.subModesInfo.isEntryPointAvailable()


class FunRandomEventBannerView(BaseEventBanner, FunSubModesWatcher):
    NAME = FUNRANDOM_ALIASES.FUN_RANDOM_ENTRY_POINT
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(FunRandomEventBannerView, self).__init__()
        self.__state = None
        self.__timerValue = 0
        self.__eventStartDate = 0
        self.__eventEndDate = 0
        return

    @property
    def isMode(self):
        return True

    @property
    def title(self):
        return backport.text(FunAssetPacksMixin.getModeLocalsResRoot().capsUserName())

    @property
    def introDescription(self):
        return backport.text(FunAssetPacksMixin.getModeLocalsResRoot().entryPoint.intro.description())

    @property
    def inProgressDescription(self):
        return backport.text(FunAssetPacksMixin.getModeLocalsResRoot().entryPoint.inProgress.description())

    @property
    def iconsPath(self):
        assetsPointer = FunAssetPacksMixin.getModeAssetsPointer()
        return 'fun_random.gui.maps.icons.feature.asset_packs.modes.{}'.format(assetsPointer)

    @property
    def videosPath(self):
        assetsPointer = FunAssetPacksMixin.getModeAssetsPointer()
        return 'fun_random.asset_packs.modes.{}'.format(assetsPointer)

    @property
    def borderColor(self):
        pass

    @property
    def bannerState(self):
        return self.__state

    @property
    def eventStartDate(self):
        return self.__eventStartDate

    @property
    def eventEndDate(self):
        return self.__eventEndDate

    @property
    def timerValue(self):
        return self.__timerValue

    def prepare(self):
        status = self.getSubModesStatus()
        self.__state = getFunRandomEventState(status)
        self.__timerValue = status.primeDelta
        self.__eventStartDate = status.rightBorder
        self.__eventEndDate = status.endTime
        if self.__state == EventBannerState.IN_PROGRESS:
            savedClickTime = AccountSettings.getSettings(FUN_RANDOM_BANNER_INTRO_CLICK_TIMESTAMP)
            if savedClickTime < self.__eventStartDate:
                self.__state = EventBannerState.INTRO

    def createToolTipContent(self, event):
        return FunRandomEntryPointTooltipView()

    def onClick(self):
        self.__onSelectFunRandom()
        if self.__state == EventBannerState.INTRO:
            AccountSettings.setSettings(FUN_RANDOM_BANNER_INTRO_CLICK_TIMESTAMP, self.__eventStartDate)

    def onAppear(self):
        if self._isVisible:
            return
        super(FunRandomEventBannerView, self).onAppear()
        self.startSubStatusListening(self.__onUpdate)
        self.startSubSettingsListening(self.__onUpdate)

    def onDisappear(self):
        if not self._isVisible:
            return
        self.stopSubStatusListening(self.__onUpdate)
        self.stopSubSettingsListening(self.__onUpdate)
        super(FunRandomEventBannerView, self).onDisappear()

    def __onUpdate(self, *args):
        if self._funRandomCtrl.subModesInfo.isEntryPointAvailable():
            EventBannersContainer().onBannerUpdate(self)
        else:
            self.__eventsService.updateEntries()

    @adisp_process
    def __onSelectFunRandom(self):
        yield self.selectFunRandomBattle()
