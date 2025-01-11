# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/task_condition_tooltip_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.tooltips.task_condition_tooltip_view_model import TaskConditionTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R

class TaskConditionTooltipView(ViewImpl):
    __slots__ = ('__vehicleLevels', '__vehicleTypes', '__battleTypes')

    def __init__(self, vehicleLevels, vehicleTypes, battleTypes):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.TaskConditionTooltipView())
        settings.flags = ViewFlags.VIEW
        settings.model = TaskConditionTooltipViewModel()
        self.__vehicleLevels = vehicleLevels
        self.__vehicleTypes = vehicleTypes
        self.__battleTypes = battleTypes
        super(TaskConditionTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TaskConditionTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TaskConditionTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    def __updateModel(self, model):
        model.setLevels(str(self.__vehicleLevels))
        array = model.getVehicleTypes()
        for item in self.__vehicleTypes.split(','):
            array.addString(item)

        array.invalidate()
        array = model.getBattleTypes()
        battleTypes = self.__battleTypes.split(',')
        for battleType in battleTypes:
            array.addNumber(int(battleType))

        array.invalidate()
