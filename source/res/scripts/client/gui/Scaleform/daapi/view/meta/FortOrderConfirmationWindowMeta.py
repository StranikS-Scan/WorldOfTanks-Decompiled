# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderConfirmationWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortOrderConfirmationWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def submit(self, count):
        """
        :param count:
        :return :
        """
        self._printOverrideError('submit')

    def getTimeStr(self, time):
        """
        :param time:
        :return String:
        """
        self._printOverrideError('getTimeStr')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setSettingsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setSettings(data) if self._isDAAPIInited() else None
