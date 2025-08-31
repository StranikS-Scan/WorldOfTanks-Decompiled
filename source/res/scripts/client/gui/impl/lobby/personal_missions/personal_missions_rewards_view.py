# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_rewards_view.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PersonalMissions
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_rewards_view_model import PersonalMissionsRewardsViewModel, CompletedQuestsType, LineType
from gui.impl.lobby.personal_missions.tooltips.rest_rewards_tooltip_view import RestRewardsTooltipView
from gui.impl.pub import ViewImpl
from gui.selectable_reward.common import PersonalMissionsSelectableRewardManager
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IPersonalMissionsController
from gui.impl.backport.backport_tooltip import _BackportTooltipContent
from gui.impl.lobby.personal_missions.personal_missions_quest_model import QuestModelParser
from gui.impl.lobby.personal_missions.personal_missions_window_events import showQuestViewById
from gui.impl.lobby.personal_missions.personal_missions_window_events import showPersonalMissionsRewardsView
from gui.shared.utils.functions import makeTooltip
from gui.impl.backport import createTooltipData
from frameworks.wulf import WindowLayer
from gui.impl.pub.lobby_window import LobbyNotificationWindow
import personal_mission_bonuses_packers as BonusPacker
from skeletons.gui.shared import IItemsCache
from gui.server_events.pm3_constants import VoiceOvers, SOUNDS
from gui.impl.lobby.personal_missions.personal_mission_bonuses_packers import packBonusModelAndTooltipData
from gui.shared.events import PersonalMissionsEvent
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
_logger = logging.getLogger(__name__)
LineTypeIndexes = {0: LineType.HIT,
 1: LineType.KILLS,
 2: LineType.ASSIST,
 3: LineType.BATTLE,
 4: LineType.MASTER}

