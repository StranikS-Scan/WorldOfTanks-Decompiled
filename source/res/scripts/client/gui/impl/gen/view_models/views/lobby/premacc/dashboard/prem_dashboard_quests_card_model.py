# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_quests_card_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class PremDashboardQuestsCardModel(ViewModel):
    __slots__ = ('onGoToQuestsView',)
    DISABLED = 'disabled'
    IN_PROGRESS = 'inprogress'
    COMPLETED = 'complete'

    def __init__(self, properties=3, commands=1):
        super(PremDashboardQuestsCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def premiumQuests(self):
        return self._getViewModel(0)

    def getIsAvailable(self):
        return self._getBool(1)

    def setIsAvailable(self, value):
        self._setBool(1, value)

    def getIsTankPremiumActive(self):
        return self._getBool(2)

    def setIsTankPremiumActive(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PremDashboardQuestsCardModel, self)._initialize()
        self._addViewModelProperty('premiumQuests', ListModel())
        self._addBoolProperty('isAvailable', False)
        self._addBoolProperty('isTankPremiumActive', False)
        self.onGoToQuestsView = self._addCommand('onGoToQuestsView')
