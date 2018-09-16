# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_missions_navigation.py
from operator import methodcaller
import WWISE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.server_events.pm_constants import SOUNDS
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache

class _PersonalMissionNavigationInfo(object):

    def __init__(self):
        self.__operationID = 1
        self.__chainID = 1

    def getOperationID(self):
        return self.__operationID

    def setOperationID(self, operationID):
        self.__operationID = operationID

    def getChainID(self):
        return self.__chainID

    def setChainID(self, chainID):
        self.__chainID = chainID


class PersonalMissionsNavigation(EventSystemEntity):
    __navigationInfo = _PersonalMissionNavigationInfo()
    _eventsCache = dependency.descriptor(IEventsCache)
    _lobbyCtx = dependency.descriptor(ILobbyContext)

    @classmethod
    def getOperationID(cls):
        return cls.__navigationInfo.getOperationID()

    @classmethod
    def getOperation(cls):
        return cls._eventsCache.personalMissions.getOperations().get(cls.getOperationID())

    @classmethod
    def setOperationID(cls, operationID):
        cls.__navigationInfo.setOperationID(operationID)
        cls.__setWWISEGlobal()

    @classmethod
    def getChainID(cls):
        return cls.__navigationInfo.getChainID()

    @classmethod
    def getChain(cls):
        return cls.getOperation().getQuests()[cls.getChainID()]

    @classmethod
    def setChainID(cls, chainID):
        cls.__navigationInfo.setChainID(chainID)
        cls.__setWWISEGlobal()

    def _populate(self):
        super(PersonalMissionsNavigation, self)._populate()
        self.__setWWISEGlobal()
        self._lobbyCtx.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self._eventsCache.onProgressUpdated += self.__onProgressUpdated

    def _dispose(self):
        self._eventsCache.onProgressUpdated += self.__onProgressUpdated
        self._lobbyCtx.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        super(PersonalMissionsNavigation, self)._dispose()

    @classmethod
    def __setWWISEGlobal(cls):
        operation = cls.getOperation()
        if operation:
            completedCount = len(operation.getQuestsInChainByFilter(cls.getChainID(), methodcaller('isCompleted')))
        else:
            completedCount = 0
        WWISE.WW_setRTCPGlobal(SOUNDS.RTCP_MISSIONS_NUMBER, completedCount)

    def __onSettingsChanged(self, diff):
        if 'isRegularQuestEnabled' in diff and not diff['isRegularQuestEnabled']:
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onProgressUpdated(self, _):
        self.__setWWISEGlobal()
