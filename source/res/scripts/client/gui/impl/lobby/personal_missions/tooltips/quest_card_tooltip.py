# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/tooltips/quest_card_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.quest_card_tooltip_model import QuestCardTooltipModel, QuestState, DescriptionQuestStatus
from gui.impl.lobby.personal_missions.personal_missions_quest_model import QuestModelParser
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.server_events.event_items import PersonalMission, PMOperation
from helpers import dependency
from skeletons.gui.game_control import IPersonalMissionsController
MIN_VEHICLE_LEVEL = 1
MAX_VEHICLE_LEVEL = 11

class QuestCardTooltip(ViewImpl):
    __slots__ = ('__currentQuestId', '__questModelParser')
    __personalMissionsCtrl = dependency.descriptor(IPersonalMissionsController)

    def __init__(self, questId):
        settings = ViewSettings(R.views.lobby.personal_missions.tooltips.QuestCardTooltip())
        settings.model = QuestCardTooltipModel()
        self.__currentQuestId = questId
        self.__questModelParser = QuestModelParser()
        super(QuestCardTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QuestCardTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(QuestCardTooltip, self)._onLoading(*args, **kwargs)
        self.__updateData()

    @staticmethod
    def __getQuestState(quest, operation):
        if not operation.isUnlocked():
            return QuestState.NAPREVIOUS
        if not quest.isUnlocked():
            return QuestState.NAPREVIOUSALL
        if not quest.hasRequiredVehicles():
            return QuestState.NATECH
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
    def __getDescriptionStatus(quest, operation):
        if quest.isDisabled():
            return DescriptionQuestStatus.NOTAVAILABLESWITCH
        if not quest.hasRequiredVehicles():
            return DescriptionQuestStatus.NOTAVAILABLENOVEHICLE
        if not operation.isUnlocked():
            return DescriptionQuestStatus.NOTAVAILABLEPREVOPERATIONNOTCOMPLETED
        if not quest.isUnlocked():
            return DescriptionQuestStatus.NOTAVAILABLEPREVQUESTNOTCOMPLETED
        if quest.isFinal() and quest.isFullCompleted():
            return DescriptionQuestStatus.DONEH
        if quest.isCompleted():
            if quest.isFinal():
                if quest.isFullCompleted():
                    return DescriptionQuestStatus.DONEH
                return DescriptionQuestStatus.DONE
            return DescriptionQuestStatus.DONE
        return DescriptionQuestStatus.AVAILABLE

    def __updateData(self):
        ctrl = self.__personalMissionsCtrl
        currentQuest = ctrl.getQuest(self.__currentQuestId)
        operation = ctrl.getOperationById(currentQuest.getOperationID())
        if currentQuest is None:
            return
        else:
            questsChains = ctrl.getQuestsChainsByOperationId(currentQuest.getOperationID())
            with self.getViewModel().transaction() as model:
                model.setId(self.__currentQuestId)
                model.setName(currentQuest.getUserName())
                model.setIsFinal(currentQuest.isFinal())
                questStatus = self.__getQuestState(currentQuest, operation)
                model.setStatus(questStatus)
                model.setPrevOperationName(ctrl.getPreviousOperationName(currentQuest.getOperationID()))
                currentOperation = ctrl.getOperationById(currentQuest.getOperationID())
                model.setDescriptionStatus(self.__getDescriptionStatus(currentQuest, currentOperation))
                model.setMaxVehicleLevel(questsChains.get(currentQuest.getChainID(), {}).get('maxLevel', MAX_VEHICLE_LEVEL))
                model.setMinVehicleLevel(questsChains.get(currentQuest.getChainID(), {}).get('minLevel', MIN_VEHICLE_LEVEL))
                self.__questModelParser.updateQuestModelFromID(questID=self.__currentQuestId, questModel=model.questData)
            return
