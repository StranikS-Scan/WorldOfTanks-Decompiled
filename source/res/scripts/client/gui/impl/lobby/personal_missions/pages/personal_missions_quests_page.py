# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/pages/personal_missions_quests_page.py
from typing import Union, Dict, Any, List
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from frameworks.wulf.view.submodel_presenter import PageSubModelPresenter
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_main_quests_view_model import PageViewIdEnum
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quests_card_model import Pm3QuestsCardModel, CardState
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quests_line_model import Pm3QuestsLineModel, QuestLineType
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quests_page_tab_model import Pm3QuestsPageTabModel, TabState
from gui.impl.gen.view_models.views.lobby.personal_missions.pages.pm3_quests_view_model import Pm3QuestsViewModel, OperationState
from gui.server_events.event_items import PersonalMission
from gui.server_events.events_dispatcher import showPersonalMissionsOperationsMap
from gui.shared.event_dispatcher import showHangar
from helpers import dependency
from personal_missions import PM_BRANCH
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IPersonalMissionsController
from gui.impl.lobby.personal_missions.personal_missions_window_events import showPersonalMissionsVehicleView, SERVER_SETTINGS_KEYS
from frameworks.wulf import Array
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from CurrentVehicle import g_currentVehicle
from skeletons.gui.lobby_context import ILobbyContext
QuestLineTypeIndexes = {0: QuestLineType.HIT,
 1: QuestLineType.KILLS,
 2: QuestLineType.ASSIST,
 3: QuestLineType.BATTLE,
 4: QuestLineType.MASTER}
MAX_CHAIN_ID = 3
MIN_PM3_OPERATION_ID = 8
DEFAULT_CHAIN_ID = 1

