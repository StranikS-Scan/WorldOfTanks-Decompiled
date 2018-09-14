# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/IngameHelpWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class IngameHelpWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def clickSettingWindow(self):
        """
        :return :
        """
        self._printOverrideError('clickSettingWindow')

    def as_setKeysS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setKeys(data) if self._isDAAPIInited() else None
