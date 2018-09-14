# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/GoldFishWindowMeta.py
from gui.Scaleform.daapi.view.meta.SimpleWindowMeta import SimpleWindowMeta

class GoldFishWindowMeta(SimpleWindowMeta):

    def eventHyperLinkClicked(self):
        self._printOverrideError('eventHyperLinkClicked')

    def as_setWindowTextsS(self, header, eventTitle, eventText, eventLink):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowTexts(header, eventTitle, eventText, eventLink)
