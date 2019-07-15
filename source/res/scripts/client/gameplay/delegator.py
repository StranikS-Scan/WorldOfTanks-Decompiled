# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/delegator.py
import BigWorld
from frameworks.state_machine import StringEvent
from frameworks.state_machine import StateMachine
from frameworks.state_machine import BaseStateObserver
from gameplay import listeners
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

    def removeStateObserver(self, observer):
        self.__machine.disconnect(observer)

    def postStateEvent(self, eventID, **kwargs):
        self.__machine.post(StringEvent(eventID, **kwargs))

    def tick(self):
        self.__machine.post(StringEvent(''))

    def goToLoginByRQ(self):
        self.connectionMgr.disconnect()
        self.postStateEvent(PlayerEventID.NON_PLAYER_BECOME_PLAYER, disconnectReason=DisconnectReason.REQUEST)

    def goToLoginByDisconnectRQ(self):
        self.loginMgr.tryPrepareWGCLogin()
        self.goToLoginByRQ()

    def goToLoginByEvent(self):
        self.postStateEvent(PlayerEventID.NON_PLAYER_BECOME_PLAYER, disconnectReason=DisconnectReason.EVENT)

    def goToLoginByKick(self, reason, isBan, expiryTime):
        self.postStateEvent(PlayerEventID.NON_PLAYER_BECOME_PLAYER, disconnectReason=DisconnectReason.KICK, kickReason=reason, isBan=isBan, expiryTime=expiryTime)

    def goToLoginByError(self, reason):
        self.connectionMgr.disconnect()
        self.postStateEvent(PlayerEventID.NON_PLAYER_BECOME_PLAYER, disconnectReason=DisconnectReason.ERROR, kickReason=reason)

    @staticmethod
    def quitFromGame():
        BigWorld.quit()
