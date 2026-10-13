# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/event_banners/standard_event_banner.py
from __future__ import absolute_import
import typing
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState
from gui.impl.lobby.user_missions.hangar_widget.event_banners.base_event_banner import BaseEventBanner
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.user_missions.widget.event_banner_model import EventBannerModel

class StandardEventBanner(BaseEventBanner):

    @property
    def bannerState(self):
        return EventBannerState.INACTIVE

    @property
    def isMode(self):
        return False

    @property
    def hasRewards(self):
        return False

    @property
    def borderColor(self):
        pass

    @property
    def title(self):
        pass

    @property
    def iconsPath(self):
        pass

    @property
    def videosPath(self):
        pass

    @property
    def introDescription(self):
        pass

    @property
    def inProgressDescription(self):
        pass

    @property
    def timerText(self):
        pass

    @property
    def timerValue(self):
        pass

    @property
    def eventStartDate(self):
        pass

    @property
    def eventEndDate(self):
        pass

    @property
    def playAppearAnim(self):
        return False

    def fillModel(self, model):
        super(StandardEventBanner, self).fillModel(model)
        model.setIsMode(self.isMode)
        model.setTitle(self.title)
        model.setHasRewards(self.hasRewards)
        model.setIntroDescription(self.introDescription)
        model.setInProgressDescription(self.inProgressDescription)
        model.setBannerState(self.bannerState)
        model.setIconsPath(self.iconsPath)
        model.setVideosPath(self.videosPath)
        model.setBorderColor(self.borderColor)
        model.setTimerText(self.timerText)
        model.setTimerValue(self.timerValue)
        model.setEventEndDate(self.eventEndDate)
        model.setEventStartDate(self.eventStartDate)
