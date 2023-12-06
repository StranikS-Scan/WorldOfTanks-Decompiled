# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/tooltips/ny_total_bonus_tooltip.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_LAST_SEEN_TOTAL_BONUS
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_total_bonus_tooltip_model import NyTotalBonusTooltipModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_multiplier_value import NyMultiplierValue
from new_year.ny_bonuses import BonusHelper
from shared_utils import inPercents
from skeletons.new_year import INewYearController
from helpers import dependency
from gui.impl import backport

class NyTotalBonusTooltip(View):
    __slots__ = ()
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(NyTotalBonusTooltip, self).__init__(ViewSettings(R.views.lobby.new_year.tooltips.NyTotalBonusTooltip(), model=NyTotalBonusTooltipModel()))

    @property
    def viewModel(self):
        return super(NyTotalBonusTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        prevBonus = AccountSettings.getNewYear(NY_LAST_SEEN_TOTAL_BONUS)
        currentBonus = self._nyController.getActiveSettingBonusValue()
        with self.viewModel.transaction() as tx:
            tx.setMaxBonus(inPercents(BonusHelper.getCommonMaxBonus(), digitsToRound=0))
            tx.setPrevBonus(inPercents(prevBonus))
            tx.setCurrentBonus(inPercents(currentBonus))
            self.__createMultipliersTable(tx.getMultipliersTable())
        AccountSettings.setNewYear(NY_LAST_SEEN_TOTAL_BONUS, currentBonus)

    def __createMultipliersTable(self, multipliersTable):
        multipliersTable.clear()
        currentUniqueToysRating = BonusHelper.getUniqueToyRating()
        rangedMultipliersList = BonusHelper.getCommonRangedUniqueToysBonuses()
        rangedMultipliersListLen = len(rangedMultipliersList)
        for index, multiplierRange in enumerate(rangedMultipliersList):
            multiplier, fromToys, toToys = multiplierRange
            singleLevel = index + 1 == rangedMultipliersListLen
            levelInterval = str(fromToys) if singleLevel else backport.text(R.strings.ny.totalBonusTooltip.toysPattern(), lower=fromToys, higher=toToys)
            tableRow = NyMultiplierValue()
            tableRow.setMultiplier(inPercents(multiplier))
            tableRow.setToys(levelInterval)
            tableRow.setIsEnabled(fromToys <= currentUniqueToysRating <= toToys)
            multipliersTable.addViewModel(tableRow)

        multipliersTable.invalidate()
