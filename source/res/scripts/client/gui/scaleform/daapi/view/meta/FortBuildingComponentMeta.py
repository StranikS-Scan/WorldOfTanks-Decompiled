# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortBuildingComponentMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onTransportingRequest(self, exportFrom, importTo):
        """
        :param exportFrom:
        :param importTo:
        :return :
        """
        self._printOverrideError('onTransportingRequest')

    def requestBuildingProcess(self, direction, position):
        """
        :param direction:
        :param position:
        :return :
        """
        self._printOverrideError('requestBuildingProcess')

    def upgradeVisitedBuilding(self, uid):
        """
        :param uid:
        :return :
        """
        self._printOverrideError('upgradeVisitedBuilding')

    def requestBuildingToolTipData(self, uid, type):
        """
        :param uid:
        :param type:
        :return :
        """
        self._printOverrideError('requestBuildingToolTipData')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setBuildingDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setBuildingData(data) if self._isDAAPIInited() else None

    def as_setBuildingToolTipDataS(self, uid, type, header, value):
        """
        :param uid:
        :param type:
        :param header:
        :param value:
        :return :
        """
        return self.flashObject.as_setBuildingToolTipData(uid, type, header, value) if self._isDAAPIInited() else None

    def as_refreshTransportingS(self):
        """
        :return :
        """
        return self.flashObject.as_refreshTransporting() if self._isDAAPIInited() else None
