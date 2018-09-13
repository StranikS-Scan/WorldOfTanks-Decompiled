# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PremiumFormMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PremiumFormMeta(DAAPIModule):

    def onPremiumBuy(self, days, price):
        self._printOverrideError('onPremiumBuy')

    def onPremiumDataRequest(self):
        self._printOverrideError('onPremiumDataRequest')

    def as_setCostsS(self, costs):
        if self._isDAAPIInited():
            return self.flashObject.as_setCosts(costs)

    def as_setGoldS(self, gold):
        if self._isDAAPIInited():
            return self.flashObject.as_setGold(gold)

    def as_setPremiumS(self, isPremium):
        if self._isDAAPIInited():
            return self.flashObject.as_setPremium(isPremium)
