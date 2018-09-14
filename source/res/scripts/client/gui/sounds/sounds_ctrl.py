# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/sounds_ctrl.py
import weakref
import MusicControllerWWISE as _MC
import SoundGroups
from gui.shared import g_itemsCache
from gui.sounds.ambients import GuiAmbientsCtrl
from gui.sounds.sound_constants import EnabledStatus
from gui.sounds.sound_systems import getCurrentSoundSystem
from gui.sounds.sound_utils import SOUND_DEBUG
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.sounds import ISoundsController

class SoundsController(ISoundsController):
    gameSession = dependency.descriptor(IGameSessionController)

    def __init__(self):
        super(SoundsController, self).__init__()
        self.__soundSystem = getCurrentSoundSystem()
        self.__guiAmbients = GuiAmbientsCtrl(weakref.proxy(self))
        SOUND_DEBUG('Sound system has been created', self.__soundSystem)

    def init(self):
        self.__soundSystem.init()
        self.__guiAmbients.init()

    def fini(self):
        self.__soundSystem.fini()
        self.__guiAmbients.fini()

    def start(self):
        self.__guiAmbients.start()
        self.gameSession.onPremiumNotify += self.__onPremiumChanged
        self.__setAccountAttrs()

    def stop(self, isDisconnected=False):
        self.gameSession.onPremiumNotify -= self.__onPremiumChanged
        self.__guiAmbients.stop(isDisconnected)
        if isDisconnected:
            _MC.g_musicController.unloadServerSounds(isDisconnected)

    @property
    def system(self):
        return self.__soundSystem

    def enable(self):
        """
        Do enable sound system globally
        """
        if not self.isEnabled():
            SoundGroups.g_instance.setEnableStatus(EnabledStatus.ENABLED_BY_USER)

    def disable(self):
        """
        Do disable sound system globally
        """
        if self.isEnabled():
            SoundGroups.g_instance.setEnableStatus(EnabledStatus.DISABLED)

    def isEnabled(self):
        """
        Is sounds enabled in general
        """
        return EnabledStatus.isEnabled(SoundGroups.g_instance.getEnableStatus())

    def __onPremiumChanged(self, isPremium, attrs, premiumExpiryTime):
        SOUND_DEBUG('Premium account status changed', isPremium, attrs, premiumExpiryTime)
        self.__setAccountAttrs(restartSounds=True)

    def __setAccountAttrs(self, restartSounds=False):
        SOUND_DEBUG('Set current account attributes', g_itemsCache.items.stats.attributes, restartSounds)
        _MC.g_musicController.setAccountAttrs(g_itemsCache.items.stats.attributes, restart=restartSounds)
