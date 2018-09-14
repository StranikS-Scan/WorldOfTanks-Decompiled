# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReportBugPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ReportBugPanelMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def reportBug(self):
        """
        :return :
        """
        self._printOverrideError('reportBug')

    def as_setHyperLinkS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setHyperLink(value) if self._isDAAPIInited() else None
