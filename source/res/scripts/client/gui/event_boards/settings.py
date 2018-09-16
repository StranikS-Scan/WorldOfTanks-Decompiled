# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/event_boards/settings.py


class _EventBoardSettings(object):

    def __init__(self):
        self.__minimized = {}

    def isGroupMinimized(self, event):
        groupID = event.getEventID()
        return self.__minimized[groupID] if groupID in self.__minimized else event.isFinished()

    def updateExpanded(self, event, value):
        groupID = event.getEventID()
        self.__minimized[groupID] = not value


_settings = _EventBoardSettings()

def isGroupMinimized(event):
    return _settings.isGroupMinimized(event)


def expandGroup(event, isExpanded):
    _settings.updateExpanded(event, isExpanded)
