# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SquadPromoWindowMeta.py
from gui.Scaleform.daapi.view.meta.SimpleWindowMeta import SimpleWindowMeta

class SquadPromoWindowMeta(SimpleWindowMeta):

    def onHyperlinkClick(self):
        self._printOverrideError('onHyperlinkClick')

    def as_setHyperlinkS(self, label):
        if self._isDAAPIInited():
            return self.flashObject.as_setHyperlink(label)
