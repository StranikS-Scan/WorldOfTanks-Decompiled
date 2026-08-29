# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/event_banners/pm4_event_banner.py
from __future__ import absolute_import
from account_helpers.settings_core.settings_constants import PersonalMission4
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.personal_missions_30.personal_mission_constants import OperationIDs
from gui.impl.lobby.personal_missions_30.views_helpers import isPM4BannerAnimationShown, isIntroShown, markPM4BannerAnimationShown
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
from gui.impl.lobby.user_missions.tooltips.pm4_banner_tooltip import PM4BannerTooltipView
from gui.shared.event_dispatcher import showPersonalMissionMainWindow
from personal_missions import PM_BRANCH

class PM4EventBunner(BaseEventBanner):
    NAME = 'PM4EntryPoint'

    @property
    def playAppearAnim(self):
        return not isPM4BannerAnimationShown()

    @property
    def bannerState(self):
        return EventBannerState.INTRO

    @property
    def introDescription(self):
        return backport.text(R.strings.hangar_event_banners.event.PM4EntryPoint.description())

    @property
    def borderColor(self):
        return '' if isIntroShown(PersonalMission4.INTRO_OP_11, PM_BRANCH.PERSONAL_MISSION_4) else '#00FFAE'

    def createToolTipContent(self, event):
        return PM4BannerTooltipView()

    def onAppearAnimationPlayed(self):
        markPM4BannerAnimationShown()

    def onClick(self):
        showPersonalMissionMainWindow(OperationIDs.OPERATION_FOURTH.value)
