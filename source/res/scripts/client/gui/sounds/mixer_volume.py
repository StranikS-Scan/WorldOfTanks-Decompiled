# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/mixer_volume.py
import WWISE
from PlayerEvents import g_playerEvents
from gui.SystemMessages import pushMessage, SM_TYPE
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
MIN_SOUND_SYSTEM_MIXER_VALUE = 10

class SystemMixerVolumeCtrl(object):
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        self.__appMixerVolume = 100
        self.__invAppMixerVolume = True

    def init(self):
        self.connectionMgr.onConnected += self.__onConnected
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer

    def fini(self):
        self.connectionMgr.onConnected -= self.__onConnected
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer

    def isSystemMixerVolumeDisabled(self):
        if self.__invAppMixerVolume:
            self.__appMixerVolume = round(WWISE.WW_getAppMixerVolume() * 100)
            self.__invAppMixerVolume = False
        return self.__appMixerVolume <= MIN_SOUND_SYSTEM_MIXER_VALUE

    def markNeedInvAppMixerVolume(self):
        self.__invAppMixerVolume = True

    def __onAvatarBecomeNonPlayer(self):
        self.__invAppMixerVolume = True
        self.__checkSoundSystemOffStatus()

    def __onConnected(self):
        self.__invAppMixerVolume = True
        self.__checkSoundSystemOffStatus()

    def __checkSoundSystemOffStatus(self):
        if self.isSystemMixerVolumeDisabled():
            pushMessage('', SM_TYPE.SystemMixerVolumeDisabled, None, None)
        return
