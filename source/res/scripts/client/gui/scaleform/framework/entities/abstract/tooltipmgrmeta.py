# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ToolTipMgrMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ToolTipMgrMeta(BaseDAAPIModule):

    def onCreateComplexTooltip(self, tooltipId, stateType):
        self._printOverrideError('onCreateComplexTooltip')

    def onCreateTypedTooltip(self, type, args, stateType):
        self._printOverrideError('onCreateTypedTooltip')

    def as_showS(self, tooltipData, linkage):
        if self._isDAAPIInited():
            return self.flashObject.as_show(tooltipData, linkage)
