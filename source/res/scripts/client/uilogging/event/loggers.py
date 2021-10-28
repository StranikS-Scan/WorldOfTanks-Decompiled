# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/event/loggers.py
from uilogging.base.logger import BaseLogger
from uilogging.base.mixins import TimedActionMixin
from uilogging.event.constants import FEATURE, LOG_ACTIONS

class EventLogger(TimedActionMixin, BaseLogger):

    def __init__(self, group):
        super(EventLogger, self).__init__(FEATURE, group)

    def videoStarted(self):
        self.startAction(LOG_ACTIONS.PLAY_VIDEO.value)

    def videoStopped(self, videoID):
        self.stopAction(LOG_ACTIONS.PLAY_VIDEO.value, additional_info='video_%s' % videoID)
