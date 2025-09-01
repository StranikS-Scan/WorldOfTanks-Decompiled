# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DGSound3DObjectComponent.py
import typing
import SoundGroups
from script_component.DynamicScriptComponent import DynamicScriptComponent

class DGSound3DObjectComponent(DynamicScriptComponent):
    _SOUND_OBJ_NAME_PATTERN = 'DGSound3DObjectComponent_{}'

    def __init__(self):
        super(DGSound3DObjectComponent, self).__init__()
        self._soundObject = SoundGroups.g_instance.WWgetSoundObject(self._SOUND_OBJ_NAME_PATTERN.format(self.entity.id), self.entity.matrix)

    def onDestroy(self):
        self._soundObject.stopAll()
        self._soundObject = None
        super(DGSound3DObjectComponent, self).onDestroy()
        return

    @property
    def soundObject(self):
        return self._soundObject
