# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/navigation_view_settings.py


class NavigationViewSettings(object):

    def __init__(self, viewId, viewContextSettings=None, previousViewSettings=None):
        if viewContextSettings is None:
            viewContextSettings = {}
        self.__viewId = viewId
        self.__viewContextSettings = viewContextSettings
        self.__previousViewSettings = previousViewSettings
        return

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def getViewId(self):
        return self.__viewId

    def getViewContextSettings(self):
        return self.__viewContextSettings

    def setViewContextSettings(self, settings):
        self.__viewContextSettings = settings

    def getPreviousViewSettings(self):
        return self.__previousViewSettings

    def setPreviousViewSettings(self, previousViewSettings):
        self.__previousViewSettings = previousViewSettings
