# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseBattleLoadingMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BaseBattleLoadingMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def as_setProgressS(self, value):
        return self.flashObject.as_setProgress(value) if self._isDAAPIInited() else None

    def as_setMapIconS(self, source):
        return self.flashObject.as_setMapIcon(source) if self._isDAAPIInited() else None

    def as_setPlayerDataS(self, playerVehicleID, prebattleID):
        return self.flashObject.as_setPlayerData(playerVehicleID, prebattleID) if self._isDAAPIInited() else None

    def as_setEventInfoPanelDataS(self, data):
        """
        :param data: Represented by EventInfoPanelVO (AS)
        """
        return self.flashObject.as_setEventInfoPanelData(data) if self._isDAAPIInited() else None

    def as_setTipS(self, value):
        return self.flashObject.as_setTip(value) if self._isDAAPIInited() else None

    def as_setTipTitleS(self, title):
        return self.flashObject.as_setTipTitle(title) if self._isDAAPIInited() else None

    def as_setVisualTipInfoS(self, data):
        """
        :param data: Represented by VisualTipInfoVO (AS)
        """
        return self.flashObject.as_setVisualTipInfo(data) if self._isDAAPIInited() else None
