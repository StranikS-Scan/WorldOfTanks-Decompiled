# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/pages/personal_missions_quest_page.py
from typing import Union, Dict, Any
from frameworks.wulf.view.submodel_presenter import PageSubModelPresenter
from gui.impl.backport.backport_tooltip import _BackportTooltipContent
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_card_model import Pm3CardModel, SmallCardState
import SoundGroups
from gui.server_events.events_dispatcher import showPersonalMissionsOperationsMap
from gui.server_events.pm3_constants import SOUNDS
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quest_view_model import Pm3QuestViewModel, QuestState, QuestLineType
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_main_quests_view_model import PageViewIdEnum
from gui.impl.lobby.personal_missions.personal_missions_quest_model import QuestModelParser
from gui.impl.lobby.personal_missions.personal_missions_window_events import showPersonalMissionsRewardsSelectionWindow, showPersonalMissionsOperationWindow, SERVER_SETTINGS_KEYS
from gui.server_events.event_items import PersonalMission
from gui.shared.event_dispatcher import showHangar
from helpers import dependency, int2roman
from personal_missions import PM_BRANCH
from skeletons.gui.game_control import IPersonalMissionsController
from gui.impl.gen import R
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from gui.shared.utils import decorators
from gui import SystemMessages
from gui.shared.gui_items.processors import quests as quests_proc
from frameworks.wulf import Array
QuestTypeIndexes = {0: QuestLineType.HIT,
 1: QuestLineType.KILLS,
 2: QuestLineType.ASSIST,
 3: QuestLineType.BATTLE,
 4: QuestLineType.MASTER}