class PersonalMissionQuestsPage(PageSubModelPresenter):
    __slots__ = ('__lastUpdateTime', '__lineSize', '__numberLine', '__operation', '__currentChainId', '__currentOperationId', '__backFromQuest')
    __personalMissionsCtrl = dependency.descriptor(IPersonalMissionsController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, viewModel, parentView):
        super(PersonalMissionQuestsPage, self).__init__(viewModel, parentView)
        self.__lastUpdateTime = None
        self.__lineSize = None
        self.__numberLine = None
        self.__operation = None
        self.__currentChainId = 1
        self.__currentOperationId = 8
        return

    @property
    def pageId(self):
        return PageViewIdEnum.QUESTS

    @property
    def viewModel(self):
        return super(PersonalMissionQuestsPage, self).getViewModel()

    def initialize(self, *args, **kwargs):
        super(PersonalMissionQuestsPage, self).initialize(*args, **kwargs)
        operationId = kwargs.get('operationId', MIN_PM3_OPERATION_ID)
        chainId = kwargs.get('chainId', DEFAULT_CHAIN_ID)
        self.__currentOperationId = operationId
        self.__currentChainId = chainId
        self.__updateData(isSwitched=kwargs.get('backFromQuest', False))
        serverSettings = self.__settingsCore.serverSettings
        if not serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.PM_NEW_CAMPAIGN_HINT):
            serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.PM_NEW_CAMPAIGN_HINT: True})

    def _getEvents(self):
        return ((self.__personalMissionsCtrl.onUpdated, self.__updateData),
         (self.__personalMissionsCtrl.onQuestsUpdated, self.__updateData),
         (self.__personalMissionsCtrl.onItemCacheUpdated, self.__updateData),
         (self.viewModel.switchTab, self.__switchTab),
         (self.viewModel.backToOperation, self.__backToOperation),
         (self.viewModel.openVehicleViewWindow, self.__openVehicleViewWindow),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onSettingsChange))

    def getTabOperationState(self, quests):
        if not self.__operation.isUnlocked():
            return OperationState.LOCKED
        if all((quest.isFullCompleted() for quest in quests)):
            return OperationState.COMPLETEWITHHONOR
        if quests and not quests[0].hasRequiredVehicles():
            return OperationState.LOCKEDNOVEHICLE
        if any((quest.isInProgress() for quest in quests)):
            return OperationState.ACTIVE
        return OperationState.COMPLETE if all((quest.isCompleted() for quest in quests)) else OperationState.ALERT

    @staticmethod
    def getCardState(quest):
        if quest.isCompleted():
            if quest.isDisabled():
                return CardState.DONES
            if quest.isOnPause:
                return CardState.DONEP
            if quest.isFinal():
                if quest.isFullCompleted():
                    return CardState.DONEH
                return CardState.DONE
            return CardState.DONE
        if quest.isDisabled():
            return CardState.SWITCH
        if quest.isOnPause:
            return CardState.PAUSE
        if not quest.isAvailable().isValid:
            return CardState.NOTAVAILABLE
        return CardState.INPROGRESS if quest.isInProgress() else CardState.AVAILABLE

    def __onSettingsChange(self, diff):
        if not any((key in SERVER_SETTINGS_KEYS for key in diff.iterkeys())):
            return
        if not self.__lobbyContext.getServerSettings().isPersonalMissionsEnabled(PM_BRANCH.PERSONAL_MISSION_3):
            showHangar()
            return
        operation = self.__personalMissionsCtrl.getOperationById(self.__currentOperationId)
        if operation.isDisabled():
            showPersonalMissionsOperationsMap(PM_BRANCH.PERSONAL_MISSION_3)
            return
        self.__updateData()

    def __updateData(self, isSwitched=False):
        ctrl = self.__personalMissionsCtrl
        self.__operation = ctrl.getOperationById(self.__currentOperationId)
        if self.__operation is None:
            return
        else:
            with self.getViewModel().transaction() as model:
                model.setOperationName(self.__operation.getShortUserName())
                model.setOperationId(self.__operation.getID())
                model.setIsSwitched(isSwitched)
                model.setPrevOperationName(ctrl.getPreviousOperationName(self.__currentOperationId))
                tabs = Array()
                questsChains = ctrl.getQuestsChainsByOperationId(self.__currentOperationId)
                allQuests = ctrl.getAllQuests()
                currVehLevel = MIN_VEHICLE_LEVEL if g_currentVehicle.item is None else g_currentVehicle.getLevel()
                for chainId, chain in questsChains.iteritems():
                    isSelected = False
                    chainMaxLevel = chain.get('maxLevel', MAX_VEHICLE_LEVEL)
                    chainMinLevel = chain.get('minLevel', MIN_VEHICLE_LEVEL)
                    tabState = self.__getTabState(self.__personalMissionsCtrl.getQuestsByChainAndOperationId(chainId, self.__currentOperationId))
                    if chainMaxLevel >= currVehLevel >= chainMinLevel and not isSwitched:
                        self.__currentChainId = chainId
                        isSelected = True
                    elif currVehLevel < chain.get('minLevel', MIN_VEHICLE_LEVEL) and self.__currentChainId == chainId:
                        self.__currentChainId = chainId if isSwitched else DEFAULT_CHAIN_ID
                        isSelected = True
                    elif isSwitched and self.__currentChainId == chainId:
                        isSelected = True
                    self.__updatePersonalMissionsTab(tabs, chain, chainId, tabState, isSelected)
                    if chainId == self.__currentChainId:
                        linesIds = ctrl.getLinesIdsByChainAndOperationId(self.__currentChainId, self.__currentOperationId)
                        questsLines = model.getQuestsLines()
                        questsLines.clear()
                        for i in range(0, len(linesIds)):
                            self.__updatePersonalMissionsQuestsLine(questsLines, allQuests, i, linesIds)

                        questsLines.invalidate()
                        model.setState(self.getTabOperationState(chain.get('data', [])))
                        model.setMaxVehicleLevel(chain.get('maxLevel', MAX_VEHICLE_LEVEL))
                        model.setMinVehicleLevel(chain.get('minLevel', MIN_VEHICLE_LEVEL))

                model.setTabs(tabs)
            return

    @staticmethod
    def __getTabState(quests):
        isFullComplete = True
        isAvailable = False
        isComplete = True
        for quest in quests.itervalues():
            if isFullComplete and not quest.isFullCompleted():
                isFullComplete = False
            if isComplete and not quest.isCompleted():
                isComplete = False
            if not isAvailable and not quest.isAvailable().isValid:
                isAvailable = True

        if isFullComplete:
            return TabState.COMPLETEWITHHONOR
        if isComplete:
            return TabState.COMPLETED
        return TabState.ISAVAILABLE if isAvailable else TabState.DISABLED

    def __updatePersonalMissionsTab(self, tabsModel, chain, chainId, tabState, isSelected):
        tab = Pm3QuestsPageTabModel()
        tab.setId(chainId)
        tab.setValue(len(self.__personalMissionsCtrl.getCompletedQuestsByChainAndOperationId(chainId, self.__currentOperationId)))
        tab.setMaxVehicleLevel(chain.get('maxLevel', MAX_VEHICLE_LEVEL))
        tab.setMinVehicleLevel(chain.get('minLevel', MIN_VEHICLE_LEVEL))
        tab.setMaxValue(len(self.__personalMissionsCtrl.getQuestsByChainAndOperationId(chainId, self.__currentOperationId)))
        tab.setState(tabState)
        tab.setSelected(isSelected)
        tabsModel.addViewModel(tab)

    def __updatePersonalMissionsQuestsLine(self, linesListModel, quests, index, linesIds):
        line = Pm3QuestsLineModel()
        line.setType(QuestLineTypeIndexes.get(index, QuestLineType.HIT))
        line.setId(index)
        questsCards = line.getCards()
        questsCards.clear()
        for i in range(linesIds[index][0], linesIds[index][1] + 1):
            self.__updatePersonalMissionsQuestsCard(questsCards, quests, i)

        questsCards.invalidate()
        linesListModel.addViewModel(line)

    def __updatePersonalMissionsQuestsCard(self, cardsListModel, quests, questId):
        quest = quests.get(questId, None)
        if quest is None:
            return
        else:
            ctrl = self.__personalMissionsCtrl
            currentQuest = ctrl.getQuest(questId)
            card = Pm3QuestsCardModel()
            card.setId(questId)
            card.setType(self.getCardState(quest))
            card.setSelected(quest.isInProgress())
            card.setIsLast(quest.isFinal())
            card.setQuestName(currentQuest.getUserName())
            cardsListModel.addViewModel(card)
            return

    def __switchTab(self, args):
        self.__currentChainId = int(args.get('tabId', 1))
        self.__updateData(True)

    def __openVehicleViewWindow(self):
        showPersonalMissionsVehicleView(self.__currentOperationId)

    def __backToOperation(self):
        self.destroy()
        showHangar()
