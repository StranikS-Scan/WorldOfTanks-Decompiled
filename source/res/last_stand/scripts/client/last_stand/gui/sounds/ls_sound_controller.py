# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/sounds/ls_sound_controller.py
import BattleReplay
import SoundGroups
import WWISE
from constants import IS_CHINA
from gui.prb_control.entities.listener import IGlobalListener
from last_stand.gui.sounds import playSound
from last_stand.skeletons.ls_sound_controller import ILSSoundController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.gui.sounds.sound_constants import SoundLanguage, LS_ENTER_EVENT, LS_EXIT_EVENT
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

class LSSoundController(ILSSoundController, IGlobalListener):
    _guiLoader = dependency.descriptor(IGuiLoader)
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self, *args, **kwargs):
        super(LSSoundController, self).__init__(*args, **kwargs)
        self._hangarEnterEventPlayed = False

    def onAvatarBecomePlayer(self):
        if BattleReplay.g_replayCtrl.isPlaying:
            self.__setEventVoiceoverLanguage()

    def onLobbyStarted(self, ctx):
        super(LSSoundController, self).onLobbyStarted(ctx)
        self._hangarEnterEventPlayed = False
        self._guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged

    def onLobbyInited(self, event):
        self.startGlobalListening()
        if self.lsCtrl.isEventPrb():
            self._playEnter()

    def onAccountBecomeNonPlayer(self):
        self.stopGlobalListening()
        self._guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged

    def onConnected(self):
        self.__setEventVoiceoverLanguage()

    def __setEventVoiceoverLanguage(self):
        language = getClientLanguage()
        if language == SoundLanguage.LANGUAGE_UA:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_UA)
        elif language == SoundLanguage.LANGUAGE_RU:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_RU)
        elif IS_CHINA:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_CN)
        else:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_EN)

    def onPrbEntitySwitched(self):
        if self.lsCtrl.isEventPrb():
            self._playEnter()
        else:
            self._playExit()

    def playSoundEvent(self, audioEvent):
        playSound(audioEvent)

    def _playEnter(self):
        if not self._hangarEnterEventPlayed:
            self._hangarEnterEventPlayed = True
            playSound(LS_ENTER_EVENT)

    def _playExit(self):
        if self._hangarEnterEventPlayed:
            self._hangarEnterEventPlayed = False
            playSound(LS_EXIT_EVENT)

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        window = self._guiLoader.windowsManager.getWindow(uniqueID)
        if not self.lsCtrl.isEventPrb() or window is None or window.content is None:
            return
        else:
            content = window.content
            aliasOrLayoutID = getattr(content, 'alias') if hasattr(content, 'alias') else getattr(content, 'layoutID')
            sound = _SOUNDS_WINDOW_STATUS_UPDATE.get((aliasOrLayoutID, newStatus))
            if sound:
                sound.execute()
            return
