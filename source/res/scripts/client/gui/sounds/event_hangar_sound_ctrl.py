# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/event_hangar_sound_ctrl.py
import SoundGroups
from constants import QUEUE_TYPE
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.event_hangar_sound import IEventHangarSoundEnv
from skeletons.gui.shared.utils import IHangarSpace

class EventHangarSoundEnvController(IEventHangarSoundEnv, IGlobalListener):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    _EVENT_ENTER_EVENT = 'ev_halloween_2019_hangar_metagame_enter'
    _EVENT_LEAVE_EVENT = 'ev_halloween_2019_hangar_metagame_exit'

    def __init__(self):
        self.__eventHangarEnvActive = False

    @prbEntityProperty
    def _prbEntity(self):
        pass

    def init(self):
        self.__hangarSpace.onSpaceCreate += self.__onHangarSpaceReady
        self.__hangarSpace.onSpaceDestroy += self.__onHangarSpaceDestroy

    def fini(self):
        self.__hangarSpace.onSpaceCreate -= self.__onHangarSpaceReady
        self.__hangarSpace.onSpaceDestroy -= self.__onHangarSpaceDestroy
        self.stopGlobalListening()

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
        SoundGroups.g_instance.playSound2D(self._EVENT_ENTER_EVENT)
        self.__eventHangarEnvActive = True

    def __stopEventHangarSound(self):
        SoundGroups.g_instance.playSound2D(self._EVENT_LEAVE_EVENT)
        self.__eventHangarEnvActive = False

    def __isInEvent(self):
        entity = self._prbEntity
        return entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES
