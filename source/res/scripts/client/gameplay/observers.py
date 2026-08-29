# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/observers.py
from collections import defaultdict
from frameworks_common.state_machine import BaseStateObserver
from gameplay.blockers import BlockingStateMixin

class BlockingStateClearObserver(BaseStateObserver):

    def __init__(self):
        self.__clearIDsToBlockingStates = defaultdict(list)

    def clear(self):
        self.__clearIDsToBlockingStates = defaultdict(list)

    def isObservingState(self, state):
        return True

    def onEnterState(self, state, event):
        if event is not None or self.__clearIDsToBlockingStates:
            return
        else:
            machine = state.getMachine()
            for child in machine.getRecursiveChildrenStates():
                if isinstance(child, BlockingStateMixin):
                    self.__clearIDsToBlockingStates[child.blockerClearLifetimeStateID].append(child)

            return

    def onExitState(self, state, event):
        for blockerState in self.__clearIDsToBlockingStates.get(state.getStateID(), []):
            blockerState.clearBlockers()
