# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortTransportConfirmationWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortTransportConfirmationWindowMeta(AbstractWindowView):

    def onCancel(self):
        self._printOverrideError('onCancel')

    def onTransporting(self, size):
        self._printOverrideError('onTransporting')

    def as_setMaxTransportingSizeS(self, maxSizeStr):
        if self._isDAAPIInited():
            return self.flashObject.as_setMaxTransportingSize(maxSizeStr)

    def as_setFooterTextS(self, text):
        if self._isDAAPIInited():
            return self.flashObject.as_setFooterText(text)

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_enableForFirstTransportingS(self, isFirstTransporting):
        if self._isDAAPIInited():
            return self.flashObject.as_enableForFirstTransporting(isFirstTransporting)
