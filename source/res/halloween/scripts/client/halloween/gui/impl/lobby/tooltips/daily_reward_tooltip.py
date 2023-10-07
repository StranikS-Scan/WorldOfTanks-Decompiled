# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/tooltips/daily_reward_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IHalloweenController
from helpers import dependency
from halloween.hw_constants import PhaseType
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.daily_reward_tooltip_model import DailyRewardTooltipModel
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.halloween_tooltip_ability_item import HalloweenTooltipAbilityItem

class DailyRewardTooltip(ViewImpl):
    _hwController = dependency.descriptor(IHalloweenController)
    __slots__ = ('__isBonusQuestCard',)

    def __init__(self, isBonusQuestCard):
        settings = ViewSettings(R.views.halloween.lobby.tooltips.DailyRewardTooltip())
        settings.model = DailyRewardTooltipModel()
        self.__isBonusQuestCard = isBonusQuestCard
        super(DailyRewardTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(DailyRewardTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DailyRewardTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    def __updateModel(self, model):
        phase = self._hwController.phases.getActivePhase(PhaseType.REGULAR)
        data = phase.getAllAbilitiesInfo(dailyQuest=not self.__isBonusQuestCard)
        if not data:
            return
        abilities, _ = data
        abilitiesView = model.getAbilities()
        abilitiesView.clear()
        for equipment, _ in abilities.iteritems():
            abilityStrRes = R.strings.artefacts.dyn(equipment.descriptor.name)
            abilityImgRes = R.images.gui.maps.icons.artefact.dyn(equipment.descriptor.iconName)
            if abilityImgRes.exists():
                ability = HalloweenTooltipAbilityItem()
                ability.setAbilityName(abilityStrRes.name())
                ability.setAbilityIcon(abilityImgRes())
                abilitiesView.addViewModel(ability)

        abilitiesView.invalidate()
