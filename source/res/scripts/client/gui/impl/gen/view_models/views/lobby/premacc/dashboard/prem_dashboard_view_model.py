# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_view_model.py
from frameworks.wulf import ViewModel
from frameworks.wulf import View

class PremDashboardViewModel(ViewModel):
    __slots__ = ('onCloseAction', 'onInitialized')

    def getHeader(self):
        return self._getView(0)

    def setHeader(self, value):
        self._setView(0, value)

    def getPremiumCard(self):
        return self._getView(1)

    def setPremiumCard(self, value):
        self._setView(1, value)

    def getDoubleXPCard(self):
        return self._getView(2)

    def setDoubleXPCard(self, value):
        self._setView(2, value)

    def getPiggyBankCard(self):
        return self._getView(3)

    def setPiggyBankCard(self, value):
        self._setView(3, value)

    def getPremiumQuestsCard(self):
        return self._getView(4)

    def setPremiumQuestsCard(self, value):
        self._setView(4, value)

    def getMapsBlackListCard(self):
        return self._getView(5)

    def setMapsBlackListCard(self, value):
        self._setView(5, value)

    def _initialize(self):
        super(PremDashboardViewModel, self)._initialize()
        self._addViewProperty('header')
        self._addViewProperty('premiumCard')
        self._addViewProperty('doubleXPCard')
        self._addViewProperty('piggyBankCard')
        self._addViewProperty('premiumQuestsCard')
        self._addViewProperty('mapsBlackListCard')
        self.onCloseAction = self._addCommand('onCloseAction')
        self.onInitialized = self._addCommand('onInitialized')
