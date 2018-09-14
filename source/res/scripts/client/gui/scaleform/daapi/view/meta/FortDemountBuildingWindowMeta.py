# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDemountBuildingWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortDemountBuildingWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def applyDemount(self):
        self._printOverrideError('applyDemount')

    def as_setDataS(self, data):
        """
        :param data: Represented by FortDemountBuildingVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
