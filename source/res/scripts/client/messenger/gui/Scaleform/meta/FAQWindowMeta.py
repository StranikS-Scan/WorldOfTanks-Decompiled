# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/FAQWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FAQWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def onLinkClicked(self, name):
        """
        :param name:
        :return :
        """
        self._printOverrideError('onLinkClicked')

    def as_appendTextS(self, text):
        """
        :param text:
        :return :
        """
        return self.flashObject.as_appendText(text) if self._isDAAPIInited() else None
