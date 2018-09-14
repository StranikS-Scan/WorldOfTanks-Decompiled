# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleParametersMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehicleParametersMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def onParamClick(self, paramID):
        """
        :param paramID:
        :return :
        """
        self._printOverrideError('onParamClick')

    def onListScroll(self):
        """
        :return :
        """
        self._printOverrideError('onListScroll')

    def as_getDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_setRendererLnkS(self, rendererLnk):
        """
        :param rendererLnk:
        :return :
        """
        return self.flashObject.as_setRendererLnk(rendererLnk) if self._isDAAPIInited() else None

    def as_setIsParamsAnimatedS(self, isParamsAnimated):
        """
        :param isParamsAnimated:
        :return :
        """
        return self.flashObject.as_setIsParamsAnimated(isParamsAnimated) if self._isDAAPIInited() else None
