# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleMarkersManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehicleMarkersManagerMeta(BaseDAAPIComponent):

    def as_setMarkerDurationS(self, duration):
        return self.flashObject.as_setMarkerDuration(duration) if self._isDAAPIInited() else None

    def as_setMarkerSettingsS(self, settings):
        return self.flashObject.as_setMarkerSettings(settings) if self._isDAAPIInited() else None

    def as_setShowExInfoFlagS(self, flag):
        return self.flashObject.as_setShowExInfoFlag(flag) if self._isDAAPIInited() else None

    def as_updateMarkersSettingsS(self):
        return self.flashObject.as_updateMarkersSettings() if self._isDAAPIInited() else None

    def as_setColorBlindS(self, isColorBlind):
        return self.flashObject.as_setColorBlind(isColorBlind) if self._isDAAPIInited() else None

    def as_setColorSchemesS(self, defaultSchemes, colorBlindSchemes):
        return self.flashObject.as_setColorSchemes(defaultSchemes, colorBlindSchemes) if self._isDAAPIInited() else None
