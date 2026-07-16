# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/challenges/notifications/challenges_start_notification.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.challenges.notifications.challenges_start_model import ChallengesStartModel
from gui.impl.lobby.gf_notifications import NotificationBase
from gui.server_events.events_dispatcher import showChallenges

class ChallengesStartNotification(NotificationBase):

    def __init__(self, resId, *args, **kwargs):
        super(ChallengesStartNotification, self).__init__(resId, ChallengesStartModel(), *args, **kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(ChallengesStartNotification, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),)

    def _update(self):
        data = self._getPayload()
        with self.viewModel as tx:
            tx.setIsPopUp(self._isPopUp)
            tx.setFirst(data.get('first', False))

    def __onClick(self):
        showChallenges()
