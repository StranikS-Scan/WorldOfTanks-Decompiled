# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortChoiceDivisionWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortChoiceDivisionWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def selectedDivision(self, divisionID):
        self._printOverrideError('selectedDivision')

    def changedDivision(self, divisionID):
        self._printOverrideError('changedDivision')

    def as_setDataS(self, data):
        """
        :param data: Represented by FortChoiceDivisionVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
