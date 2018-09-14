# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CAPTCHAMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class CAPTCHAMeta(AbstractWindowView):

    def submit(self, responce):
        self._printOverrideError('submit')

    def reload(self):
        self._printOverrideError('reload')

    def as_setImageS(self, imageURL, width, height):
        if self._isDAAPIInited():
            return self.flashObject.as_setImage(imageURL, width, height)

    def as_setErrorMessageS(self, message):
        if self._isDAAPIInited():
            return self.flashObject.as_setErrorMessage(message)
