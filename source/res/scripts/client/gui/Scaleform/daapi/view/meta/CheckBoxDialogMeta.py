# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CheckBoxDialogMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class CheckBoxDialogMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def onCheckBoxChange(self, isSelected):
        """
        :param isSelected:
        :return :
        """
        self._printOverrideError('onCheckBoxChange')

    def as_setCheckBoxLabelS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCheckBoxLabel(value) if self._isDAAPIInited() else None

    def as_setCheckBoxSelectedS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCheckBoxSelected(value) if self._isDAAPIInited() else None

    def as_setCheckBoxEnabledS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCheckBoxEnabled(value) if self._isDAAPIInited() else None
