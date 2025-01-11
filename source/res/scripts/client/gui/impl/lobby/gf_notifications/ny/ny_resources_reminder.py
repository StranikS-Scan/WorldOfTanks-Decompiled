# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_resources_reminder.py
from adisp import adisp_process, adisp_async
from frameworks.wulf.gui_constants import ViewStatus
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_resources_reminder_model import NyResourcesReminderModel, reminderType
from gui.impl.new_year.navigation import ViewAliases, NewYearNavigation
from helpers import dependency
from new_year.ny_constants import NYObjects
from ny_notification import NyNotification
from skeletons.new_year import IFriendServiceController
reminderReverseMapper = {reminderType.PERSONAL.value: reminderType.PERSONAL,
 reminderType.FRIENDS.value: reminderType.FRIENDS,
 reminderType.FINDFRIENDS.value: reminderType.FINDFRIENDS}

class NyResourcesReminder(NyNotification):
    __friendsService = dependency.descriptor(IFriendServiceController)
    __slots__ = ('__friendSpaId', '__viewType')

    def __init__(self, resId, *args, **kwargs):
        model = NyResourcesReminderModel()
        super(NyResourcesReminder, self).__init__(resId, model, *args, **kwargs)
        self.__viewType = self.linkageData.viewType

    @property
    def viewModel(self):
        return super(NyResourcesReminder, self).getViewModel()

    def _getEvents(self):
        events = super(NyResourcesReminder, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick),)

    def _canNavigate(self):
        viewType = reminderReverseMapper[self.__viewType]
        return super(NyResourcesReminder, self)._canNavigate() and self.__friendsService.isServiceEnabled and self._nyController.isEnabled() if viewType == reminderType.FRIENDS or viewType == reminderType.FINDFRIENDS else super(NyResourcesReminder, self)._canNavigate() and self._nyController.isEnabled()

    def _update(self):
        with self.viewModel.transaction() as model:
            viewType = reminderReverseMapper[self.linkageData.viewType]
            isValid = True
            if viewType == reminderType.PERSONAL:
                model.setIsExtra(self.linkageData.isExtra)
            elif viewType == reminderType.FRIENDS:
                model.setFriendName(unicode(self.linkageData.friendName))
                isValid = self.linkageData.friendID in self.__friendsService.bestFriendList
            model.setViewType(viewType)
            model.setIsPopUp(self._isPopUp)
            model.setResourcesCount(self.linkageData.resourceCount)
            model.setIsButtonDisabled(not self._canNavigate() or not isValid)

    @adisp_process
    def __onClick(self):
        self.viewModel.setIsButtonDisabled(True)
        viewName = NewYearNavigation.getCurrentViewName()
        viewObj = NewYearNavigation.getCurrentObject()
        if self._canNavigate():
            if self.viewModel.getViewType() == reminderType.FINDFRIENDS:
                if viewName != ViewAliases.FRIENDS_VIEW:
                    self._navigateToNy(None, ViewAliases.FRIENDS_VIEW)
            else:
                if self.__friendsService.isInFriendHangar:
                    self.__friendsService.leaveFriendHangar()
                if self.viewModel.getViewType() == reminderType.PERSONAL:
                    if viewObj != NYObjects.RESOURCES or viewName != ViewAliases.GLADE_VIEW:
                        self._navigateToNy(NYObjects.RESOURCES, ViewAliases.GLADE_VIEW)
                else:
                    self.__friendSpaId = self.linkageData.friendID
                    isSuccess = yield self.__friendsService.updateFriendList()
                    if isSuccess and self.__friendSpaId in self.__friendsService.bestFriendList:
                        if not (self.__friendsService.isInFriendHangar and self.__friendsService.friendHangarSpaId == self.__friendSpaId and viewObj == NYObjects.RESOURCES and viewName == ViewAliases.FRIEND_GLADE_VIEW):
                            self._navigateToNy(NYObjects.RESOURCES, ViewAliases.FRIEND_GLADE_VIEW, executeBeforeSwitch=self.__enterFriendHangar)
                    elif self.viewStatus == ViewStatus.LOADED:
                        self.viewModel.setIsButtonDisabled(True)
                        return
            if self.viewStatus == ViewStatus.LOADED:
                self.viewModel.setIsButtonDisabled(False)
        return

    @adisp_async
    @adisp_process
    def __enterFriendHangar(self, callback):
        result = yield self.__friendsService.enterFriendHangar(self.__friendSpaId)
        callback(result)
