# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SituationIndicatorsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class SituationIndicatorsMeta(BaseDAAPIComponent):

    def as_setPerksS(self, items):
        return self.flashObject.as_setPerks(items) if self._isDAAPIInited() else None

    def as_updatePerkS(self, perkName, state, duration, lifeTime):
        return self.flashObject.as_updatePerk(perkName, state, duration, lifeTime) if self._isDAAPIInited() else None

    def as_setWeatherS(self, items):
        return self.flashObject.as_setWeather(items) if self._isDAAPIInited() else None

    def as_updateWeatherS(self, weatherName, state, toolTip):
        return self.flashObject.as_updateWeather(weatherName, state, toolTip) if self._isDAAPIInited() else None

    def as_clearPanelS(self):
        return self.flashObject.as_clearPanel() if self._isDAAPIInited() else None

    def as_replayPauseS(self, isPaused):
        return self.flashObject.as_replayPause(isPaused) if self._isDAAPIInited() else None
