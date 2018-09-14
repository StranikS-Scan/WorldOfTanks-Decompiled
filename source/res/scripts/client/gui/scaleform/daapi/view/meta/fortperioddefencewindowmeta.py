# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortPeriodDefenceWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortPeriodDefenceWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def onApply(self, data):
        self._printOverrideError('onApply')

    def onCancel(self):
        self._printOverrideError('onCancel')

    def as_setDataS(self, data):
        """
        :param data: Represented by PeriodDefenceVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        """
        :param data: Represented by PeriodDefenceInitVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None
