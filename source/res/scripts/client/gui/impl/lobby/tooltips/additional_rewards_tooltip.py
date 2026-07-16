# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/additional_rewards_tooltip.py
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.tooltips.additional_rewards_tooltip_model import AdditionalRewardsTooltipModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES

class AdditionalRewardsTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.tooltips.AdditionalRewardsTooltip())
        settings.model = AdditionalRewardsTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AdditionalRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdditionalRewardsTooltip, self).getViewModel()

    def _onLoading(self, packedBonuses, *args, **kwargs):
        super(AdditionalRewardsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setHeaderText(self._getHeader())
            model.setHeaderCount(self._getHeaderCount())
            model.setDescription(R.invalid())
            model.setDescriptionCount(0)
            self._fillBonusesArray(packedBonuses, model.getBonus())

    @classmethod
    def _getHeader(cls):
        return R.strings.tooltips.quests.awards.additional.header()

    @classmethod
    def _getHeaderCount(cls):
        pass

    @staticmethod
    def _fillBonusesArray(bonusModels, array):
        attachmentCount = 0
        attachmentModel = None
        array.clear()
        for bonusModel in bonusModels:
            if hasattr(bonusModel, 'getIcon') and bonusModel.getIcon() == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ATTACHMENT]:
                if attachmentModel is None:
                    attachmentModel = IconBonusModel()
                    attachmentModel.setIcon(bonusModel.getIcon())
                    attachmentModel.setName(bonusModel.getName())
                    array.addViewModel(attachmentModel)
                attachmentCount += int(bonusModel.getValue())
            array.addViewModel(bonusModel)

        if attachmentModel is not None:
            attachmentModel.setValue(str(attachmentCount))
        array.invalidate()
        return


class AdditionalBattlePassRewardsTooltip(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.tooltips.AdditionalBattlePassRewardsTooltip())
        settings.model = AdditionalRewardsTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AdditionalBattlePassRewardsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AdditionalBattlePassRewardsTooltip, self).getViewModel()

    def _onLoading(self, packedBonuses, *args, **kwargs):
        super(AdditionalBattlePassRewardsTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillViewModelsArray(packedBonuses, model.getBonus())
