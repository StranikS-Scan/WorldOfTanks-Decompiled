# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleParametersMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehicleParametersMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onParamClick(self, paramID):
        self._printOverrideError('onParamClick')

    def onListScroll(self):
        self._printOverrideError('onListScroll')

    def as_getDPS(self):
        return self.flashObject.as_getDP() if self._isDAAPIInited() else None

    def as_setRendererLnkS(self, rendererLnk):
        return self.flashObject.as_setRendererLnk(rendererLnk) if self._isDAAPIInited() else None

    def as_setIsParamsAnimatedS(self, isParamsAnimated):
        return self.flashObject.as_setIsParamsAnimated(isParamsAnimated) if self._isDAAPIInited() else None
