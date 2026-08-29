# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/delegator.py
import BigWorld
from frameworks_common.state_machine import StringEvent
from frameworks_common.state_machine import StateMachine
from frameworks_common.state_machine import BaseStateObserver
from frameworks_common.state_machine import OneshotStateIdsObserver
from gameplay import listeners
from gameplay.blockers import BlockingStateMixin
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager, DisconnectReason
from skeletons.gui.login_manager import ILoginManager
from skeletons.gameplay import IGameplayLogic, PlayerEventID

class GameplayLogic(IGameplayLogic):
    __slots__ = ('__machine', '__adaptor')
    connectionMgr = dependency.descriptor(IConnectionManager)
    loginMgr = dependency.descriptor(ILoginManager)

    def __init__(self, machine):
        super(GameplayLogic, self).__init__()
        self.__machine = machine
        self.__adaptor = listeners.PlayerEventsAdaptor(self.__machine)

    def start(self):
        self.__adaptor.startListening()
        self.__machine.configure()
        self.__machine.start()

    def stop(self):
        self.__adaptor.stopListening()
        self.__machine.stop()

    def addStateObserver(self, observer):
        self.__machine.connect(observer)

    def addOneshotObserver(self, gameplayStateIDs, observerLifetimeObj, enterFn=None, exitFn=None):
        self.__machine.connect(OneshotStateIdsObserver(gameplayStateIDs, self.__machine, observerLifetimeObj, enterFn, exitFn))

    def removeStateObserver(self, observer):
        self.__machine.disconnect(observer)

    def postStateEvent(self, eventID, **kwargs):
        self.__machine.post(StringEvent(eventID, **kwargs))

    def tick(self):
        self.__machine.post(StringEvent(''))

    def addStateEnterBlocker(self, stateID, event):
        state = self.__machine.getStateByID(stateID)
        state.addEnterBlocker(event)

    def addStateExitBlocker(self, stateID, event):
        state = self.__machine.getStateByID(stateID)
        state.addExitBlocker(event)

    def goToLoginByRQ(self):
        self.connectionMgr.disconnect()
        self.postStateEvent(PlayerEventID.NON_PLAYER_BECOME_PLAYER, disconnectReason=DisconnectReason.REQUEST)

    def goToLoginByDisconnectRQ(self):
        self.loginMgr.tryPrepareWGCLogin()
        self.goToLoginByRQ()

    def goToLoginByEvent(self):
        self.postStateEvent(PlayerEventID.NON_PLAYER_BECOME_PLAYER, disconnectReason=DisconnectReason.EVENT)

    def goToLoginByKick(self, reason, kickReasonType, expiryTime):
        self.postStateEvent(PlayerEventID.NON_PLAYER_BECOME_PLAYER, disconnectReason=DisconnectReason.KICK, kickReason=reason, kickReasonType=kickReasonType, expiryTime=expiryTime)

    def goToLoginByError(self, reason):
        self.connectionMgr.disconnect()
        self.postStateEvent(PlayerEventID.NON_PLAYER_BECOME_PLAYER, disconnectReason=DisconnectReason.ERROR, kickReason=reason)

    @staticmethod
    def quitFromGame():
        BigWorld.quit()
