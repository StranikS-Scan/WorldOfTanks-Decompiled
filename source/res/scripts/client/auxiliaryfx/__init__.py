# Embedded file name: scripts/client/AuxiliaryFx/__init__.py
from AuxiliaryFx.FxController import AuxiliaryFxController
from AuxiliaryFx.Roccat import RoccatFxManager
import AuxiliaryFx

class IAuxiliaryFxManager:

    def isEnabled(self):
        return False

    def destroy(self):
        pass

    def start(self):
        pass


g_instance = None

class AuxiliaryFxManager:

    def __init__(self):
        self.__fxManagers = [(RoccatFxManager.RoccatFxManager(), RoccatFxManager.RoccatVehicleFx)]
        self.__chatActionsHandler = _ChatActionsHandler()

    def start(self):
        for fxManager, _ in self.__fxManagers:
            fxManager.start()

    def destroy(self):
        for fxManager, _ in self.__fxManagers:
            fxManager.destroy()

        self.__fxManagers = None
        self.__chatActionsHandler.destroy()
        self.__chatActionsHandler = None
        return

    def createFxController(self, vehicle):
        controllers = []
        for fxManager, FxCtrl in self.__fxManagers:
            controllers.append(FxCtrl(vehicle, fxManager))

        return AuxiliaryFxController(controllers)

    def execEffect(self, effectName):
        for fxManager, _ in self.__fxManagers:
            execEffect = getattr(fxManager, effectName, None)
            if execEffect is not None:
                execEffect()

        return


from PlayerEvents import g_playerEvents
from ConnectionManager import connectionManager as g_connectionManager
import gui.SystemMessages
from gui.prb_control.dispatcher import g_prbLoader
from messenger.proto.events import g_messengerEvents
from messenger.m_constants import PROTO_TYPE
from messenger.ext.player_helpers import isCurrentPlayer

class _ChatActionsHandler:

    def __init__(self):
        g_playerEvents.onAccountBecomePlayer += self.__subscribe
        g_connectionManager.onDisconnected += self.__onDisconnected

    def __subscribe(self):
        invitesManager = g_prbLoader.getInvitesManager()
        if invitesManager is not None:
            invitesManager.onReceivedInviteListModified += self.__onReceivedInviteListModified
            invitesManager.onInvitesListInited += self.__onReceivedInviteListModified
        g_messengerEvents.serviceChannel.onServerMessageReceived += self.__onSysMessage
        g_messengerEvents.serviceChannel.onClientMessageReceived += self.__onSysMessage
        g_messengerEvents.channels.onConnectStateChanged += self.__onConnectStateChanged
        return

    def destroy(self):
        invitesManager = g_prbLoader.getInvitesManager()
        if invitesManager is not None:
            invitesManager.onReceivedInviteListModified -= self.__onReceivedInviteListModified
            invitesManager.onInvitesListInited -= self.__onReceivedInviteListModified
        g_messengerEvents.serviceChannel.onServerMessageReceived -= self.__onSysMessage
        g_messengerEvents.serviceChannel.onClientMessageReceived -= self.__onSysMessage
        g_messengerEvents.channels.onConnectStateChanged -= self.__onConnectStateChanged
        if g_connectionManager is not None:
            g_connectionManager.onDisconnected -= self.__onDisconnected
        if g_playerEvents is not None:
            g_playerEvents.onAccountBecomePlayer -= self.__subscribe
        return

    def __onDisconnected(self):
        g_instance.execEffect('resetBackground')

    def __onReceivedInviteListModified(self, *args):
        if g_prbLoader.getInvitesManager().getUnreadCount():
            g_instance.execEffect('startInvitationEffect')
        else:
            g_instance.execEffect('stopInvitationEffect')

    def __onSysMessage(self, clientID, formatted, settings):
        gameGreetingName = gui.SystemMessages.SM_TYPE.GameGreeting.name()
        if gameGreetingName not in settings.auxData:
            g_instance.execEffect('systemMessageEffect')

    def __onConnectStateChanged(self, channel):
        if channel.isJoined() and channel.getProtoType() is PROTO_TYPE.BW:
            data = channel.getProtoData()
            if not isCurrentPlayer(data.owner) and channel.isPrivate():
                g_instance.execEffect('channelOpenedEffect')
