# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/play_streak_rewards.py
from notification_base import NotificationBase
from gui.impl.gen.view_models.views.lobby.notifications.notification_model import NotificationModel

class PlayStreakRewards(NotificationBase):
    __slots__ = ()

    def __init__(self, resId, *args, **kwargs):
        model = NotificationModel()
        super(PlayStreakRewards, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return super(PlayStreakRewards, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PlayStreakRewards, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setIsPopUp(self._isPopUp)
