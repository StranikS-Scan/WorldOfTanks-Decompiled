# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EULAMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class EULAMeta(AbstractWindowView):

    def requestEULAText(self):
        self._printOverrideError('requestEULAText')

    def onLinkClick(self, url):
        self._printOverrideError('onLinkClick')

    def onApply(self):
        self._printOverrideError('onApply')

    def as_setEULATextS(self, text):
        if self._isDAAPIInited():
            return self.flashObject.as_setEULAText(text)
