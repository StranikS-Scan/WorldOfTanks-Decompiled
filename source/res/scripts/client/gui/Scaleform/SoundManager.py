# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/SoundManager.py
# Compiled at: 2011-08-08 14:08:56
from debug_utils import LOG_DEBUG
import ResMgr
from items import _xml
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.utils.sound import Sound
import Vibroeffects

class BUTTON_TYPES(object):
    NORMAL = 'normal'


class SoundManager(UIInterface):

    def __init__(self):
        self.__soundEvents = {}
        self.__loadConfig()

    def __loadConfig(self):
        xmlPath = 'gui/gui_sounds.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        for groupName, types in section.items():
            group = self.__soundEvents.setdefault(groupName, {})
            for typeName, events in types.items():
                type = group.setdefault(typeName, {})
                for eventName, event in events.items():
                    type[eventName] = event.asString

        return

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'GuiSound.Button': self.onButtonEvent})

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('GuiSound.Button')
        UIInterface.dispossessUI(self)

    def onButtonEvent(self, callbackID, state, type=BUTTON_TYPES.NORMAL):
        sound = self.__soundEvents.get('buttons', {}).get(type, {}).get(state, '')
        if sound:
            Sound(sound).play()
            if state == 'press':
                Vibroeffects.VibroManager.g_instance.playButtonClickEffect(type)
