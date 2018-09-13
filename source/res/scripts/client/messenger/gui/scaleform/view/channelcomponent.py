# Embedded file name: scripts/client/messenger/gui/Scaleform/view/ChannelComponent.py
import weakref
import constants
from debug_utils import LOG_DEBUG
from messenger.gui import events_dispatcher
from messenger.gui.Scaleform.meta.ChannelComponentMeta import ChannelComponentMeta

class ChannelComponent(ChannelComponentMeta):

    def __init__(self):
        super(ChannelComponent, self).__init__()
        self._controller = lambda : None

    def __del__(self):
        LOG_DEBUG('ChannelComponent deleted', self)

    def setController(self, controller):
        controller.activate()
        events_dispatcher.notifyCarousel(controller.getChannel().getClientID(), notify=False)
        self._controller = weakref.ref(controller)
        if self.flashObject:
            self.as_setJoinedS(controller.isJoined())

    def removeController(self):
        self._controller = lambda : None
        if self.flashObject:
            self.as_setJoinedS(False)

    def close(self):
        if self._controller():
            self._controller().exit()

    def minimize(self):
        if self._controller():
            self._controller().deactivate()

    def getMessageMaxLength(self):
        return round(constants.CHAT_MESSAGE_MAX_LENGTH / 2, 0)

    def isJoined(self):
        isJoined = False
        if self._controller():
            isJoined = self._controller().isJoined()
        return isJoined

    def sendMessage(self, message):
        result = False
        if self._controller():
            result = self._controller().sendMessage(message)
        return result

    def getHistory(self):
        result = ''
        if self._controller():
            result = '\n'.join(self._controller().getHistory())
        return result
