# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DGSound3DComponent.py
import typing
from DGSoundAbstractComponent import DGSoundAbstractComponent
from DGSound3DObjectComponent import DGSound3DObjectComponent

class DGSound3DComponent(DGSoundAbstractComponent):

    @property
    def soundObject(self):
        if self.entity is None or self.entity.isDestroyed:
            return
        else:
            component = self.entity.dynamicComponents.get(DGSound3DObjectComponent.__name__)
            return component.soundObject if component else None

    def _play(self, soundName):
        if self.soundObject is not None:
            self.soundObject.play(soundName)
        return
