# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/tooltips/seniority_awards_compensation_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.seniority_awards.tooltips import seniority_awards_compensation_tooltip_model
from gui.impl.lobby.awards.packers import getAdditionalAwardsBonusPacker
from gui.impl.pub import ViewImpl

class SeniorityAwardsCompensationTooltip(ViewImpl):
    __slots__ = ('__bonusBefore', '__bonusAfter')

    def __init__(self, itemBefore, itemAfter):
        settings = ViewSettings(R.views.lobby.seniority_awards.tooltips.SeniorityAwardsCompensationTooltip())
        settings.model = seniority_awards_compensation_tooltip_model.SeniorityAwardsCompensationTooltipModel()
        self.__bonusBefore = [itemBefore]
        self.__bonusAfter = [itemAfter]
        super(SeniorityAwardsCompensationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SeniorityAwardsCompensationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            self.__fillItem(tx.getItemBefore(), self.__bonusBefore)
            self.__fillItem(tx.getItemAfter(), self.__bonusAfter)

    @classmethod
    def __fillItem(cls, bonusModelsList, bonuses):
        cls.__packBonus(bonusModelsList, bonuses)
        bonusModelsList.invalidate()

    @classmethod
    def __packBonus(cls, bonusModelsList, bonuses):
        packer = getAdditionalAwardsBonusPacker()
        for bonus in bonuses:
            bonusList = packer.pack(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusModelsList.addViewModel(item)
