# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/event_sound_subctrl.py
import SoundGroups
from constants import CURRENT_REALM
from gui.sounds.sound_constants import SoundLanguage
from helpers import dependency, getClientLanguage
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID

class EventSoundSubController(object):
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        self.__previousSpaceId = GuiGlobalSpaceID.UNDEFINED

    def init(self):
        self.appLoader.onGUISpaceEntered += self.__onGUISpaceEntered

    def fini(self):
        self.appLoader.onGUISpaceEntered -= self.__onGUISpaceEntered

    def start(self):
        pass

    def stop(self, isDisconnected=False):
        pass

    def __onGUISpaceEntered(self, spaceID):
        if self.__previousSpaceId != spaceID:
            self.handleSoundSpaceChange(self.__previousSpaceId, spaceID)
            self.__previousSpaceId = spaceID

    def handleSoundSpaceChange(self, oldSpaceID, newSpaceID):
        if oldSpaceID == GuiGlobalSpaceID.BATTLE or oldSpaceID == GuiGlobalSpaceID.UNDEFINED:
            self.__updateEventVoiceoverLanguage(SoundLanguage.HANGAR_LANGUAGE_CONFIG)
        elif newSpaceID == GuiGlobalSpaceID.BATTLE:
            self.__updateEventVoiceoverLanguage(SoundLanguage.BATTLE_LANGUAGE_CONFIG)

    def __updateEventVoiceoverLanguage(self, envConfig):
        clientLanguage = getClientLanguage().upper()
        for realms, languages in envConfig.items():
            if CURRENT_REALM in realms:
                switchPosition = languages.get(clientLanguage, languages['default'])
                SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, switchPosition)
                return

        SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_SILENCE)
