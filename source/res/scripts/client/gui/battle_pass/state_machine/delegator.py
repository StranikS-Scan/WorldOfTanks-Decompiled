# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/state_machine/delegator.py
import weakref
import typing
from frameworks.state_machine import StringEvent
from gui.battle_pass.state_machine import lockOverlays
from gui.battle_pass.state_machine.observers import FinalStateMachineObserver
from gui.battle_pass.state_machine.states import FinalRewardEventID
if typing.TYPE_CHECKING:
    from frameworks.state_machine import BaseStateObserver
    from frameworks.state_machine import StateMachine
    from skeletons.gui.game_control import IBattlePassController

class FinalRewardLogic(object):
    __slots__ = ('__battlePassController', '__machine', '__observers')

    def __init__(self, battlePassController, machine):
        super(FinalRewardLogic, self).__init__()
        self.__battlePassController = weakref.proxy(battlePassController)
        self.__machine = machine
        self.__observers = None
        return

    def start(self):
        if self.__machine.isRunning():
            return
        self.__machine.configure()
        self.__observers = FinalStateMachineObserver()
        self.addStateObserver(self.__observers)
        self.__machine.start()

    def stop(self):
        self.__machine.stop()
        if self.__observers is not None:
            self.removeStateObserver(self.__observers)
        self.__observers = None
        return

    def startFinalFlow(self, rewards, data):
        self.__machine.saveRewards(rewards, data)
        lockOverlays(True)
        self.postStateEvent(FinalRewardEventID.PROGRESSION_COMPLETE)

    def postVotingOpened(self, **kwargs):
        self.postStateEvent(FinalRewardEventID.VOTING_OPENED, **kwargs)

    def postPreviewOpen(self):
        self.postStateEvent(FinalRewardEventID.OPEN_PREVIEW)

    def postClosePreview(self):
        self.postStateEvent(FinalRewardEventID.CLOSE_PREVIEW)

    def postNextState(self, **kwargs):
        self.postStateEvent(FinalRewardEventID.NEXT, **kwargs)

    def postEscape(self):
        self.postStateEvent(FinalRewardEventID.ESCAPE)

    def getRewardsData(self):
        return self.__machine.getRewardsData()

    def clearRewardsData(self):
        self.__machine.clearRewardsData()

    def addStateObserver(self, observer):
        self.__machine.connect(observer)

    def removeStateObserver(self, observer):
        self.__machine.disconnect(observer)

    def postStateEvent(self, eventID, **kwargs):
        if self.__machine.isRunning():
            self.__machine.post(StringEvent(eventID, **kwargs))
