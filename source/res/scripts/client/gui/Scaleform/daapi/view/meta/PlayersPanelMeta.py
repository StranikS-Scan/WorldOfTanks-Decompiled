# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PlayersPanelMeta.py
from gui.Scaleform.daapi.view.battle.classic.base_stats import StatsBase

class PlayersPanelMeta(StatsBase):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends StatsBase
    null
    """

    def tryToSetPanelModeByMouse(self, panelMode):
        """
        :param panelMode:
        :return :
        """
        self._printOverrideError('tryToSetPanelModeByMouse')

    def switchToOtherPlayer(self, vehicleID):
        """
        :param vehicleID:
        :return :
        """
        self._printOverrideError('switchToOtherPlayer')

    def as_setPanelModeS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setPanelMode(value) if self._isDAAPIInited() else None
