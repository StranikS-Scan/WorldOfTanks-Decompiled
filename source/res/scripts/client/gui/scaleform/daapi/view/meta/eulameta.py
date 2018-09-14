# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EULAMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class EULAMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def requestEULAText(self):
        """
        :return :
        """
        self._printOverrideError('requestEULAText')

    def onLinkClick(self, url):
        """
        :param url:
        :return :
        """
        self._printOverrideError('onLinkClick')

    def onApply(self):
        """
        :return :
        """
        self._printOverrideError('onApply')

    def as_setEULATextS(self, text):
        """
        :param text:
        :return :
        """
        return self.flashObject.as_setEULAText(text) if self._isDAAPIInited() else None
