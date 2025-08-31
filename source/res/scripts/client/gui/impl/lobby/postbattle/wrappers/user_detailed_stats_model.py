# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/postbattle/wrappers/user_detailed_stats_model.py
import typing
from gui.impl.gen.view_models.views.lobby.postbattle.details_stats_model import DetailsStatsModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.postbattle.details_group_model import DetailsGroupModel

class UserDetailedStatsModel(DetailsStatsModel):
    __slots__ = ('__creditsModel', '__crystalsModel', '__xpModel', '__premiumEarningsModel')

    def __init__(self):
        super(UserDetailedStatsModel, self).__init__()
        self.__creditsModel = None
        self.__crystalsModel = None
        self.__xpModel = None
        self.__premiumEarningsModel = None
        return

    def setCredits(self, model):
        if not self.__creditsModel:
            self.__creditsModel = model
            self.getGroups().addViewModel(model)
        else:
            self.__creditsModel.setRecords(model.getRecords())

    def setCrystals(self, model):
        if not self.__crystalsModel:
            self.__crystalsModel = model
            self.getGroups().addViewModel(model)
        else:
            self.__crystalsModel.setRecords(model.getRecords())

    def setXP(self, model):
        if not self.__xpModel:
            self.__xpModel = model
            self.getGroups().addViewModel(model)
        else:
            self.__xpModel.setRecords(model.getRecords())

    def setPremiumBonus(self, currencies):
        self.premiumBonuses.setCurrencies(currencies)

    def invalidate(self):
        self.getGroups().invalidate()
        self.premiumBonuses.getCurrencies().invalidate()

    def _finalize(self):
        self.__creditsModel = None
        self.__crystalsModel = None
        self.__xpModel = None
        self.__premiumEarningsModel = None
        super(UserDetailedStatsModel, self)._finalize()
        return
