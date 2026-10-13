# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/sounds/halloween_sound_controller.py
from __future__ import absolute_import
import BattleReplay
import SoundGroups
import WWISE
from constants import IS_CHINA, IS_CT
from gui.prb_control.entities.listener import IGlobalListener
from halloween.gui.sounds import playSound
from halloween.skeletons.halloween_sound_controller import IHalloweenSoundController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.gui.sounds.sound_constants import SoundLanguage, HW_ENTER_EVENT, HW_EXIT_EVENT, HW_SOUND_REMAPPING, HW_RESET_HANGAR_MUSIC_EVENT
from helpers import dependency, getClientLanguage
from skeletons.gui.impl import IGuiLoader

class _StatusUpdateOperation(object):

    def execute(self):
        pass


class _StatusUpdateEvent(_StatusUpdateOperation):

    def __init__(self, event):
        self._event = event

    def execute(self):
        playSound(self._event)


class _StatusUpdateState(_StatusUpdateOperation):

    def __init__(self, group, value):
        self._group = group
        self._value = value

    def execute(self):
        WWISE.WW_setState(self._group, self._value)


_SOUNDS_WINDOW_STATUS_UPDATE = {}

def getEventVoiceoverLanguage():
    language = getClientLanguage()
    if language == SoundLanguage.LANGUAGE_UA:
        return SoundLanguage.VOICEOVER_UA
    if language == SoundLanguage.LANGUAGE_RU:
        return SoundLanguage.VOICEOVER_RU
    return SoundLanguage.VOICEOVER_CN if IS_CHINA else SoundLanguage.VOICEOVER_EN


class HalloweenSoundController(IHalloweenSoundController, IGlobalListener):
    _guiLoader = dependency.descriptor(IGuiLoader)
    _hwController = dependency.descriptor(IHalloweenController)

    def __init__(self, *args, **kwargs):
        super(HalloweenSoundController, self).__init__(*args, **kwargs)
        self._hangarEnterEventPlayed = False

    def onAvatarBecomePlayer(self):
        if BattleReplay.g_replayCtrl.isPlaying:
            self.__setEventVoiceoverLanguage()

    def onLobbyInited(self, event):
        self._hangarEnterEventPlayed = False
        self.startGlobalListening()
        self._guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        if self._hwController.isEventPrb():
            self._playEnter()

    def onAccountBecomePlayer(self):
        if IS_CT:
            WWISE.activateRemapping(HW_SOUND_REMAPPING)

    def onAccountBecomeNonPlayer(self):
        playSound(HW_RESET_HANGAR_MUSIC_EVENT)
        self.stopGlobalListening()
        self._guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        if IS_CT:
            WWISE.deactivateRemapping(HW_SOUND_REMAPPING)

    def onConnected(self):
        self.__setEventVoiceoverLanguage()

    def __setEventVoiceoverLanguage(self):
        language = getEventVoiceoverLanguage()
        SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, language)

    def onPrbEntitySwitched(self):
        if self._hwController.isEventPrb():
            self._playEnter()
        else:
            self._playExit()

    def playSoundEvent(self, audioEvent):
        playSound(audioEvent)

    def _playEnter(self):
        if not self._hangarEnterEventPlayed:
            self._hangarEnterEventPlayed = True
            playSound(HW_ENTER_EVENT)

    def _playExit(self):
        if self._hangarEnterEventPlayed:
            self._hangarEnterEventPlayed = False
            playSound(HW_EXIT_EVENT)

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        window = self._guiLoader.windowsManager.getWindow(uniqueID)
        if not self._hwController.isEventPrb() or window is None or window.content is None:
            return
        else:
            content = window.content
            aliasOrLayoutID = getattr(content, 'alias') if hasattr(content, 'alias') else getattr(content, 'layoutID')
            sound = _SOUNDS_WINDOW_STATUS_UPDATE.get((aliasOrLayoutID, newStatus))
            if sound:
                sound.execute()
            return
