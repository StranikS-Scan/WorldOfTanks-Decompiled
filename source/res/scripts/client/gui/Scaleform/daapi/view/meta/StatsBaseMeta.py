# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StatsBaseMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StatsBaseMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def acceptSquad(self, uid):
        """
        :param uid:
        :return :
        """
        self._printOverrideError('acceptSquad')

    def addToSquad(self, uid):
        """
        :param uid:
        :return :
        """
        self._printOverrideError('addToSquad')

    def as_setIsIntaractiveS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setIsIntaractive(value) if self._isDAAPIInited() else None
