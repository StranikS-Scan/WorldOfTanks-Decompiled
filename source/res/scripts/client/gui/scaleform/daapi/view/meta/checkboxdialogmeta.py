# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CheckBoxDialogMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CheckBoxDialogMeta(BaseDAAPIComponent):

    def onCheckBoxChange(self, isSelected):
        self._printOverrideError('onCheckBoxChange')

    def as_setCheckBoxLabelS(self, value):
        return self.flashObject.as_setCheckBoxLabel(value) if self._isDAAPIInited() else None

    def as_setCheckBoxSelectedS(self, value):
        return self.flashObject.as_setCheckBoxSelected(value) if self._isDAAPIInited() else None

    def as_setCheckBoxEnabledS(self, value):
        return self.flashObject.as_setCheckBoxEnabled(value) if self._isDAAPIInited() else None
