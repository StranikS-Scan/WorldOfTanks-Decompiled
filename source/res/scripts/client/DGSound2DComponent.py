# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DGSound2DComponent.py
import SoundGroups
from DGSoundAbstractComponent import DGSoundAbstractComponent

class DGSound2DComponent(DGSoundAbstractComponent):

    def _play(self, soundName):
        SoundGroups.g_instance.playSound2D(soundName)
