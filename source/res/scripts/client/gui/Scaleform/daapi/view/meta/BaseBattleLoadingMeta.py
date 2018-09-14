# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseBattleLoadingMeta.py
from gui.Scaleform.framework.entities.View import View

class BaseBattleLoadingMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def as_setProgressS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setProgress(value) if self._isDAAPIInited() else None

    def as_setTipS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setTip(value) if self._isDAAPIInited() else None

    def as_setTipTitleS(self, title):
        """
        :param title:
        :return :
        """
        return self.flashObject.as_setTipTitle(title) if self._isDAAPIInited() else None

    def as_setEventInfoPanelDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setEventInfoPanelData(data) if self._isDAAPIInited() else None

    def as_setArenaInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setArenaInfo(data) if self._isDAAPIInited() else None

    def as_setMapIconS(self, source):
        """
        :param source:
        :return :
        """
        return self.flashObject.as_setMapIcon(source) if self._isDAAPIInited() else None

    def as_setVisualTipInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setVisualTipInfo(data) if self._isDAAPIInited() else None

    def as_setPlayerDataS(self, playerVehicleID, prebattleID):
        """
        :param playerVehicleID:
        :param prebattleID:
        :return :
        """
        return self.flashObject.as_setPlayerData(playerVehicleID, prebattleID) if self._isDAAPIInited() else None

    def as_setVehiclesDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setVehiclesData(data) if self._isDAAPIInited() else None

    def as_addVehicleInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_addVehicleInfo(data) if self._isDAAPIInited() else None

    def as_updateVehicleInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateVehicleInfo(data) if self._isDAAPIInited() else None

    def as_setVehicleStatusS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setVehicleStatus(data) if self._isDAAPIInited() else None

    def as_setPlayerStatusS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setPlayerStatus(data) if self._isDAAPIInited() else None
