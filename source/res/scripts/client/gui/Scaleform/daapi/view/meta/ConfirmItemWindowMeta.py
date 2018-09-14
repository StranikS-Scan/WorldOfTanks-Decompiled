# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ConfirmItemWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ConfirmItemWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def submit(self, count, currency):
        """
        :param count:
        :param currency:
        :return :
        """
        self._printOverrideError('submit')

    def as_setDataS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None

    def as_setSettingsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setSettings(data) if self._isDAAPIInited() else None
