# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StaticFormationStatsViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StaticFormationStatsViewMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def selectSeason(self, index):
        self._printOverrideError('selectSeason')

    def as_setDataS(self, data):
        """
        :param data: Represented by StaticFormationStatsViewVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setStatsS(self, data):
        """
        :param data: Represented by StaticFormationStatsVO (AS)
        """
        return self.flashObject.as_setStats(data) if self._isDAAPIInited() else None
