# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationPropertiesSheetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CustomizationPropertiesSheetMeta(BaseDAAPIComponent):

    def onActionBtnClick(self, actionType, actionData):
        self._printOverrideError('onActionBtnClick')

    def editMode(self, value, interactionType):
        self._printOverrideError('editMode')

    def interactionStatusUpdate(self, value):
        self._printOverrideError('interactionStatusUpdate')

    def elementControlsHide(self):
        self._printOverrideError('elementControlsHide')

    def onClose(self):
        self._printOverrideError('onClose')

    def as_setDataAndShowS(self, data):
        return self.flashObject.as_setDataAndShow(data) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
