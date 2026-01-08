# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SMSound3DObjectComponent.py
import typing
import SoundGroups
from script_component.DynamicScriptComponent import DynamicScriptComponent

class SMSound3DObjectComponent(DynamicScriptComponent):
    _SOUND_OBJ_NAME_PATTERN = 'SMSound3DObjectComponent_{}'

    def __init__(self):
        super(SMSound3DObjectComponent, self).__init__()
        self._soundObject = SoundGroups.g_instance.WWgetSoundObject(self._SOUND_OBJ_NAME_PATTERN.format(self.entity.id), self.entity.matrix)

    def onDestroy(self):
        self._soundObject.stopAll()
        self._soundObject = None
        super(SMSound3DObjectComponent, self).onDestroy()
        return

    @property
    def soundObject(self):
        return self._soundObject
