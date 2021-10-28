# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ExchangeTokenWindowMeta.py
from gui.Scaleform.daapi.view.lobby.exchange.ExchangeWindow import ExchangeWindow

class ExchangeTokenWindowMeta(ExchangeWindow):

    def as_setExchangePropertiesS(self, primary, secondary, flipRate):
        return self.flashObject.as_setExchangeProperties(primary, secondary, flipRate) if self._isDAAPIInited() else None
