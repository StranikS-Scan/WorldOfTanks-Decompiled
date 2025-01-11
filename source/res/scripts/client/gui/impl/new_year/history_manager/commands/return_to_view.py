# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/history_manager/commands/return_to_view.py
from gui.shared import EVENT_BUS_SCOPE

class ReturnToView(object):

    def __init__(self, context, backButtonText=None, scope=EVENT_BUS_SCOPE.LOBBY):
        self.__context = context
        self.__backButtonText = backButtonText
        self.__scope = scope

    def getBackButtonText(self):
        return self.__backButtonText

    def getContext(self):
        return self.__context

    def execute(self):
        raise NotImplementedError

    def updateContext(self, context):
        self.__context = context

    def _getScope(self):
        return self.__scope
