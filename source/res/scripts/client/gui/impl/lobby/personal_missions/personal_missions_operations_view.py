# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_operations_view.py
import typing
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from frameworks.wulf import ViewFlags, ViewSettings, Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_operations_view_model import PersonalMissionsOperationsViewModel
from gui.impl.lobby.personal_missions.tooltips.personal_missions_operations_tooltip import PersonalMissionsOperationsTooltip
from gui.impl.lobby.personal_missions.tooltips.personal_missions_last_operation_tooltip import PersonalMissionsLastOperationTooltip
from gui.impl.pub import ViewImpl
from gui.selectable_reward.common import PersonalMissionsSelectableRewardManager
from gui.server_events.event_items import PMOperation
from gui.shared.event_dispatcher import showHangar
from gui.shared.gui_items import Vehicle
from personal_missions import PM_BRANCH
from personal_missions_constants import PM3_FINAL_REWARD_VIEW_ID
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IPersonalMissionsController
from helpers import dependency
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PersonalMissions
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_operations_view_model import RewardsStatus
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_operation_model import Pm3OperationModel, MissionStatus
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from helpers import int2roman, i18n
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_operation_model import LastMissionStatus
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_main_quests_view_model import PageViewIdEnum
from gui.impl.lobby.personal_missions.personal_missions_window_events import showPersonalMissionsOperationWindow, showPersonalMissionsWebbrg, PM3_INFO_PAGE, showPersonalMissionsRewardsSelectionWindow, SERVER_SETTINGS_KEYS, showPersonalMissionsVehicleView
from gui.server_events.pm3_constants import SOUNDS
if typing.TYPE_CHECKING:
    import Event

