# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MarkPreviewMeta.py
from gui.Scaleform.daapi.view.meta.VehiclePreviewMeta import VehiclePreviewMeta

class MarkPreviewMeta(VehiclePreviewMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends VehiclePreviewMeta
    null
    """

    def as_show3DSceneTooltipS(self, id, args):
        """
        :param id:
        :param args:
        :return :
        """
        return self.flashObject.as_show3DSceneTooltip(id, args) if self._isDAAPIInited() else None

    def as_hide3DSceneTooltipS(self):
        """
        :return :
        """
        return self.flashObject.as_hide3DSceneTooltip() if self._isDAAPIInited() else None
