# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_quest_mode_tooltip.py
from frameworks.wulf import ViewSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_quest_mode_tooltip_model import NyQuestModeTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class NyQuestModeTooltip(ViewImpl):
    __slots__ = ('__battleModes', '__minVehicleLevel', '__maxVehicleLevel')

    def __init__(self, battleModes, minVehicleLevel, maxVehicleLevel):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyQuestModeTooltip())
        settings.model = NyQuestModeTooltipModel()
        super(NyQuestModeTooltip, self).__init__(settings)
        self.__battleModes = battleModes.split(',')
        self.__minVehicleLevel = minVehicleLevel
        self.__maxVehicleLevel = maxVehicleLevel

    @property
    def viewModel(self):
        return super(NyQuestModeTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyQuestModeTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            battleModes = model.getBattleModes()
            for battleMode in self.__battleModes:
                battleModes.addString(battleMode)

            battleModes.invalidate()
            model.setMinVehicleLevel(self.__minVehicleLevel)
            model.setMaxVehicleLevel(self.__maxVehicleLevel)