class PersonalMissionsOperationsView(ViewImpl):
    __slots__ = ()
    __pm3Controller = dependency.descriptor(IPersonalMissionsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __selectableRewardManager = PersonalMissionsSelectableRewardManager
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, layoutID=R.views.lobby.personal_missions.PersonalMissionsOperationsView()):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsOperationsViewModel()
        super(PersonalMissionsOperationsView, self).__init__(settings)

    @staticmethod
    def getOperationStatus(operation):
        isOnPaused = operation.isDisabled()
        if not operation.isUnlocked():
            if isOnPaused:
                return MissionStatus.DISABLEDPAUSED
            return MissionStatus.DISABLED
        if operation.isCompleted():
            if operation.isFullCompleted():
                return MissionStatus.COMPLETEDPERFECTLY
            if isOnPaused:
                return MissionStatus.COMPLETEDPAUSED
            return MissionStatus.COMPLETED
        if operation.isInProgress():
            if not operation.isAvailable().isValid:
                return MissionStatus.ACTIVEPAUSED
            return MissionStatus.ACTIVE
        if not operation.hasRequiredVehicles():
            return MissionStatus.AVAILABLEPAUSED
        return MissionStatus.AVAILABLEPAUSED if isOnPaused else MissionStatus.AVAILABLE

    def getRewardsStatus(self):
        isSelectableRewardAvailable = bool(self.__selectableRewardManager.getAvailableSelectableBonuses())
        return RewardsStatus.AVAILABLE if isSelectableRewardAvailable else RewardsStatus.HIDDEN

    @staticmethod
    def getIsHasLevels(operation):
        return True if operation.isDisabled() or not operation.isUnlocked() or operation.isFullCompleted() else operation.hasRequiredVehicles()

    @property
    def viewModel(self):
        return super(PersonalMissionsOperationsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.personal_missions.tooltips.PersonalMissionsOperationsTooltip():
            return PersonalMissionsOperationsTooltip(contentID, event.getArgument('operationId'))
        return PersonalMissionsLastOperationTooltip(contentID, event.getArgument('operationId')) if contentID == R.views.lobby.personal_missions.tooltips.PersonalMissionsLastOperationTooltip() else None

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsOperationsView, self)._onLoading(*args, **kwargs)
        serverSettings = self.__settingsCore.serverSettings
        if not serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.PM_NEW_CAMPAIGN_HINT):
            serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.PM_NEW_CAMPAIGN_HINT: True})
        self.__updateModel()

    def _getEvents(self):
        return ((self.__pm3Controller.onQuestsUpdated, self.__updateModel),
         (self.__pm3Controller.onItemCacheUpdated, self.__updateRewardsStatusModel),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onOpenOperation, self.__onOpenOperation),
         (self.viewModel.onTakeRewards, self.__onTakeRewards),
         (self.viewModel.onInfo, self.__onInfo),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onSettingsChange))

    def __onSettingsChange(self, diff):
        if not any((key in SERVER_SETTINGS_KEYS for key in diff.iterkeys())):
            return
        if not self.__lobbyContext.getServerSettings().isPersonalMissionsEnabled(PM_BRANCH.PERSONAL_MISSION_3):
            showHangar()
            return
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            model.setRewardsStatus(self.getRewardsStatus())
            operationsModels = model.getOperations()
            operationsModels.clear()
            operations = self.__pm3Controller.getOperations()
            for _, operation in operations.iteritems():
                self.__addOperationData(operationsModels, operation)

            operationsModels.invalidate()
            self.__updateLastOperation(model.lastOperation)

    def __addOperationData(self, model, operation):
        operationModel = Pm3OperationModel()
        operationModel.setName(operation.getShortUserName())
        operationId = operation.getID()
        operationModel.setOperationId(operationId)
        operationModel.setIsHasLevels(self.getIsHasLevels(operation))
        operationModel.setTotalQuests(operation.getQuestsCount())
        currentCompletedQuests = len(operation.getCompletedQuests())
        prevCompletedQuests = self.__getPrevCompletedQuests(operationId)
        self.__saveCompletedQuests(operationId, currentCompletedQuests)
        operationModel.setCompletedQuests(currentCompletedQuests)
        operationModel.setDelta(prevCompletedQuests)
        operationModel.setStatus(self.getOperationStatus(operation))
        operationModel.setPrevOperationName(self.__pm3Controller.getPreviousOperationName(operationId))
        self.__updateVehicleBonus(operationModel, operation.getVehicleBonus())
        model.addViewModel(operationModel)

    @staticmethod
    def __updateVehicleBonus(operationModel, vehicle):
        if vehicle is None:
            return
        else:
            operationModel.setVehicleName(vehicle.userName)
            operationModel.setLevel(int2roman(vehicle.level))
            operationModel.setIsElite(vehicle.isElite)
            operationModel.setTypeIcon(vehicle.type)
            return

    def __getLastOperationStatus(self):
        operations = self.__eventsCache.getPersonalMissions().getOperationsForBranch(PM_BRANCH.PERSONAL_MISSION_3)
        operationsValues = operations.itervalues()
        allDisabled = True
        allFullCompleted = True
        allCompleted = True
        for op in operationsValues:
            if not op.isDisabled():
                allDisabled = False
            if not op.isFullCompleted():
                allFullCompleted = False
            if not op.isCompleted():
                allCompleted = False

        if allDisabled:
            return LastMissionStatus.DISABLED
        if allFullCompleted:
            return LastMissionStatus.COMPLETED
        return LastMissionStatus.ACTIVE if allCompleted else LastMissionStatus.DISABLED

    def __updateLastOperation(self, model):
        vehicle = first(self.__pm3Controller.getVehiclesForChampionQuestPM3())
        model.setName(i18n.makeString('#personal_missions:operations/title%d' % PM3_FINAL_REWARD_VIEW_ID))
        model.setStatus(self.__getLastOperationStatus())
        model.setOperationId(PM3_FINAL_REWARD_VIEW_ID)
        model.setLevel(int2roman(vehicle.level))
        model.setVehicleName(vehicle.userName)
        model.setTypeIcon(vehicle.type)
        model.setTotalQuests(len(self.__pm3Controller.getFinalQuests()))
        currentCompletedQuests = len(self.__pm3Controller.getFullCompletedFinalQuests())
        model.setCompletedQuests(currentCompletedQuests)
        prevCompletedQuests = self.__getPrevCompletedQuests(PM3_FINAL_REWARD_VIEW_ID)
        model.setDelta(prevCompletedQuests)
        self.__saveCompletedQuests(PM3_FINAL_REWARD_VIEW_ID, currentCompletedQuests)

    def __updateRewardsStatusModel(self):
        with self.viewModel.transaction() as model:
            model.setRewardsStatus(self.getRewardsStatus())

    def __saveCompletedQuests(self, operationId, completedQuestsCount):
        settings = AccountSettings.getPersonalMissions(PersonalMissions.PREV_COMPLETED_QUESTS)
        settings[operationId] = completedQuestsCount
        AccountSettings.setPersonalMissions(PersonalMissions.PREV_COMPLETED_QUESTS, settings)

    def __getPrevCompletedQuests(self, operationId):
        settings = AccountSettings.getPersonalMissions(PersonalMissions.PREV_COMPLETED_QUESTS)
        return settings.get(operationId, 0)

    def __onClose(self):
        self.destroyWindow()
        showHangar()

    def __onOpenOperation(self, args):
        operationId = int(args.get('operationId', '8'))
        if operationId == PM3_FINAL_REWARD_VIEW_ID:
            showPersonalMissionsVehicleView(operationId)
        else:
            showPersonalMissionsOperationWindow(PageViewIdEnum.QUESTS, operationId)

    def __onTakeRewards(self):
        showPersonalMissionsRewardsSelectionWindow()

    def __onInfo(self):
        self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_ON)
        showPersonalMissionsWebbrg(PM3_INFO_PAGE, parent=self.getParentWindow(), returnClb=self.__onInfoClose)

    def __onInfoClose(self, **kwargs):
        self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_OFF)
