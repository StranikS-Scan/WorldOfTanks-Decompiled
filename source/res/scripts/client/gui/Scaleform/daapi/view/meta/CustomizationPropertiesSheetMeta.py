# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationPropertiesSheetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CustomizationPropertiesSheetMeta(BaseDAAPIComponent):

    def onActionBtnClick(self, actionType, actionData):
        self._printOverrideError('onActionBtnClick')

    def elementControlsHide(self):
        self._printOverrideError('elementControlsHide')

    def onClose(self):
        self._printOverrideError('onClose')

    def registerInscriptionController(self, inscriptionController, inputLines):
        self._printOverrideError('registerInscriptionController')

    def as_setDataAndShowS(self, data):
        return self.flashObject.as_setDataAndShow(data) if self._isDAAPIInited() else None

    def as_setArrowsStatesS(self, left, right):
        return self.flashObject.as_setArrowsStates(left, right) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
