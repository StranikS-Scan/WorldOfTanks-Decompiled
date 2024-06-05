# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/items/sm_artefacts.py
import items.artefacts as artefacts

class SPGZoneEquipment(artefacts.AreaOfEffectEquipment):
    __slots__ = ('yawHitPrediction', 'hitPredictionDuration')

    def _readConfig(self, xmlCtx, section):
        super(SPGZoneEquipment, self)._readConfig(xmlCtx, section)
        self.yawHitPrediction = section.readInt('yawHitPrediction', 0)
        self.hitPredictionDuration = section.readFloat('hitPredictionDuration', 0)
