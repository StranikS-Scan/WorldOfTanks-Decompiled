# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleMarkersManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehicleMarkersManagerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_setMarkerDurationS(self, duration):
        """
        :param duration:
        :return :
        """
        return self.flashObject.as_setMarkerDuration(duration) if self._isDAAPIInited() else None

    def as_setMarkerSettingsS(self, settings):
        """
        :param settings:
        :return :
        """
        return self.flashObject.as_setMarkerSettings(settings) if self._isDAAPIInited() else None

    def as_setShowExInfoFlagS(self, flag):
        """
        :param flag:
        :return :
        """
        return self.flashObject.as_setShowExInfoFlag(flag) if self._isDAAPIInited() else None

    def as_updateMarkersSettingsS(self):
        """
        :return :
        """
        return self.flashObject.as_updateMarkersSettings() if self._isDAAPIInited() else None

    def as_setColorBlindS(self, isColorBlind):
        """
        :param isColorBlind:
        :return :
        """
        return self.flashObject.as_setColorBlind(isColorBlind) if self._isDAAPIInited() else None

    def as_setColorSchemesS(self, defaultSchemes, colorBlindSchemes):
        """
        :param defaultSchemes:
        :param colorBlindSchemes:
        :return :
        """
        return self.flashObject.as_setColorSchemes(defaultSchemes, colorBlindSchemes) if self._isDAAPIInited() else None
