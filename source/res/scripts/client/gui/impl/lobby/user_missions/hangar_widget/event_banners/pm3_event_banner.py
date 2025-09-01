# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/event_banners/pm3_event_banner.py
from account_helpers.settings_core.settings_constants import PersonalMission3
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.missions.widget.pm3_banner_tooltip_view_model import BannerTypeEnum
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.tooltips.pm3_banner_tooltip import PM3BannerTooltipView
from gui.shared.event_dispatcher import showPersonalMissionMainWindow, showPersonalMissionCampaignSelectorWindow
from gui.impl.lobby.personal_missions_30.views_helpers import isIntroShown, isBannerAnimationShown, markBannerAnimationShown
from gui.impl.lobby.personal_missions_30.personal_mission_constants import IntroKeys, OperationIDs

class PM3BaseEventBanner(BaseEventBanner):

    @property
    def playAppearAnim(self):
        return True if not isBannerAnimationShown(PersonalMission3.PM_BANNER_ANIMATION_KEY) else False

    def onAppearAnimationPlayed(self):
        markBannerAnimationShown(PersonalMission3.PM_BANNER_ANIMATION_KEY)


class PM3EventBannerTeaser(PM3BaseEventBanner):
    NAME = 'PM3EntryPointTeaser'

    @property
    def bannerState(self):
        return EventBannerState.INTRO

    @property
    def introDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.PM3EntryPoint.intro.description())

    @property
    def borderColor(self):
        return '' if isIntroShown(IntroKeys.MAIN_INTRO_VIEW.value) else '#00FFAE'

    def createToolTipContent(self, event):
        return PM3BannerTooltipView(bannerType=BannerTypeEnum.PM3ENTRYPOINTTEASER)

    def onClick(self):
        showPersonalMissionCampaignSelectorWindow()


class PM3EventBannerOperation1(PM3BaseEventBanner):
    NAME = 'PM3EntryPointOperation1'

    @property
    def bannerState(self):
        return EventBannerState.IN_PROGRESS

    @property
    def inProgressDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.PM3EntryPoint.inProgress.description())

    def createToolTipContent(self, event):
        return PM3BannerTooltipView(bannerType=BannerTypeEnum.PM3ENTRYPOINTOPERATION1)

    def onClick(self):
        showPersonalMissionMainWindow(OperationIDs.OPERATION_FIRST.value)


class PM3EventBannerOperation2(PM3BaseEventBanner):
    NAME = 'PM3EntryPointOperation2'

    @property
    def bannerState(self):
        return EventBannerState.IN_PROGRESS

    @property
    def inProgressDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.PM3EntryPoint.inProgress.description())

    def createToolTipContent(self, event):
        return PM3BannerTooltipView(bannerType=BannerTypeEnum.PM3ENTRYPOINTOPERATION2)

    def onClick(self):
        showPersonalMissionMainWindow(OperationIDs.OPERATION_SECOND.value)


class PM3EventBannerOperation3(PM3BaseEventBanner):
    NAME = 'PM3EntryPointOperation3'

    @property
    def bannerState(self):
        return EventBannerState.IN_PROGRESS

    @property
    def inProgressDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.PM3EntryPoint.inProgress.description())

    def createToolTipContent(self, event):
        return PM3BannerTooltipView(bannerType=BannerTypeEnum.PM3ENTRYPOINTOPERATION3)

    def onClick(self):
        showPersonalMissionMainWindow(OperationIDs.OPERATION_THIRD.value)
