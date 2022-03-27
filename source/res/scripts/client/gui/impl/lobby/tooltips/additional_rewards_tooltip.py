# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/additional_rewards_tooltip.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.additional_rewards_tooltip_model import AdditionalRewardsTooltipModel
from gui.impl.pub import ViewImpl
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from gui.shared.missions.packers.bonus import BonusUIPacker

class AdditionalRewardsTooltip(ViewImpl):
    __slots__ = ('__bonuses', '__bonusPackers')

    def __init__(self, bonuses, bonusPacker=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.tooltips.AdditionalRewardsTooltip())
        settings.model = AdditionalRewardsTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AdditionalRewardsTooltip, self).__init__(settings)
        self.__bonuses = bonuses
        from gui.impl.lobby.awards.packers import getAdditionalAwardsBonusPacker
        self.__bonusPackers = bonusPacker or getAdditionalAwardsBonusPacker()

    @property
    def viewModel(self):
        return super(AdditionalRewardsTooltip, self).getViewModel()

    def _onLoading(self, headerTextR=R.strings.tooltips.quests.awards.additional.header(), headerCount=0, descriptionR=R.invalid(), descriptionCount=0, *args, **kwargs):
        super(AdditionalRewardsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setHeaderText(headerTextR)
            model.setHeaderCount(headerCount)
            model.setDescription(descriptionR)
            model.setDescriptionCount(descriptionCount)
            bonusArray = model.getBonus()
            for bonus in self.__bonuses:
                if bonus.isShowInGUI():
                    bonusList = self.__bonusPackers.pack(bonus)
                    for item in bonusList:
                        bonusArray.addViewModel(item)
