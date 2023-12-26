# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_dog_mission_completed.py
from helpers import dependency
from ny_notification import NyNotification
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_dog_mission_completed_model import NyDogMissionCompletedModel
from gui.impl.new_year.navigation import ViewAliases
from new_year.ny_constants import NYObjects
from skeletons.new_year import IFriendServiceController

class NyDogMissionCompleted(NyNotification):
    __friendController = dependency.descriptor(IFriendServiceController)
    __slots__ = ()

    def __init__(self, resId, *args, **kwargs):
        model = NyDogMissionCompletedModel()
        super(NyDogMissionCompleted, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return super(NyDogMissionCompleted, self).getViewModel()

    def _getEvents(self):
        events = super(NyDogMissionCompleted, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),)

    def _canNavigate(self):
        return super(NyDogMissionCompleted, self)._canNavigate() and self._nyController.isEnabled()

    def _update(self):
        with self.viewModel.transaction() as model:
            model.setIsPopUp(self._isPopUp)
            model.setMissionsCompleted(self.linkageData.missionsCompleted)
            model.setMissionsTotal(self.linkageData.missionsTotal)
            model.setBundleLevel(self.linkageData.dogLevel)
            model.setIsButtonDisabled(not self._canNavigate())

    def __onClick(self):
        if self._canNavigate():
            if self.__friendController.isInFriendHangar:
                self.__friendController.leaveFriendHangar()
            self._navigateToNy(NYObjects.CELEBRITY_D, ViewAliases.CELEBRITY_VIEW)
