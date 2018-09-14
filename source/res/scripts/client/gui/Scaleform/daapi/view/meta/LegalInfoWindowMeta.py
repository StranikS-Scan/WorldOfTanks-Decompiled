# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LegalInfoWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class LegalInfoWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def getLegalInfo(self):
        """
        :return :
        """
        self._printOverrideError('getLegalInfo')

    def onCancelClick(self):
        """
        :return :
        """
        self._printOverrideError('onCancelClick')

    def as_setLegalInfoS(self, legalInfo):
        """
        :param legalInfo:
        :return :
        """
        return self.flashObject.as_setLegalInfo(legalInfo) if self._isDAAPIInited() else None