class PersonalMissionsRewardsView(ViewImpl):
    __slots__ = ('__questId', '__tooltipData', '__questUserShortName', '__questUserDescr', '__selectedBonuses', '__viewType', '__countSelectableBonuses', '__operationID')
    __personalMissionsController = dependency.descriptor(IPersonalMissionsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __selectableRewardManager = PersonalMissionsSelectableRewardManager
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID, questId, selectedBonuses=None, viewType=CompletedQuestsType.COMPLETE, operationID=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsRewardsViewModel()
        super(PersonalMissionsRewardsView, self).__init__(settings)
        self.__questId = questId
        self.__viewType = viewType
        self.__tooltipData = {}
        self.__questUserShortName = ''
        self.__selectedBonuses = selectedBonuses
        self.__countSelectableBonuses = None
        self.__operationID = operationID
        return

    @property
    def viewModel(self):
        return super(PersonalMissionsRewardsView, self).getViewModel()

    def closeView(self):
        if self.soundManager.isSoundPlaying(VoiceOvers.REWARD_SCREEN_VO):
            self.soundManager.playSound(VoiceOvers.STOP_REWARD_VO)
        self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_OFF)
        self.destroyWindow()
        g_eventBus.handleEvent(PersonalMissionsEvent(PersonalMissionsEvent.ON_AWARD_PM_SCREEN_CLOSE, ctx={'questID': self.__questId,
         'selectedRewards': self.__selectedBonuses,
         'operationID': self.__operationID}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsRewardsView, self)._onLoading(*args, **kwargs)
        self.__updateData()

    def __updateData(self, *_):
        with self.viewModel.transaction() as vm:
            if self.__selectedBonuses:
                self.__processSelectedBonuses(vm)
            elif self.__operationID is not None:
                self.processOperationData(vm)
            else:
                self.__processQuestData(vm)
        return

    def __processSelectedBonuses(self, vm):
        import gui.server_events.bonuses as serverBonuses
        rewardsModel = vm.getRewards()
        rewardsModel.clear()
        vm.setIsSelectedRewards(True)
        itemsBonus = serverBonuses.ItemsBonus(name='items', value=self.__selectedBonuses['items'])
        BonusPacker.packBonusModelAndTooltipData([itemsBonus], rewardsModel, self.__tooltipData)
        self.soundManager.playSound(SOUNDS.EVENT_REWARD_SCREEN_GENERAL)

    def __processQuestData(self, vm):
        currentCountSelectableBonuses = len(self.__selectableRewardManager.getAvailableSelectableBonuses())
        if self.__countSelectableBonuses is not None and currentCountSelectableBonuses == self.__countSelectableBonuses:
            return
        else:
            self.__countSelectableBonuses = currentCountSelectableBonuses
            self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_ON)
            qID = self.__questId
            parser = QuestModelParser()
            parser.updateQuestModelFromID(questModel=vm.questModel, questID=qID)
            self.__tooltipData = parser.getTooltipData()
            vm.setQuestID(qID)
            ctrl = self.__personalMissionsController
            currentQuest = ctrl.getQuest(qID)
            operationID = currentQuest.getOperationID()
            chainID = currentQuest.getChainID()
            nextQuest = ctrl.getSelectedQuestForChain(chainID, operationID)
            if nextQuest is not None:
                vm.setNextTaskName(nextQuest.getUserName())
                vm.setNextQuestID(nextQuest.getID())
            operationInfo = ctrl.getOperationById(operationID)
            self.__handleQuest(vm, currentQuest)
            self.__questUserShortName = currentQuest.getShortUserName()
            vm.setCurrentTaskName(self.__questUserShortName)
            linesIdsList = ctrl.getLinesIdsByChainAndOperationId(chainID, operationID)
            currentQuestId = currentQuest.getID()
            for index, lineIds in enumerate(linesIdsList):
                if currentQuestId in xrange(lineIds[0], lineIds[1] + 1):
                    vm.setType(LineTypeIndexes.get(index, LineType.HIT))
                    break

            questsChains = ctrl.getQuestsChainsByOperationId(operationID)
            chainQuests = questsChains.get(currentQuest.getChainID(), {}).get('data', [])
            vm.setIsFullChainComplete(all((quest.isFullCompleted() for quest in chainQuests)))
            vm.setOperationName(operationInfo.getShortUserName())
            self.applyDataForGeneralProgress(vm, operationID)
            return

    def applyDataForGeneralProgress(self, vm, operationID):
        ctrl = self.__personalMissionsController
        vm.setMaxValue(len(ctrl.getFinalQuests()))
        currentCompletedQuests = len(ctrl.getFullCompletedFinalQuests())
        vm.setValue(currentCompletedQuests)
        prevCompletedQuests = self.__getPrevCompletedQuests(operationID)
        vm.setDelta(prevCompletedQuests)
        self.__saveCompletedQuests(operationID, currentCompletedQuests)

    def __saveCompletedQuests(self, operationId, completedQuestsCount):
        settings = AccountSettings.getPersonalMissions(PersonalMissions.PREV_COMPLETED_QUESTS)
        settings[operationId] = completedQuestsCount
        AccountSettings.setPersonalMissions(PersonalMissions.PREV_COMPLETED_QUESTS, settings)

    def __getPrevCompletedQuests(self, operationId):
        settings = AccountSettings.getPersonalMissions(PersonalMissions.PREV_COMPLETED_QUESTS)
        return settings.get(operationId, 0)

    def processOperationData(self, vm):
        pm3ctrl = self.__personalMissionsController
        operation = pm3ctrl.getOperationById(self.__operationID)
        if operation is None or not operation.isFullCompleted():
            return
        else:
            self.applyDataForGeneralProgress(vm, self.__operationID)
            packBonusModelAndTooltipData(pm3ctrl.getAddBonusesForOperation(operation), vm.getRewards(), self.__tooltipData)
            vm.setIsOperationAddRewards(True)
            vm.setOperationName(operation.getShortUserName())
            return

    def __handleQuest(self, vm, quest):
        isFinal = quest.isFinal()
        questType = self.__viewType
        self.__applyView(vm, questType)
        self.__applySounds(isFinal, quest)

    def __applyView(self, vm, questType):
        vm.setQuestTypeComplete(questType)

    def __applySounds(self, isFinal, quest):
        rewardSwitch = VoiceOvers.REWARD_SWITCH_HONOR if isFinal and quest.isFullCompleted() else VoiceOvers.REWARD_SWITCH_SIMPLE
        sound = SOUNDS.EVENT_SPECIAL_GREETING if isFinal else SOUNDS.EVENT_REWARD_SCREEN_GENERAL
        self.soundManager.setSwitch(VoiceOvers.REWARD_GROUP, rewardSwitch)
        self.soundManager.playSound(sound)
        if isFinal:
            self.soundManager.playSound(VoiceOvers.REWARD_SCREEN_VO)

    def _getEvents(self):
        return ((self.__itemsCache.onSyncCompleted, self.__updateData),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onOpenQuest, self.__openNextQuestView),
         (self.viewModel.onChooseReward, self.__onChooseRewards))

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            if tooltipData:
                return _BackportTooltipContent(tooltipData)
            questInfo = self.__personalMissionsController.getQuest(self.__questId)
            if questInfo is None:
                return
            questConfig = questInfo.getConditionsConfig()
            idName = event.getArgument('idName', '')
            if idName not in questConfig:
                return
            header, body = QuestModelParser.getDescriptionsForQuest(questInfo.getGeneralQuestID(), questConfig, idName)
            tooltip = makeTooltip(header=header, body=body)
            tooltipData = createTooltipData(tooltip)
            return _BackportTooltipContent(tooltipData)
        elif contentID == R.views.lobby.personal_missions.tooltips.RestRewardsTooltipView():
            inBoxCount = int(event.getArgument('inBoxCount', 0))
            return RestRewardsTooltipView(list(self.viewModel.getRewards())[-inBoxCount:])
        else:
            return

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltipData.get(tooltipId)

    def __onClose(self):
        self.closeView()

    def __openNextQuestView(self, event):
        self.__appLoader.getApp().containerManager.destroyViews(VIEW_ALIAS.BATTLE_RESULTS)
        nextQuestId = int(event.get('id', -1))
        nextQuest = self.__personalMissionsController.getQuest(nextQuestId)
        if nextQuest is None:
            return
        else:
            showQuestViewById(questId=nextQuestId, operationId=nextQuest.getOperationID())
            self.closeView()
            return

    def __onChooseRewards(self, args):
        questId = args.get('id')
        if questId:
            import gui.impl.lobby.personal_missions.personal_missions_window_events as p
            p.showPersonalMissionsRewardsSelectionWindow(questId=questId, onRewardsReceivedCallback=showPersonalMissionsRewardsView)
            self.closeView()


class PersonalMissionsRewardsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, questId=None, selectedBonuses=None, viewType=None, parent=None, operationID=None):
        super(PersonalMissionsRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PersonalMissionsRewardsView(R.views.lobby.personal_missions.PersonalMissionsRewardsView(), questId=questId, selectedBonuses=selectedBonuses, viewType=viewType, operationID=operationID), parent=parent, layer=WindowLayer.OVERLAY)
