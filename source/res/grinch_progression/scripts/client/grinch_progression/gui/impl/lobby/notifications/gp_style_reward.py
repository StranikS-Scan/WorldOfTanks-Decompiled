# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/notifications/gp_style_reward.py
from grinch_progression.gui.impl.gen.view_models.views.lobby.notifications.gp_style_reward_model import GpStyleRewardModel
from gui.impl.lobby.gf_notifications.ny.award_notification_base import AwardNotificationBase, bonusesSortOrder, splitHugeBonuses, customSplitBonuses, fromRawBonusWithListsToBonuses
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class GpStyleReward(AwardNotificationBase):
    __itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, resId, *args, **kwargs):
        model = GpStyleRewardModel()
        super(GpStyleReward, self).__init__(resId, model, *args, **kwargs)
        self.__rewards = []

    @property
    def viewModel(self):
        return super(GpStyleReward, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        data = self.linkageData.toDict()
        self.__rewards = fromRawBonusWithListsToBonuses(data.get('bonuses', []))
        super(GpStyleReward, self)._onLoading(self)

    def _update(self):
        self.__setRewards()

    def _getEvents(self):
        return super(GpStyleReward, self)._getEvents() + ((self.viewModel.onStylePreview, self.__onStylePreview),)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(GpStyleReward, self).createToolTip(event)

    def __setRewards(self):
        bonuses = customSplitBonuses(self.__rewards)
        hugeBonuses, _ = splitHugeBonuses(bonuses)
        with self.getViewModel().transaction() as model:
            self._tooltips.clear()
            self._fillRewardsList(rewardsList=model.hugeRewards.getItems(), bonuses=hugeBonuses, sortMethod=bonusesSortOrder, packer=getChallengeBonusPacker())
            model.setIsPopUp(self._isPopUp)
            model.setIsButtonDisabled(not self._canNavigate())

    def __onStylePreview(self, intCD):
        styleItem = self.__itemsCache.items.getItemByCD(int(intCD.get('intCD')))
        if styleItem is None:
            return
        else:
            self._showStylePreview(styleItem)
            return
