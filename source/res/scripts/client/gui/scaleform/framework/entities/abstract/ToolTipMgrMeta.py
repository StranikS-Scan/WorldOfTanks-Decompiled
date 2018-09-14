# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ToolTipMgrMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ToolTipMgrMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def onCreateComplexTooltip(self, tooltipId, stateType):
        """
        :param tooltipId:
        :param stateType:
        :return :
        """
        self._printOverrideError('onCreateComplexTooltip')

    def onCreateTypedTooltip(self, tooltipType, args, stateType):
        """
        :param tooltipType:
        :param args:
        :param stateType:
        :return :
        """
        self._printOverrideError('onCreateTypedTooltip')

    def as_showS(self, tooltipData, linkage):
        """
        :param tooltipData:
        :param linkage:
        :return :
        """
        return self.flashObject.as_show(tooltipData, linkage) if self._isDAAPIInited() else None
