# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortModernizationWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortModernizationWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def applyAction(self):
        """
        :return :
        """
        self._printOverrideError('applyAction')

    def openOrderDetailsWindow(self):
        """
        :return :
        """
        self._printOverrideError('openOrderDetailsWindow')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_applyButtonLblS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_applyButtonLbl(value) if self._isDAAPIInited() else None

    def as_cancelButtonS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_cancelButton(value) if self._isDAAPIInited() else None

    def as_windowTitleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_windowTitle(value) if self._isDAAPIInited() else None
