# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/personal_missions.py
import logging
from collections import OrderedDict
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.server_events import IEventsCache
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.personal_missions_model import PersonalMissionsModel, State
from gui.impl.gen import R
from gui.server_events.event_items import PMOperation
_logger = logging.getLogger(__name__)

class PersonalMissionsPresenter(ViewComponent[PersonalMissionsModel]):
    LAYOUT_ID = R.aliases.user_missions.hub.basicMissions.PersonalMissions()
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.personalMissionsCache = self.eventsCache.getPersonalMissions()
        self.currentOperation = None
        super(PersonalMissionsPresenter, self).__init__(model=PersonalMissionsModel)
        return

    @property
    def viewModel(self):
        return super(PersonalMissionsPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        _logger.info('PersonalMissions:_onLoading')
        super(PersonalMissionsPresenter, self)._onLoading()
        self.__fillModel()

    def _getEvents(self):
        return ((self.eventsCache.onSyncCompleted, self.__onCacheSyncCompleted),)

    def __onCacheSyncCompleted(self):
        self.__fillModel()

    def __fillModel(self):
        operations = OrderedDict(sorted(self.personalMissionsCache.getOperationsForBranch('pm3').items()))
        previousDetailProgress, previousMissionsProgress = self.__getProgress(self.currentOperation)
        self.currentOperation = self.__getInProgressOperation(operations)
        currentDetailProgress, currentMissionsProgress = self.__getProgress(self.currentOperation)
        nextOperation = self.__getNextOperation(operations)
        areAllOperationsCompleted = all((op.isCompleted() for op in operations.values()))
        with self.viewModel.transaction() as tx:
            if self.__isFirstActivation(operations):
                tx.setState(State.CAMPAIGN_3_NOT_ACTIVATED)
                tx.setCampaignName(self.__getCampaignName())
            elif self.__isBaseProgress(operations):
                tx.setState(State.IN_PROGRESS)
                tx.setCurrentOperationName(self.currentOperation.getUserName())
                tx.setCurrentOperationId(self.currentOperation.getID())
                tx.setStageNumber(1)
                tx.setDetailId(1)
                tx.setPreviousProgress(previousDetailProgress)
                tx.setCurrentProgress(currentDetailProgress)
                tx.setTotalProgress(15)
                tx.setVehicleName('++MegaTank++')
            elif self.__isProgressForHonors(operations):
                tx.setState(State.IN_PROGRESS_FOR_HONORS)
                tx.setCurrentOperationName(self.currentOperation.getUserName())
                tx.setCurrentOperationId(self.currentOperation.getID())
                tx.setPreviousProgress(previousMissionsProgress)
                tx.setCurrentProgress(currentMissionsProgress)
                tx.setTotalProgress(self.currentOperation.getQuestCount())
            elif nextOperation is not None and self.__IsCompleted(operations):
                tx.setState(State.COMPLETED)
                tx.setCurrentOperationName(self.currentOperation.getUserName())
                tx.setCurrentOperationId(self.currentOperation.getID())
                tx.setNextOperationName(nextOperation.getUserName())
                tx.setNextOperationId(nextOperation.getID())
                tx.setAllOperationsCompleted(areAllOperationsCompleted)
            elif nextOperation is not None and self.__isFullCompleted(operations):
                tx.setState(State.COMPLETED_WITH_HONORS)
                tx.setCurrentOperationName(self.currentOperation.getUserName())
                tx.setCurrentOperationId(self.currentOperation.getID())
                tx.setNextOperationName(nextOperation.getUserName())
                tx.setNextOperationId(nextOperation.getID())
                tx.setAllOperationsCompleted(areAllOperationsCompleted)
        return

    def __isFirstActivation(self, operations):
        firstOperation = operations.get(8, None)
        if firstOperation is None:
            return False
        else:
            isFirstOperationAvailable, _ = firstOperation.isAvailable()
            isFirstActivation = self.currentOperation is None and isFirstOperationAvailable and not firstOperation.isInProgress()
            return isFirstActivation

    def __getInProgressOperation(self, operations):
        return findFirst(lambda op: op.isInProgress(), operations.values()) if operations else None

    def __isBaseProgress(self, operations):
        operationInProgress = self.__getInProgressOperation(operations)
        return operationInProgress is not None and not operationInProgress.IsCompleted()

    def __isProgressForHonors(self, operations):
        operationInProgress = self.__getInProgressOperation(operations)
        return operationInProgress is not None and not operationInProgress.IsFullCompleted() and operationInProgress.IsCompleted()

    def __isCompleted(self, operations):
        return self.currentOperation is not None and not self.currentOperation.isFullCompleted() and self.currentOperation.isCompleted() and self.__getInProgressOperation(operations) is None

    def __isFullCompleted(self, operations):
        return self.currentOperation is not None and self.currentOperation.isFullCompleted() and self.__getInProgressOperation(operations) is None

    def __getCampaignName(self):
        campaigns = self.personalMissionsCache.getCampaignsForBranch('pm3')
        return '' if campaigns is None else campaigns.values()[0].getUserName()

    def __getProgress(self, operation):
        detailProgress = 0
        missionsProgress = 0
        if self.currentOperation is not None:
            detailProgress = 1
            missionsProgress = len(self.currentOperation.getCompletedQuests())
        return (detailProgress, missionsProgress)

    def __getNextOperation(self, operations):
        return operations.get(9, None)
