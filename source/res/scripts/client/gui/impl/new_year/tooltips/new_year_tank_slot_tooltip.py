# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/new_year_tank_slot_tooltip.py
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.new_year_tank_slot_tooltip_model import NewYearTankSlotTooltipModel
from gui.impl.new_year.new_year_helper import IS_ROMAN_NUMBERS_ALLOWED
from new_year.ny_constants import PERCENT
from new_year.vehicle_branch import getRegularSlotBonusConfig
_BONUS_ORDER = ['xpFactor', 'freeXPFactor', 'tankmenXPFactor']

class NewYearTankSlotTooltipContent(View):
    __slots__ = ('__level', '__levelName')

    def __init__(self, level, levelName):
        settings = ViewSettings(R.views.lobby.new_year.tooltips.new_year_tank_slot_tooltip.NewYearTankSlotTooltipContent())
        settings.model = NewYearTankSlotTooltipModel()
        super(NewYearTankSlotTooltipContent, self).__init__(settings)
        self.__level = level
        self.__levelName = levelName

    @property
    def viewModel(self):
        return super(NewYearTankSlotTooltipContent, self).getViewModel()

    def _initialize(self):
        super(NewYearTankSlotTooltipContent, self)._initialize()
        with self.viewModel.transaction() as model:
            model.setLevel(self.__level)
            model.setLevelName(self.__levelName)
            model.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
            for bonusType in _BONUS_ORDER:
                vehBonusValues = []
                for _, (vehBonusType, vehBonusValue) in getRegularSlotBonusConfig().iteritems():
                    if vehBonusType == bonusType:
                        vehBonusValues.append(vehBonusValue)

                if bonusType == 'xpFactor':
                    model.setXpFactor(PERCENT * min(vehBonusValues))
                if bonusType == 'freeXPFactor':
                    model.setFreeXPFactor(PERCENT * min(vehBonusValues))
                if bonusType == 'tankmenXPFactor':
                    model.setTankmenXPFactor(PERCENT * min(vehBonusValues))
