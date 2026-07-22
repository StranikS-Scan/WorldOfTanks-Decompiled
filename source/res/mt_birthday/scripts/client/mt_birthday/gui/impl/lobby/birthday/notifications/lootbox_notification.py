# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/notifications/lootbox_notification.py
from gui.impl.lobby.gf_notifications.notification_base import NotificationBase
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from mt_birthday.gui.impl.gen.view_models.views.lobby.notifications.lootbox_notification_view_model import LootboxNotificationViewModel
from skeletons.gui.game_control import IGuiLootBoxesController

class LootboxNotification(NotificationBase):
    __slots__ = ()
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, resId, *args, **kwargs):
        model = LootboxNotificationViewModel()
        super(LootboxNotification, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return super(LootboxNotification, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LootboxNotification, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setIsPopUp(self._isPopUp)
            model.setIsSmallContainer(False)
            self._updateCount(model=model)

    def _getEvents(self):
        return ((self.viewModel.goToContainers, self.__goToContainers),)

    @replaceNoneKwargsModel
    def _updateCount(self, model=None):
        model.setCount(self._linkageData.toDict().get('incrCount' if self._isPopUp else 'count', 0))

    def __goToContainers(self):
        if self._canNavigate():
            from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
            if self.__guiLootBoxes.isLootBoxesAvailable():
                showStorageView(initialLootBoxId=self._linkageData.toDict().get('lootboxID', 0))


class GiftLootboxNotification(LootboxNotification):

    def _onLoading(self, *args, **kwargs):
        super(GiftLootboxNotification, self)._onLoading(*args, **kwargs)
        self.viewModel.setIsSmallContainer(True)
