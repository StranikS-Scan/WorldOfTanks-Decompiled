# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/comp7_skill_tooltip.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.comp7_skill_tooltip_model import Comp7SkillTooltipModel
from gui.impl.lobby.comp7.comp7_model_helpers import fillEquipmentStats
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7SkillTooltip(ViewImpl):
    __slots__ = ('__intCD',)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, intCD):
        settings = ViewSettings(R.views.lobby.comp7.tooltips.Comp7SkillTooltip())
        settings.model = Comp7SkillTooltipModel()
        super(Comp7SkillTooltip, self).__init__(settings)
        self.__intCD = intCD

    @property
    def viewModel(self):
        return super(Comp7SkillTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(Comp7SkillTooltip, self)._onLoading(*args, **kwargs)
        self.__setViewData()

    @replaceNoneKwargsModel
    def __setViewData(self, model=None):
        vehicle = g_currentVehicle.item
        equipments = self.__comp7Controller.getVehicleEquipments(vehicle)
        config = equipments[self.__intCD]
        equipment = config['item']
        model.setName(equipment.name)
        model.setIntCD(self.__intCD)
        model.setStartLevel(config['startLevel'])
        fillEquipmentStats(model.skillsStats, equipment)
