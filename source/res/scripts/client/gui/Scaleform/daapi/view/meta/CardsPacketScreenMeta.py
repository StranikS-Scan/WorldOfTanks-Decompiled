# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CardsPacketScreenMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CardsPacketScreenMeta(BaseDAAPIComponent):

    def onOpenCarsClick(self):
        self._printOverrideError('onOpenCarsClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setCardsS(self, cards):
        return self.flashObject.as_setCards(cards) if self._isDAAPIInited() else None
