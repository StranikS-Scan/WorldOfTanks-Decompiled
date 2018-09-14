# Embedded file name: scripts/client/gui/Scaleform/SoundManager.py
from debug_utils import *
import ResMgr
from items import _xml
from gui.Scaleform.windows import UIInterface
import SoundGroups
import Vibroeffects
from gui.doc_loaders.GuiSoundsLoader import GuiSoundsLoader

class BUTTON_TYPES(object):
    NORMAL = 'normal'


class RENDERER_TYPES(object):
    NORMAL = 'normal'


class SoundSettings(dict):

    def __init__(self):
        self.__schemas = {}
        self.__groups = {}
        self.__overrides = {}

    @staticmethod
    def populateSettings(dataSection):
        res = SoundSettings()
        for typeName, settings in dataSection.items():
            if typeName == 'overrides':
                for overrideName, events in settings.items():
                    res.__overrides[overrideName] = {}
                    for eventName, event in events.items():
                        res.__overrides[overrideName][eventName] = event.asString

            elif typeName == 'schemas':
                for schemaName, parts in settings.items():
                    res.__schemas[schemaName] = {}
                    for partName, subParts in parts.items():
                        for subPartName, data in subParts.items():
                            if partName == 'sounds':
                                res.__schemas[schemaName][subPartName] = data.asString
                            elif partName == 'groups':
                                res.__groups[subPartName] = schemaName

            elif typeName == 'default':
                for eventName, event in settings.items():
                    res[eventName] = event.asString

            else:
                res[typeName] = settings.asString

        return res

    def getSoundName(self, soundType, soundId, state):
        if len(soundId) and self.__overrides.has_key(soundId) > 0:
            sound = self.__overrides.get(soundId, {}).get(state, '')
        elif len(soundType) > 0 and self.__groups.has_key(soundType):
            schemaName = self.__groups.get(soundType, '')
            sound = self.__schemas.get(schemaName, {}).get(state, '')
        elif len(soundType) > 0 and self.__schemas.has_key(soundType):
            sound = self.__schemas.get(soundType, {}).get(state, '')
        else:
            sound = self.get(state, '')
        return sound


class SoundManager(UIInterface):

    def __init__(self):
        self.__soundEvents = {}
        self.__loadConfig()
        self.sounds = GuiSoundsLoader()

    def __loadConfig(self):
        xmlPath = 'gui/gui_sounds.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        for groupName, types in section.items():
            self.__soundEvents[groupName] = SoundSettings.populateSettings(types)

        return

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        sm = self.uiHolder.movie.soundManager
        sm.script = self
        try:
            self.sounds.load()
        except Exception:
            LOG_ERROR('There is error while loading sounds xml data')
            LOG_CURRENT_EXCEPTION()

    def soundEventHandler(self, control, state, type, id):
        self.tryPlaySnd(control, state, type, id)

    def dispossessUI(self):
        self.uiHolder.movie.soundManager.script = None
        UIInterface.dispossessUI(self)
        return

    def playSound(self, dictPath):
        if dictPath is None:
            return
        else:
            scope = self.__soundEvents
            for key in str(dictPath).split('.'):
                if key not in scope:
                    return
                scope = scope[key]

            if type(scope) != str:
                LOG_ERROR('Invalid soundpath under key: %s', dictPath)
                return
            SoundGroups.g_instance.playSound2D(scope)
            return

    def playEffectSound(self, effectName):
        sound = self.sounds.getEffectSound(effectName)
        if sound is not None:
            SoundGroups.g_instance.playSound2D(sound)
        return

    def onButtonEvent(self, callbackID, state, type, id):
        self.tryPlaySnd('buttons', state, type, id)

    def onItemRendererEvent(self, callbackID, state, type):
        self.tryPlaySnd('itemRenderer', state, type, 'fakeId')

    def tryPlaySnd(self, sndType, state, type, id):
        sound = self.__soundEvents.get(sndType, SoundSettings()).getSoundName(type, id, state)
        if sound:
            SoundGroups.g_instance.playSound2D(sound)
            if state == 'press':
                Vibroeffects.VibroManager.g_instance.playButtonClickEffect(type)
