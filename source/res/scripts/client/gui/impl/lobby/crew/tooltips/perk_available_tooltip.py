# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/perk_available_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.perk_available_tooltip_model import PerkAvailableTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class PerkAvailableTooltip(ViewImpl):
    __slots__ = ('__tankmanID',)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, tankmanID):
        settings = ViewSettings(R.views.lobby.crew.tooltips.PerkAvailableTooltip())
        settings.model = PerkAvailableTooltipModel()
        self.__tankmanID = tankmanID
        super(PerkAvailableTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PerkAvailableTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PerkAvailableTooltip, self)._onLoading()
        tankman = self._itemsCache.items.getTankman(self.__tankmanID)
        newSkillsCount, lastNewSkillLvl = tankman.newSkillsCount
        availableSkills = len(tankman.availableSkills(useCombinedRoles=True))
        with self.viewModel.transaction() as vm:
            if availableSkills < newSkillsCount:
                newSkillsCount = availableSkills
                lastNewSkillLvl = 0
                vm.setIsAllSlotsTrained(True)
            vm.setPerkCount(newSkillsCount - tankman.newFreeSkillsCount)
            vm.setLastPerkLevel(lastNewSkillLvl)
            vm.setZeroPerkCount(tankman.newFreeSkillsCount)
