# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/event_banners/base_event_banner.py
from abc import ABCMeta
from helpers import time_utils
from gui.impl.gen.view_models.views.lobby.user_missions.constants.event_banner_state import EventBannerState

class BaseEventBanner(object):
    __metaclass__ = ABCMeta
    NAME = ''

    def __init__(self):
        super(BaseEventBanner, self).__init__()
        self._isVisible = False

    @property
    def bannerState(self):
        return EventBannerState.INACTIVE

    @property
    def isMode(self):
        return False

    @property
    def borderColor(self):
        pass

    @property
    def introDescription(self):
        pass

    @property
    def inProgressDescription(self):
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

    @property
    def showTimerBeforeEventEnd(self):
        hoursBeforeEnd = 72
        return hoursBeforeEnd * time_utils.ONE_HOUR

    def createToolTipContent(self, event):
        return None

    def onClick(self):
        pass

    def onAppearAnimationPlayed(self):
        pass

    def prepare(self):
        pass

    def onAppear(self):
        self._isVisible = True

    def onDisappear(self):
        self._isVisible = False
