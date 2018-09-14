# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PremiumWindowMeta.py
from gui.Scaleform.daapi.view.meta.SimpleWindowMeta import SimpleWindowMeta

class PremiumWindowMeta(SimpleWindowMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends SimpleWindowMeta
    null
    """

    def onRateClick(self, rateId):
        """
        :param rateId:
        :return :
        """
        self._printOverrideError('onRateClick')

    def as_setHeaderS(self, prc, bonus1, bonus2):
        """
        :param prc:
        :param bonus1:
        :param bonus2:
        :return :
        """
        return self.flashObject.as_setHeader(prc, bonus1, bonus2) if self._isDAAPIInited() else None

    def as_setRatesS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setRates(data) if self._isDAAPIInited() else None
