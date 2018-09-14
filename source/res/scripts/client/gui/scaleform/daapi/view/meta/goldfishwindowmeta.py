# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/GoldFishWindowMeta.py
from gui.Scaleform.daapi.view.meta.SimpleWindowMeta import SimpleWindowMeta

class GoldFishWindowMeta(SimpleWindowMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SimpleWindowMeta
    null
    """

    def eventHyperLinkClicked(self):
        """
        :return :
        """
        self._printOverrideError('eventHyperLinkClicked')

    def as_setWindowTextsS(self, header, eventTitle, eventText, eventLink):
        """
        :param header:
        :param eventTitle:
        :param eventText:
        :param eventLink:
        :return :
        """
        return self.flashObject.as_setWindowTexts(header, eventTitle, eventText, eventLink) if self._isDAAPIInited() else None
