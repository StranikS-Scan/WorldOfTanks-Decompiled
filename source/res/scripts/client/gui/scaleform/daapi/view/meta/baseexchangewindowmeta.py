# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseExchangeWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BaseExchangeWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def exchange(self, data):
        """
        :param data:
        :return :
        """
        self._printOverrideError('exchange')

    def as_setPrimaryCurrencyS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setPrimaryCurrency(value) if self._isDAAPIInited() else None

    def as_exchangeRateS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_exchangeRate(data) if self._isDAAPIInited() else None
