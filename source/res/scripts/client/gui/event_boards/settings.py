# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/event_boards/settings.py


class _EventBoardSettings(object):
    """
    Session only settings data for event boards
    """

    def __init__(self):
        self.__minimized = {}

    def isGroupMinimized(self, event):
        id = event.getEventID()
        return self.__minimized[id] if id in self.__minimized else event.isFinished()

    def updateExpanded(self, event, value):
        id = event.getEventID()
        self.__minimized[id] = not value


_settings = _EventBoardSettings()

def isGroupMinimized(event):
    return _settings.isGroupMinimized(event)


def expandGroup(event, isExpanded):
    _settings.updateExpanded(event, isExpanded)
