# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationInscriptionControllerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CustomizationInscriptionControllerMeta(BaseDAAPIComponent):

    def sendChar(self, char):
        self._printOverrideError('sendChar')

    def finish(self):
        self._printOverrideError('finish')

    def removeChar(self):
        self._printOverrideError('removeChar')

    def deleteAll(self):
        self._printOverrideError('deleteAll')

    def as_showS(self, inscriptionLength):
        return self.flashObject.as_show(inscriptionLength) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_invalidInscriptionS(self, data):
        return self.flashObject.as_invalidInscription(data) if self._isDAAPIInited() else None

    def as_showHintS(self, data):
        return self.flashObject.as_showHint(data) if self._isDAAPIInited() else None
