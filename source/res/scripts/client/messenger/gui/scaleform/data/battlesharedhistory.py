# Embedded file name: scripts/client/messenger/gui/Scaleform/data/BattleSharedHistory.py
from collections import deque
from debug_utils import LOG_WARNING
from messenger.gui.Scaleform import FILL_COLORS
from messenger.m_constants import BATTLE_SHARED_HISTORY_MAX_LEN

class BattleSharedHistory(object):

    def __init__(self, numberOfMessages):
        super(BattleSharedHistory, self).__init__()
        self.clear()
        self.__numberOfMessages = numberOfMessages
        self.__syncCursor = False

    def clear(self):
        self.__history = deque([], BATTLE_SHARED_HISTORY_MAX_LEN)
        self.__cursor = -1

    def numberOfMessages(self):
        return self.__numberOfMessages

    def isEnabled(self):
        return self.__numberOfMessages > 0

    def activate(self):
        self.__cursor = len(self.__history)

    def syncCursor(self, value):
        self.__syncCursor = value
        if value:
            self.activate()

    def deactivate(self):
        self.__cursor = -1

    def addMessage(self, message, fillColor = FILL_COLORS.BLACK):
        if self.isEnabled():
            self.__history.append((message, fillColor))
            if self.__syncCursor:
                self.next()

    def getNavControlsEnabled(self):
        prevControl = self.__cursor > self.__numberOfMessages
        toLastControl = self.__cursor < len(self.__history)
        nextControl = toLastControl
        if self.__cursor == len(self.__history):
            self.syncCursor(True)
        return (prevControl, nextControl, toLastControl)

    def getHistory(self):
        history = []
        if self.isEnabled() and self.__cursor > -1:
            start = self.__cursor - self.__numberOfMessages
            end = self.__cursor
            start = max(start, 0)
            temp = list(self.__history)
            history = temp[start:end]
        return history

    def next(self):
        if self.__cursor > -1:
            self.__cursor = min(len(self.__history), self.__cursor + 1)
        elif not self.isEnabled():
            LOG_WARNING('History is not enabled.', self.__numberOfMessages)
        else:
            LOG_WARNING('History is not activated.', self.__cursor)

    def prev(self):
        if self.__cursor > -1:
            self.__cursor = max(self.__numberOfMessages, self.__cursor - 1)
        elif not self.isEnabled():
            LOG_WARNING('History is not enabled.', self.__numberOfMessages)
        else:
            LOG_WARNING('History is not activated.', self.__cursor)
