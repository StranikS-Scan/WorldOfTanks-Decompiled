# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SystemMessageDialogMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class SystemMessageDialogMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def as_setInitDataS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setInitData(value) if self._isDAAPIInited() else None

    def as_setMessageDataS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setMessageData(value) if self._isDAAPIInited() else None
