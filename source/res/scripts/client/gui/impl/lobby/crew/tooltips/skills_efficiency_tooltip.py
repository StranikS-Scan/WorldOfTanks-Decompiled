# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/skills_efficiency_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.skills_efficiency_tooltip_model import SkillsEfficiencyTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from items.tankmen import MAX_SKILLS_EFFICIENCY_XP
from skeletons.gui.shared import IItemsCache

class SkillsEfficiencyTooltip(ViewImpl):
    __slots__ = ('tankmanID', 'skillEfficiency', 'isShowDiscount')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanID, skillEfficiency=0, isShowDiscount=False, *args, **kwargs):
        self.tankmanID = tankmanID
        self.isShowDiscount = isShowDiscount
        self.skillEfficiency = skillEfficiency
        settings = ViewSettings(R.views.lobby.crew.tooltips.SkillsEfficiencyTooltip(), args=args, kwargs=kwargs)
        settings.model = SkillsEfficiencyTooltipModel()
        super(SkillsEfficiencyTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SkillsEfficiencyTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(SkillsEfficiencyTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        tankman = self.itemsCache.items.getTankman(self.tankmanID)
        with self.viewModel.transaction() as vm:
            if tankman and tankman.currentVehicleSkillsEfficiency >= self.skillEfficiency:
                vm.setPercent(tankman.currentVehicleSkillsEfficiency)
                vm.setCurrentXP(tankman.skillsEfficiencyXP)
            else:
                vm.setPercent(self.skillEfficiency)
                vm.setCurrentXP(MAX_SKILLS_EFFICIENCY_XP * self.skillEfficiency)
            vm.setMaxXP(MAX_SKILLS_EFFICIENCY_XP)
            vm.setIsDiscountInformationVisible(self.isShowDiscount and not tankman.descriptor.getFullSkillsCount(withFree=False))
