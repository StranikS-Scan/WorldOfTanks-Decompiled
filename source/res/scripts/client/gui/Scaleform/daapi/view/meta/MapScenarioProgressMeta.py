# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MapScenarioProgressMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MapScenarioProgressMeta(BaseDAAPIComponent):

    def as_setMaxValueWaveS(self, value):
        return self.flashObject.as_setMaxValueWave(value) if self._isDAAPIInited() else None

    def as_setCurrentValueWaveS(self, value):
        return self.flashObject.as_setCurrentValueWave(value) if self._isDAAPIInited() else None

    def as_setTitleWaveS(self, title):
        return self.flashObject.as_setTitleWave(title) if self._isDAAPIInited() else None

    def as_setMaxValueBaseS(self, value):
        return self.flashObject.as_setMaxValueBase(value) if self._isDAAPIInited() else None

    def as_setCurrentValueProbableDamageBaseS(self, currentValue, probableDamageValue, isNoAnim):
        return self.flashObject.as_setCurrentValueProbableDamageBase(currentValue, probableDamageValue, isNoAnim) if self._isDAAPIInited() else None

    def as_setTitleBaseS(self, title):
        return self.flashObject.as_setTitleBase(title) if self._isDAAPIInited() else None
