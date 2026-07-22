# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/tooltips/economy_bonus_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from helpers import dependency
from mt_birthday.gui.impl.gen.view_models.views.lobby.tooltips.economy_bonus_tooltip_model import EconomyBonusTooltipModel
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IBRProgressionOnTokensController
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController

class EconomyBonusTooltip(ViewImpl):
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)
    __brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.mt_birthday.lobby.tooltips.EconomyBonusTooltip(), model=EconomyBonusTooltipModel())
        super(EconomyBonusTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EconomyBonusTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            tx.setPercent(self.__tankBirthdayController.getEconomyBonusValue())
            self.__fillBattleTypes(tx)

    def __fillBattleTypes(self, model):
        array = model.getModes()
        for bonusType in self.__tankBirthdayController.getEconomicBonusTypes():
            bonusType = self.__brProgression.checkBRBattleTypeForIcon(bonusType)
            array.addNumber(bonusType)

        array.invalidate()
