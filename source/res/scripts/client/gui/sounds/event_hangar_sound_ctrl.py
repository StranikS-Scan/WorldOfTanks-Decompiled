# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/event_hangar_sound_ctrl.py
import datetime
import SoundGroups
from constants import QUEUE_TYPE
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from helpers.time_utils import getServerRegionalTime
from skeletons.gui.event_hangar_sound import IEventHangarSoundEnv
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import Hw21StorageKeys
from gui.sounds.sound_constants import HW21SoundConsts

class EventHangarSoundEnvController(IEventHangarSoundEnv, IGlobalListener):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__eventHangarEnvActive = False
        self.__eventInviteSound = None
        return

    @prbEntityProperty
    def _prbEntity(self):
        pass

    def init(self):
        self.__hangarSpace.onSpaceCreate += self.__onHangarSpaceReady
        self.__hangarSpace.onSpaceDestroy += self.__onHangarSpaceDestroy

    def fini(self):
        self.__eventInviteSound = None
        self.__hangarSpace.onSpaceCreate -= self.__onHangarSpaceReady
        self.__hangarSpace.onSpaceDestroy -= self.__onHangarSpaceDestroy
        self.stopGlobalListening()
        return

    def onPrbEntitySwitched(self):
        self.__updateEventSound()

    def __onHangarSpaceReady(self):
        self.startGlobalListening()
        self.__updateEventSound()

    def __onHangarSpaceDestroy(self, wasInited):
        self.stopGlobalListening()
        if self.__eventHangarEnvActive:
            self.__stopEventHangarSound()

    def __updateEventSound(self):
        if self.__isInEvent() and not self.__eventHangarEnvActive:
            self.__startEventHangarSound()
        elif self.__eventHangarEnvActive:
            self.__stopEventHangarSound()

    def __startEventHangarSound(self):
        SoundGroups.g_instance.playSound2D(HW21SoundConsts.EVENT_ENTER_EVENT)
        self.__eventHangarEnvActive = True
        self.__playInviteStory()

    def __stopEventHangarSound(self):
        self.__stopInviteStory()
        self.__eventHangarEnvActive = False
        SoundGroups.g_instance.playSound2D(HW21SoundConsts.EVENT_LEAVE_EVENT)

    def __isInEvent(self):
        entity = self._prbEntity
        return entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES

    def __playInviteStory(self):
        dayOfMonth = self.__getDayOfMonth()
        wasFirstHello = self.__getValue(Hw21StorageKeys.HANGAR_HELLO_FIRST, False)
        if not wasFirstHello:
            self.__setValue(Hw21StorageKeys.HANGAR_HELLO_FIRST, True)
        lastHelloDate = self.__getValue(Hw21StorageKeys.HANGAR_LAST_HELLO_DATE, 0)
        if lastHelloDate != dayOfMonth:
            self.__setValue(Hw21StorageKeys.HANGAR_LAST_HELLO_DATE, dayOfMonth)
            if self.__eventInviteSound is None:
                wwevent = HW21SoundConsts.HANGAR_DAILY_VO if wasFirstHello else HW21SoundConsts.HANGAR_FIRST_DAILY_VO
                self.__eventInviteSound = SoundGroups.g_instance.getSound2D(wwevent)
                self.__eventInviteSound.play()
        return

    def __stopInviteStory(self):
        if self.__eventInviteSound is not None and self.__eventInviteSound.isPlaying:
            self.__eventInviteSound.stop()
            self.__eventInviteSound = None
        return

    def __setValue(self, name, value):
        self.__settingsCore.serverSettings.setHW21NarrativeSettings({name: value})

    def __getValue(self, name, default=None):
        return self.__settingsCore.serverSettings.getHW21NarrativeSettings(name, default)

    def __getDayOfMonth(self):
        return datetime.datetime.fromtimestamp(getServerRegionalTime()).day
