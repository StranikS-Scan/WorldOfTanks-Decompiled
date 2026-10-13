# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/sounds/souls_collector_sound.py
from __future__ import absolute_import, division
import SoundGroups
from halloween.gui.sounds.sound_constants import SoulsCollectorSounds, SOULS_COLLECTOR_OBJ_NAME
from halloween.gui.sounds import playSound

class SoulsCollectorSound(object):

    def __init__(self, collectorComp):
        self._soulsCollectorSoundObject = SoundGroups.g_instance.WWgetSoundObject(SOULS_COLLECTOR_OBJ_NAME, collectorComp.entity.matrix)
        self._soulsCollectorSoundObject.play(SoulsCollectorSounds.LOOP)
        self._needNotifyCollectorFullFilled = True

    def destroy(self):
        if self._soulsCollectorSoundObject:
            self._soulsCollectorSoundObject.stopAll()
            self._soulsCollectorSoundObject = None
        return

    def updateSoulsCollectorState(self, collected, capacity, isCollecting):
        self._soulsCollectorSoundObject.setRTPC(SoulsCollectorSounds.RTPC, float(collected) / capacity * 100)
        if collected > 0 and self._needNotifyCollectorFullFilled and collected >= capacity:
            self._needNotifyCollectorFullFilled = False
            playSound(SoulsCollectorSounds.FULL)
        elif collected <= 0:
            self._needNotifyCollectorFullFilled = True

    def onFilling(self, collected):
        if collected > 0:
            playSound(SoulsCollectorSounds.COLLECT)
