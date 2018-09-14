# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsTileChainsViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class QuestsTileChainsViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def getTileData(self, vehicleType, taskFilterType):
        """
        :param vehicleType:
        :param taskFilterType:
        :return :
        """
        self._printOverrideError('getTileData')

    def getChainProgress(self):
        """
        :return :
        """
        self._printOverrideError('getChainProgress')

    def getTaskDetails(self, taskId):
        """
        :param taskId:
        :return :
        """
        self._printOverrideError('getTaskDetails')

    def selectTask(self, taskId):
        """
        :param taskId:
        :return :
        """
        self._printOverrideError('selectTask')

    def refuseTask(self, taskId):
        """
        :param taskId:
        :return :
        """
        self._printOverrideError('refuseTask')

    def gotoBack(self):
        """
        :return :
        """
        self._printOverrideError('gotoBack')

    def showAwardVehicleInfo(self, awardVehicleID):
        """
        :param awardVehicleID:
        :return :
        """
        self._printOverrideError('showAwardVehicleInfo')

    def showAwardVehicleInHangar(self, awardVehicleID):
        """
        :param awardVehicleID:
        :return :
        """
        self._printOverrideError('showAwardVehicleInHangar')

    def as_setHeaderDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_updateTileDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateTileData(data) if self._isDAAPIInited() else None

    def as_updateChainProgressS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateChainProgress(data) if self._isDAAPIInited() else None

    def as_updateTaskDetailsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateTaskDetails(data) if self._isDAAPIInited() else None

    def as_setSelectedTaskS(self, taskId):
        """
        :param taskId:
        :return :
        """
        return self.flashObject.as_setSelectedTask(taskId) if self._isDAAPIInited() else None
