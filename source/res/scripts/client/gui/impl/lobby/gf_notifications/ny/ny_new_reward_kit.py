# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_new_reward_kit.py
from ny_notification import NyNotification
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_new_reward_kit_model import NyNewRewardKitModel
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from new_year.ny_navigation_helper import showLootBox
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class NyNewRewardKit(NyNotification):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, resId, *args, **kwargs):
        model = NyNewRewardKitModel()
        super(NyNewRewardKit, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return super(NyNewRewardKit, self).getViewModel()

    def _getEvents(self):
        events = super(NyNewRewardKit, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),)

    def _update(self):
        with self.viewModel.transaction() as model:
            model.setIsButtonDisabled(not self._canNavigate())
            model.setIsPopUp(self._isPopUp)
            model.setKitsCount(self.linkageData.count)
            model.setCategory(self.linkageData.category)

    def _canNavigate(self):
        return super(NyNewRewardKit, self)._canNavigate() and self.__lobbyContext.getServerSettings().isLootBoxesEnabled() and self._nyController.isEnabled()

    def __onClick(self):
        if self._canNavigate():
            showLootBox(lootBoxType=NewYearLootBoxes.PREMIUM, category=self.linkageData.category)
