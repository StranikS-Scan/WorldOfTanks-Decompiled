# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingProcessWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortBuildingProcessWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def requestBuildingInfo(self, uid):
        """
        :param uid:
        :return :
        """
        self._printOverrideError('requestBuildingInfo')

    def applyBuildingProcess(self, uid):
        """
        :param uid:
        :return :
        """
        self._printOverrideError('applyBuildingProcess')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_responseBuildingInfoS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_responseBuildingInfo(data) if self._isDAAPIInited() else None
