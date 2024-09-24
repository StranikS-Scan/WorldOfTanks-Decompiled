# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/tooltips/random_national_bonus_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.random_national_bonus_tooltip_view_model import RandomNationalBonusTooltipViewModel
from gui.impl.pub import ViewImpl

class RandomNationalBonusTooltipView(ViewImpl):
    __slots__ = ('__name', '__value', '__icon')

    def __init__(self, name, value, icon):
        settings = ViewSettings(R.views.lobby.lootbox_system.tooltips.RandomNationalBonusTooltipView())
        settings.model = RandomNationalBonusTooltipViewModel()
        super(RandomNationalBonusTooltipView, self).__init__(settings)
        self.__name = name
        self.__value = value
        self.__icon = icon

    @property
    def viewModel(self):
        return super(RandomNationalBonusTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RandomNationalBonusTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vmTx:
            vmTx.setName(self.__name)
            vmTx.setValue(self.__value)
            vmTx.setIcon(self.__icon)