class PersonalMissionQuestPage(PageSubModelPresenter):
    __slots__ = ('__lastUpdateTime', '__currentQuestId', '__questModelParser')
    __personalMissionsCtrl = dependency.descriptor(IPersonalMissionsController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, viewModel, parentView):
        super(PersonalMissionQuestPage, self).__init__(viewModel, parentView)
        self.__lastUpdateTime = None
        self.__currentQuestId = 481
        self.__questModelParser = QuestModelParser()
        return

    @property
    def pageId(self):
        return PageViewIdEnum.QUEST

    @property
    def viewModel(self):
        return super(PersonalMissionQuestPage, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(PersonalMissionQuestPage, self).initialize(*args, **kwargs)
        questId = kwargs.get('questId', 481)
        self.__currentQuestId = int(questId)
        self.__updateData()

    def getQuestState(self, quest):
        ctrl = self.__personalMissionsCtrl
        operation = ctrl.getOperationById(quest.getOperationID())
        if not operation.isUnlocked():
            return QuestState.NAPREVIOUS
        if not quest.hasRequiredVehicles():
            return QuestState.NATECH
        if not quest.isUnlocked():
            return QuestState.NAPREVIOUSALL
        if quest.isInProgress():
            if quest.isCompleted():
                return QuestState.INPROGRESSHONOR
            return QuestState.INPROGRESS
        if quest.isCompleted():
            if quest.isFinal():
                if quest.isFullCompleted():
                    return QuestState.DONEHONOR
                return QuestState.DONEBASIC
            return QuestState.DONE
        return QuestState.AVAILABLE

    @staticmethod
    def getSmallCardState(quest):
        if quest.isCompleted():
            if quest.isDisabled():
                return SmallCardState.DONES
            if quest.isOnPause:
                return SmallCardState.DONEP
            if quest.isFinal():
                if quest.isFullCompleted():
                    return SmallCardState.DONEH
                return SmallCardState.DONE
            return SmallCardState.DONE
        if quest.isDisabled():
            return SmallCardState.SWITCH
        if quest.isOnPause:
            return SmallCardState.PAUSE
        if not quest.isAvailable().isValid:
            return SmallCardState.NOTAVAILABLE
        return SmallCardState.INPROGRESS if quest.isInProgress() else SmallCardState.AVAILABLE

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            if tooltipData is not None:
                return _BackportTooltipContent(tooltipData)
            return
        else:
            return

    def _getEvents(self):
        return ((self.__personalMissionsCtrl.onUpdated, self.__updateData),
         (self.__personalMissionsCtrl.onQuestsUpdated, self.__updateData),
         (self.__personalMissionsCtrl.onRewardsViewClose, self.__onRewardsViewClose),
         (self.viewModel.applyQuest, self.__applyQuest),
         (self.viewModel.switchSelected, self.__switchSelected),
         (self.viewModel.backToOperation, self.__backToOperation),
         (self.viewModel.nextQuest, self.__nextQuest),
         (self.viewModel.prevQuest, self.__prevQuest),
         (self.viewModel.getSelectionBonus, self.__getSelectionBonus),
         (self.viewModel.updateRewards, self.__updateData),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onSettingsChange))

    def __onSettingsChange(self, diff):
        if not any((key in SERVER_SETTINGS_KEYS for key in diff.iterkeys())):
            return
        if not self.__lobbyContext.getServerSettings().isPersonalMissionsEnabled(PM_BRANCH.PERSONAL_MISSION_3):
            showHangar()
            return
        ctrl = self.__personalMissionsCtrl
        currentQuest = ctrl.getQuest(self.__currentQuestId)
        operationID = currentQuest.getOperationID()
        operation = ctrl.getOperationById(operationID)
        if operation.isDisabled():
            showPersonalMissionsOperationsMap(PM_BRANCH.PERSONAL_MISSION_3)
            return
        if currentQuest.isDisabled():
            showPersonalMissionsOperationWindow(PageViewIdEnum.QUESTS, operationID)
            return
        self.__updateData()

    def __updateData(self, isShowAnimationRewards=False):
        ctrl = self.__personalMissionsCtrl
        currentQuest = ctrl.getQuest(self.__currentQuestId)
        if currentQuest is None:
            return
        else:
            with self.getViewModel().transaction() as model:
                linesIdsList = ctrl.getLinesIdsByChainAndOperationId(currentQuest.getChainID(), currentQuest.getOperationID())
                currentQuestId = currentQuest.getID()
                for index, lineIds in enumerate(linesIdsList):
                    if currentQuestId in range(lineIds[0], lineIds[1] + 1):
                        model.setType(QuestTypeIndexes.get(index, QuestLineType.HIT))
                        break

                cardsListModel = Array()
                initialQuestsSortedIds = sorted(ctrl.getInitialQuestsByChainAndOperationId(currentQuest.getChainID(), currentQuest.getOperationID()))
                finalQuestsSortedIds = sorted(ctrl.getFinalQuestsByChainAndOperationId(currentQuest.getChainID(), currentQuest.getOperationID()))
                linesIds = zip(initialQuestsSortedIds, finalQuestsSortedIds)
                lineId = 0
                for index in range(1, len(linesIds)):
                    if self.__currentQuestId in range(linesIds[index][0], linesIds[index][1] + 1):
                        lineId = index

                for questId in range(linesIds[lineId][0], linesIds[lineId][1] + 1):
                    self.__updatePersonalMissionsCard(cardsListModel, ctrl.getAllQuests(), questId)

                model.setCardsList(cardsListModel)
                self.__questModelParser.updateQuestModelFromID(questID=self.__currentQuestId, questModel=model.questData, isShowAnimationRewards=isShowAnimationRewards)
                questState = self.getQuestState(currentQuest)
                model.setState(questState)
                model.setTitleValue(ctrl.getPreviousOperationName(currentQuest.getOperationID()) if questState == QuestState.NAPREVIOUS else '-'.join([int2roman(currentQuest.getVehMinLevel()), int2roman(currentQuest.getVehMaxLevel())]))
            return

    def __onRewardsViewClose(self, **kwargs):
        if self.__currentQuestId == kwargs.get('questId', 0):
            self.__updateData(isShowAnimationRewards=kwargs.get('isSelectedRewards', False))

    def __updatePersonalMissionsCard(self, cardsListModel, quests, questId):
        quest = quests.get(questId, None)
        if quest is None:
            return
        else:
            card = Pm3CardModel()
            card.setQuestId(questId)
            card.setState(self.getSmallCardState(quest))
            card.setIsSelected(questId == self.__currentQuestId)
            card.setIsLast(quest.isFinal())
            cardsListModel.addViewModel(card)
            return

    def __applyQuest(self, args):
        self.__processMission(args.get('id'))

    @decorators.adisp_process('updating')
    def __processMission(self, eventID):
        quest = self.__personalMissionsCtrl.getQuest(eventID)
        result = yield quests_proc.PMQuestSelect(quest, self.__eventsCache.getPersonalMissions(), PM_BRANCH.PERSONAL_MISSION_3).request()
        if result and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __switchSelected(self, args):
        self.__playSwitchCardSound()
        ctrl = self.__personalMissionsCtrl
        inputId = args.get('id')
        selectedQuest = ctrl.getQuest(inputId)
        if selectedQuest is None or selectedQuest.isDisabled():
            return
        else:
            self.__currentQuestId = inputId
            self.__updateData()
            return

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            tooltipData = self.__questModelParser.getTooltipData()
            return tooltipData[tooltipId] if tooltipId in tooltipData else None

    def __nextQuest(self):
        self.__playSwitchCardSound()
        self.__currentQuestId = self.__personalMissionsCtrl.getNextQuestId(self.__currentQuestId)
        self.__updateData()

    def __prevQuest(self):
        self.__playSwitchCardSound()
        self.__currentQuestId = self.__personalMissionsCtrl.getPrevQuestId(self.__currentQuestId)
        self.__updateData()

    def __playSwitchCardSound(self):
        SoundGroups.g_instance.playSound2D(SOUNDS.SWITCH_CARD_ANIMATION)

    def __backToOperation(self):
        self.destroy()
        showHangar()

    def __getSelectionBonus(self, args):
        questId = args.get('questId')
        if questId is not None:
            showPersonalMissionsRewardsSelectionWindow(questId)
        return
