# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ConfirmDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ConfirmDialogMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def submit(self, selected):
        """
        :param selected:
        :return :
        """
        self._printOverrideError('submit')

    def as_setSettingsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setSettings(data) if self._isDAAPIInited() else None
