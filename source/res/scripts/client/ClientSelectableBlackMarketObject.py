# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableBlackMarketObject.py
from ClientSelectableObject import ClientSelectableObject
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBlackMarketUrl
from gui.shared.event_dispatcher import showShop

class ClientSelectableBlackMarketObject(ClientSelectableObject):

    def __init__(self):
        super(ClientSelectableBlackMarketObject, self).__init__()
        self.clickSoundName = 'black_market_car'

    def onMouseClick(self):
        super(ClientSelectableBlackMarketObject, self).onMouseClick()
        showShop(url=getBlackMarketUrl())
