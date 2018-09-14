# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/AbstractState.py
import BigWorld
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP

class AbstractState(object):

    def __init__(self, stateId):
        super(AbstractState, self).__init__()
        self.__id = stateId
        self.__isActive = False

    def id(self):
        return self.__id

    def handleKeyEvent(self, event):
        pass

    def activate(self):
        if self.__isActive:
            LOG_DEBUG_DEV_BOOTCAMP('State.activate: state is already active')
            return
        self.__isActive = True
        self._doActivate()

    def deactivate(self):
        if not self.__isActive:
            LOG_DEBUG_DEV_BOOTCAMP('State.deactivate: state is already not active')
            return
        self._doDeactivate()
        self.__isActive = False

    def onSpaceLoadCompleted(self):
        BigWorld.player().onSpaceLoaded()

    def onAvatarBecomeNonPlayer(self):
        pass

    def onArenaLoadCompleted(self):
        pass

    def getIntroVideoData(self):
        return {}

    def _doActivate(self):
        raise NotImplementedError('Should be implemented in subclass')

    def _doDeactivate(self):
        raise NotImplementedError('Should be implemented in subclass')
