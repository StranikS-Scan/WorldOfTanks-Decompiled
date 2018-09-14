# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TeamBasesPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TeamBasesPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def as_addS(self, barId, sortWeight, colorType, title, points, captureTime, vehiclesCount):
        """
        :param barId:
        :param sortWeight:
        :param colorType:
        :param title:
        :param points:
        :param captureTime:
        :param vehiclesCount:
        :return :
        """
        return self.flashObject.as_add(barId, sortWeight, colorType, title, points, captureTime, vehiclesCount) if self._isDAAPIInited() else None

    def as_removeS(self, id):
        """
        :param id:
        :return :
        """
        return self.flashObject.as_remove(id) if self._isDAAPIInited() else None

    def as_stopCaptureS(self, id, points):
        """
        :param id:
        :param points:
        :return :
        """
        return self.flashObject.as_stopCapture(id, points) if self._isDAAPIInited() else None

    def as_updateCaptureDataS(self, id, points, rate, captureTime, vehiclesCount):
        """
        :param id:
        :param points:
        :param rate:
        :param captureTime:
        :param vehiclesCount:
        :return :
        """
        return self.flashObject.as_updateCaptureData(id, points, rate, captureTime, vehiclesCount) if self._isDAAPIInited() else None

    def as_setCapturedS(self, id, title):
        """
        :param id:
        :param title:
        :return :
        """
        return self.flashObject.as_setCaptured(id, title) if self._isDAAPIInited() else None

    def as_setOffsetForEnemyPointsS(self):
        """
        :return :
        """
        return self.flashObject.as_setOffsetForEnemyPoints() if self._isDAAPIInited() else None

    def as_clearS(self):
        """
        :return :
        """
        return self.flashObject.as_clear() if self._isDAAPIInited() else None
