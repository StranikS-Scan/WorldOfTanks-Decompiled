# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/details_stats_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.details_group_model import DetailsGroupModel
from gui.impl.gen.view_models.views.lobby.postbattle.premium_bonuses_model import PremiumBonusesModel

class DetailsStatsModel(ViewModel):
    __slots__ = ()
    RECORD_TYPE = 'record'
    EARNINGS_SUBGROUP_TYPE = 'earningsSubgroup'
    EXPENSES_SUBGROUP_TYPE = 'expensesSubgroup'
    CREDITS_GROUP_TYPE = 'creditsGroup'
    XP_GROUP_TYPE = 'xpGroup'
    CRYSTALS_GROUP_TYPE = 'crystalsGroup'
    PREMIUM_EARNINGS_GROUP_TYPE = 'premiumBenefits'

    def __init__(self, properties=2, commands=0):
        super(DetailsStatsModel, self).__init__(properties=properties, commands=commands)

    @property
    def premiumBonuses(self):
        return self._getViewModel(0)

    def getGroups(self):
        return self._getArray(1)

    def setGroups(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(DetailsStatsModel, self)._initialize()
        self._addViewModelProperty('premiumBonuses', PremiumBonusesModel())
        self._addArrayProperty('groups', Array())
