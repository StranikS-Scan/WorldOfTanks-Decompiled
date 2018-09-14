# Embedded file name: scripts/client/LightFx/LightManager.py
import time
from debug_utils import *
import BigWorld
import LightEffect
from LightEffectsCache import LightEffectsCache
from Math import Vector4
import gui.SystemMessages
from messenger.m_constants import PROTO_TYPE
from messenger.ext.player_helpers import isCurrentPlayer
g_instance = None

class LightManager:
    UPDATE_TIMEOUT = 0.5
    ALL_LIGHTS = 'All'
    LOCATIONS_MASKS = {'Zone_LeftSpeaker': 1,
     'Zone_RightSpeaker': 4,
     'Zone_Keyboard': 16,
     'Zone_Logo': 524288,
     ALL_LIGHTS: 4294967295L}

    def __init__(self):
        self.__isEnabled = False
        self.__lightObject = BigWorld.WGLightFx()
        self.__lights = {}
        self.__isEnabled = self.__lightObject.initialize()
        if not self.__isEnabled:
            LOG_DEBUG('LightFx is not enabled')
            return
        else:
            self.__lightObject.reset()
            LightEffectsCache.load()
            for lightEffect in LightEffectsCache.allEffects().values():
                lightEffect.onStop += self.__onEffectStop

            numberOfDevices = self.__lightObject.getNumberOfDevices()
            for deviceIndex in range(numberOfDevices):
                numberOfLights = self.__lightObject.getNumberOfLights(deviceIndex)
                for lightIndex in range(numberOfLights):
                    lightDescription = self.__lightObject.getLightDescription(deviceIndex, lightIndex)
                    self.__lights[lightDescription] = (deviceIndex, lightIndex)

            self.__runningEffects = []
            self.__lastUpdateTime = None
            self.__periodicTimerID = None
            LightManager._chatActionsHandler = _ChatActionsHandler()
            self.__periodicUpdate()
            return

    def start(self):
        if self.isEnabled():
            self.setStartupLights()

    def destroy(self):
        if not self.__isEnabled:
            return
        else:
            if self.__periodicTimerID is not None:
                BigWorld.cancelCallback(self.__periodicTimerID)
            for lightEffect in LightEffectsCache.allEffects().values():
                lightEffect.destroy()

            LightManager._chatActionsHandler.destroy()
            return

    def isEnabled(self):
        return self.__isEnabled

    def getLights(self):
        return self.__lights

    def setLightColor(self, lightDescription, color):
        self.setLightAction(lightDescription, color, LightEffect.ACTION_COLOR)

    def setLightPulse(self, lightDescription, color):
        self.setLightAction(lightDescription, color, LightEffect.ACTION_PULSE)

    def setLightActionByIndex(self, deviceIndex, lightIndex, color, action):
        if action == LightEffect.ACTION_COLOR:
            self.__lightObject.setLightColor(deviceIndex, lightIndex, color)
        elif action == LightEffect.ACTION_PULSE:
            self.__lightObject.setLightPulse(deviceIndex, lightIndex, color)

    def actionColorEx(self, mask, action, color):
        self.__lightObject.actionColorEx(mask, action, color, Vector4())

    def setLightAction(self, lightDescription, color, action):
        if not self.isEnabled():
            return
        if LightManager.LOCATIONS_MASKS.has_key(lightDescription):
            self.actionColorEx(LightManager.LOCATIONS_MASKS[lightDescription], action, color)

    def startLightEffect(self, lightEffectName):
        if not self.isEnabled():
            return
        lightEffect = LightEffectsCache.getEffect(lightEffectName)
        if not lightEffect.isRunning():
            self.__runningEffects.append(lightEffect)
            lightEffect.start()
        for oneLightAction in lightEffect.lightActions.values():
            self.setLightAction(oneLightAction.lightDescription, oneLightAction.color, oneLightAction.action)

    def stopLightEffect(self, lightEffectName):
        if not self.isEnabled():
            return
        lightEffect = LightEffectsCache.getEffect(lightEffectName)
        if lightEffect.isRunning():
            lightEffect.stop()

    def __onEffectStop(self, lightEffect):
        self.__runningEffects.remove(lightEffect)

    def turnOffAll(self):
        for lightEffect in self.__runningEffects[:]:
            self.stopLightEffect(lightEffect.name)

    def setStartupLights(self):
        self.turnOffAll()
        self.startLightEffect('Splash Screen')

    def __periodicUpdate(self):
        self.__periodicTimerID = None
        blackLights = LightManager.LOCATIONS_MASKS.keys()
        blackLights.remove(LightManager.ALL_LIGHTS)
        if len(self.__runningEffects) > 0:
            lightEffect = self.__runningEffects[-1]
            for oneLightAction in lightEffect.lightActions.values():
                if oneLightAction.lightDescription in blackLights:
                    blackLights.remove(oneLightAction.lightDescription)
                if oneLightAction.lightDescription == LightManager.ALL_LIGHTS:
                    del blackLights[:]
                if oneLightAction.action == LightEffect.ACTION_COLOR:
                    self.setLightAction(oneLightAction.lightDescription, oneLightAction.color, oneLightAction.action)
                else:
                    del blackLights[:]
                    break

        for lightDescription in blackLights:
            self.setLightAction(lightDescription, Vector4(), LightEffect.ACTION_COLOR)

        self.__lightObject.update()
        self.__lastUpdateTime = time.time()
        self.__periodicTimerID = BigWorld.callback(LightManager.UPDATE_TIMEOUT, self.__periodicUpdate)
        return


class GameLights:

    @staticmethod
    def startTicks():
        g_instance.startLightEffect('Ticks')

    @staticmethod
    def roundStarted():
        g_instance.stopLightEffect('Ticks')
        g_instance.startLightEffect('Round Started')

    INVITATION_EFFECT = 'Invitation'
    CHAT_CHANNEL_OPENED_EFFECT = 'Chat Channel'

    @staticmethod
    def systemMessage():
        g_instance.startLightEffect('System Message')


from LightFx.LightManager import GameLights
from PlayerEvents import g_playerEvents
from ConnectionManager import connectionManager as g_connectionManager
from gui.prb_control.dispatcher import g_prbLoader
from messenger.proto.events import g_messengerEvents
_chatActionsHandler = None

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
        return

    def __onDisconnected(self):
        g_instance.setStartupLights()

    def __onReceivedInviteListModified(self, *args):
        if g_prbLoader.getInvitesManager().getUnreadCount():
            g_instance.startLightEffect(GameLights.INVITATION_EFFECT)
        else:
            g_instance.stopLightEffect(GameLights.INVITATION_EFFECT)

    def __onSysMessage(self, clientID, formatted, settings):
        gameGreetingName = gui.SystemMessages.SM_TYPE.GameGreeting.name()
        if gameGreetingName not in settings.auxData:
            GameLights.systemMessage()

    def __onConnectStateChanged(self, channel):
        if channel.isJoined() and channel.getProtoType() is PROTO_TYPE.BW:
            data = channel.getProtoData()
            if not isCurrentPlayer(data.owner) and channel.isPrivate():
                g_instance.startLightEffect(GameLights.CHAT_CHANNEL_OPENED_EFFECT)
