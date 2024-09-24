# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/tooltips/commander_bonus_additional_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.tooltips.crew_perks_additional_tooltip_model import CrewPerksAdditionalTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items.Tankman import COMMANDER_BONUS
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from items.components.skills_constants import SkillTypeName
ANIMATION_NAME = 'skillCommanderBonus'
DEF_COMMANDER_BONUS = 10

class CommanderBonusAdditionalTooltip(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_tankman',)

    def __init__(self, tankmanId):
        settings = ViewSettings(R.views.lobby.crew.tooltips.CrewPerksAdditionalTooltip())
        settings.model = CrewPerksAdditionalTooltipModel()
        self._tankman = self._itemsCache.items.getTankman(int(tankmanId)) if tankmanId else None
        super(CommanderBonusAdditionalTooltip, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CommanderBonusAdditionalTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(CommanderBonusAdditionalTooltip, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as vm:
            vm.setIconName(COMMANDER_BONUS)
            vm.setUserName(backport.text(R.strings.tooltips.commanderBonus.name()))
            vm.setSkillType(SkillTypeName.COMMANDER_SPECIAL)
            commanderBonus = int(self._tankman.vehicleBonuses.get('commander', 10) if self._tankman else DEF_COMMANDER_BONUS)
            commBonusDesc = backport.text(R.strings.tooltips.commanderBonus.alt.description(), commBonus=str(commanderBonus))
            vm.setDescription(commBonusDesc)
            vm.setAnimationName(ANIMATION_NAME)
            vm.setInfo(backport.text(R.strings.tooltips.commanderBonus.alt.info()))
