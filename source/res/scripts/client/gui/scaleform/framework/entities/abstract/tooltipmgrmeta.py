# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ToolTipMgrMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ToolTipMgrMeta(BaseDAAPIComponent):

    def onCreateComplexTooltip(self, tooltipId, stateType):
        self._printOverrideError('onCreateComplexTooltip')

    def onCreateTypedTooltip(self, tooltipType, args, stateType):
        self._printOverrideError('onCreateTypedTooltip')

    def onHideTooltip(self, tooltipId):
        self._printOverrideError('onHideTooltip')

    def as_showS(self, tooltipData, linkage, redraw=False):
        return self.flashObject.as_show(tooltipData, linkage, redraw) if self._isDAAPIInited() else None
