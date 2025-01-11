# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_quest_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_item_part_model import Pm3QuestItemPartModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_item_part_progress_model import Pm3QuestItemPartProgressModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_part_relation_model import QuestRelationType
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_relation_group_model import Pm3QuestRelationGroupModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_part_model import Pm3QuestPartModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_quest_model import Pm3QuestModel
from gui.impl.lobby.personal_missions.personal_mission_bonuses_packers import packBonusModelAndTooltipData
from skeletons.gui.game_control import IPersonalMissionsController
from gui.server_events.event_items import PersonalMission
from gui.impl.gen import R
from gui.impl import backport
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PersonalMissions
from helpers import dependency, int2roman
import personal_missions_constants as PMConstants
from skeletons.gui.offers import IOffersDataProvider

class QuestModelParser(object):
    __slots__ = ('__pm3Controller', 'generalQuestID', '__tooltipData', 'questInfo', 'questConfig')
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __QUEST_CONFIG_PARAMS_NAMES = ['battlesLimit', 'uniqueGoal', 'totalGoal']
    __QUEST_CONFIG_ICON_TYPE_NAMES = ['lightTank',
     'mediumTank',
     'heavyTank',
     'AT-SPG',
     'SPG']

    def __init__(self):
        self.__pm3Controller = dependency.instance(IPersonalMissionsController)
        self.generalQuestID = ''
        self.__tooltipData = {}
        self.questInfo = None
        self.questConfig = {}
        return

    def updateQuestModelFromID(self, questID, questModel=Pm3QuestModel(), isShowAnimationRewards=False):
        self.questInfo = self.__pm3Controller.getQuest(questID)
        if self.questInfo is None:
            return
        else:
            self.questConfig = self.questInfo.getConditionsConfig()
            questModel.setId(self.questInfo.getID())
            questModel.setName(self.questInfo.getUserName())
            questModel.setIsFinal(self.questInfo.isFinal())
            questModel.setQuestLevelFrom(int2roman(self.questInfo.getVehMinLevel()))
            questModel.setQuestLevelTo(int2roman(self.questInfo.getVehMaxLevel()))
            self.generalQuestID = self.questInfo.getGeneralQuestID()
            mainQuestsDict = {}
            addQuestsDict = {}
            for key, val in self.questConfig.items():
                quest = val.get('config')
                if quest['isMain']:
                    mainQuestsDict[key] = val
                addQuestsDict[key] = val

            self.__tooltipData.clear()
            questsProgress = self.questInfo.getConditionsProgress()
            self.__updateQuestsPartModel(questModel.mainQuests, mainQuestsDict, questsProgress, isShowAnimationRewards=isShowAnimationRewards)
            if addQuestsDict:
                self.__updateQuestsPartModel(questModel.addQuests, addQuestsDict, questsProgress, isMain=False, isShowAnimationRewards=isShowAnimationRewards)
            else:
                self.__clearPm3QuestPartModel(questModel.addQuests)
            return questModel

    def __clearPm3QuestPartModel(self, pm3QuestPartModel):
        pm3QuestPartModel.getRewards().clear()
        pm3QuestPartModel.relation.getGroups().clear()
        pm3QuestPartModel.getQuests().clear()

    def getTooltipData(self):
        return self.__tooltipData

    def __updateQuestsPartModel(self, questsPartModel, quests, questsProgress, isMain=True, isShowAnimationRewards=False):
        rewardList = questsPartModel.getRewards()
        rewardList.clear()
        groupsModel = questsPartModel.relation.getGroups()
        questsPartModel.relation.setRelationType(QuestRelationType.OR)
        packBonusModelAndTooltipData(self.questInfo.getBonuses(isMain=isMain), rewardList, self.__tooltipData, offersDataProvider=self.__offersProvider, isShowAnimationRewards=isShowAnimationRewards)
        rewardList.invalidate()
        questIsDone = isMain and self.questInfo.isCompleted() or not isMain and self.questInfo.isFullCompleted()
        questsPartModel.setIsDone(questIsDone)
        listQuestModel = questsPartModel.getQuests()
        listQuestModel.clear()
        groupsRelationDict = {}
        for questName in quests:
            self.__addQuestItemPart(listQuestModel, quests, questsProgress.get(questName, {}), questName, questIsDone)
            groupList = groupsRelationDict.get(quests[questName].get('config').get('groupID', 0), [])
            groupList = groupList + [questName]
            groupsRelationDict.update({quests[questName].get('config').get('groupID', 0): groupList})

        listQuestModel.invalidate()
        self.__updateRelation(groupsModel, groupsRelationDict)

    @classmethod
    def getDescriptionsForQuest(cls, generalQuestId, quests, questName):
        quest = quests[questName]
        title = ''
        description = ''
        titleName = '{}_title_{}'.format(generalQuestId, questName)
        descriptionName = '{}_description_{}'.format(generalQuestId, questName)
        titleResId = R.strings.personal_missions_details.dyn(titleName)()
        configs = quest.get('config', {})
        paramsObj = configs.get('params', {}).copy()
        paramsObj['goal'] = configs.get('goal', configs.get('totalGoal', 0) / configs.get('uniqueGoal', 1))
        questDescription = quest.get('description', {})
        if isinstance(questDescription, PMConstants.AverageDescription):
            paramsObj['goal'] //= quests[questDescription.counterID]['config'].get('goal', 1)
        for paramName in cls.__QUEST_CONFIG_PARAMS_NAMES:
            paramsObj[paramName] = configs.get(paramName, 0)

        if titleResId > 0:
            title = backport.text(titleResId, **paramsObj)
        descriptionId = R.strings.personal_missions_details.dyn(descriptionName)()
        if descriptionId > 0:
            description = backport.text(descriptionId, **paramsObj)
        return (title, description)

    def __addQuestItemPart(self, listQuestModel, questsConfig, questProgress, questName, isDone):
        questItemPartModel = Pm3QuestItemPartModel()
        questConfig = questsConfig.get(questName, {})
        icon = questConfig.get('description', None)
        config = questConfig['config']
        if isinstance(icon, PMConstants.RegularDescription):
            questItemPartModel.setIcon(icon.iconID)
        elif isinstance(icon, PMConstants.HeaderDescription):
            questItemPartModel.setHeaderDescription(icon.displayType)
            if icon.displayType == PMConstants.DISPLAY_TYPE.BIATHLON:
                questItemPartModel.setBiathlonGoal(config.get('goal', 0))
        title, description = self.getDescriptionsForQuest(self.generalQuestID, questsConfig, questName)
        questItemPartModel.setIdName(questName)
        questItemPartModel.setName(title)
        questItemPartModel.setDescription(description)
        isCumulative = config.get('isCumulative', False)
        isAward = config.get('isAward', False)
        questItemPartModel.setIsCumulative(isCumulative)
        questItemPartModel.setIsCycle(not isCumulative and isAward)
        questItemPartModel.setQuestTooltipID(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent())
        questItemPartModel.setType(questConfig.get('type', ''))
        progressionModel = questItemPartModel.getProgression()
        progressionModel.clear()
        self.__addQuestItemPartProgresses(progressionModel, questsConfig, questProgress, questName, isDone)
        listQuestModel.invalidate()
        listQuestModel.addViewModel(questItemPartModel)
        return

    def __addQuestItemPartProgresses(self, progressionModel, questsConfigs, questProgress, taskName, isDone):
        questConfig = questsConfigs[taskName]
        config = questConfig['config']
        battlesLimit = config.get('battlesLimit', 0)
        description = questConfig.get('description', None)
        if isinstance(description, PMConstants.HeaderDescription) and description.displayType == PMConstants.DISPLAY_TYPE.BIATHLON:
            self.__addProgressesForBattlesSeriesWithLimit(progressionModel, battlesLimit, questProgress, taskName, isDone)
            return
        elif 'battlesSeries' in taskName and isinstance(description, PMConstants.HeaderDescription) and description.displayType == PMConstants.DISPLAY_TYPE.SERIES:
            self.__addProgressesForBattlesSeriesWithDisplayTypeSeries(progressionModel, questConfig, questProgress, taskName, isDone)
            return
        elif not config.get('isCumulative', False) and 'damageAndAssist' not in taskName:
            return
        else:
            uniqueGoal = config.get('uniqueGoal', 0)
            if 'killsDiversity' in taskName and uniqueGoal == len(self.__QUEST_CONFIG_ICON_TYPE_NAMES):
                self.__addProgressesForKillsDiversity(progressionModel, questConfig, questProgress, taskName, isDone)
                return
            valueTo = config.get('goal', 0)
            currValue = valueTo if isDone else min(questProgress.get('value', 0), valueTo)
            if isinstance(description, PMConstants.AverageDescription):
                counter = questsConfigs[description.counterID]['config'].get('goal', 1)
                valueTo //= counter
                currValue //= counter
            prevValues = self.__getPrevProgressQuest(self.generalQuestID, taskName)
            self.__addQuestItemPartProgressModel(progressionModel, valueTo, prevValues, currValue, False)
            self.__saveProgressQuest(self.generalQuestID, taskName, currValue)
            return

    def __addProgressesForBattlesSeriesWithLimit(self, progressionModel, battlesLimit, questProgress, taskName, isDone):
        targetValue = 1
        currValues = questProgress.get('battles', [])
        for i in range(battlesLimit):
            tempCurrValue = targetValue if isDone or len(currValues) > i else 0
            isFailed = False if isDone or len(currValues) <= i else not currValues[i]
            currTaskName = '{}_{}'.format(taskName, i)
            prevValues = self.__getPrevProgressQuest(self.generalQuestID, currTaskName)
            self.__addQuestItemPartProgressModel(progressionModel, targetValue, prevValues, tempCurrValue, isFailed)
            self.__saveProgressQuest(self.generalQuestID, currTaskName, tempCurrValue)

    def __addProgressesForBattlesSeriesWithDisplayTypeSeries(self, progressionModel, questConfig, questProgress, taskName, isDone):
        config = questConfig['config']
        valueTo = config.get('battlesSeries', config.get('goal', 0))
        prevValues = self.__getPrevProgressQuest(self.generalQuestID, taskName)
        currValue = valueTo if isDone else min(questProgress.get('value', 0), valueTo)
        targetValue = 1
        for i in range(valueTo):
            tempCurrentValue = targetValue if isDone or currValue > i else 0
            self.__addQuestItemPartProgressModel(progressionModel, targetValue, targetValue if prevValues > i else 0, tempCurrentValue, False)

        self.__saveProgressQuest(self.generalQuestID, taskName, currValue)

    def __addProgressesForKillsDiversity(self, progressionModel, questConfig, questProgress, taskName, isDone):
        config = questConfig['config']
        totalGoal = config.get('totalGoal', 0)
        goal = totalGoal // config['uniqueGoal']
        currValues = questProgress.get('counter', {})
        for iconName in self.__QUEST_CONFIG_ICON_TYPE_NAMES:
            currTaskName = '{}_{}'.format(taskName, iconName)
            prevValues = self.__getPrevProgressQuest(self.generalQuestID, currTaskName)
            currValue = goal if isDone else min(currValues.get(iconName, 0), goal)
            self.__addQuestItemPartProgressModel(progressionModel, goal, prevValues, currValue, False, backport.image(R.images.gui.maps.icons.vehicleTypes.gold.dyn(iconName.replace('-', '_'))()))
            self.__saveProgressQuest(self.generalQuestID, currTaskName, currValue)

    @staticmethod
    def __addQuestItemPartProgressModel(progressionModel, valueTo, prevValues, currValue, isFailed, icon=None):
        questItemPartProgressModel = Pm3QuestItemPartProgressModel()
        questItemPartProgressModel.setTo(valueTo)
        questItemPartProgressModel.setPreviousValue(prevValues)
        questItemPartProgressModel.setCurrentValue(currValue)
        questItemPartProgressModel.setIsFailed(isFailed)
        if icon is not None:
            questItemPartProgressModel.setIcon(icon)
        progressionModel.addViewModel(questItemPartProgressModel)
        return

    def __updateRelation(self, relationModel, groupsDict):
        relationModel.clear()
        order = ('battlesSeries',)

        def compareKeys(x):
            if x in order:
                return order.index(x)
            return '' if 'Series' in x else x

        for groupList in groupsDict:
            group = Pm3QuestRelationGroupModel()
            groupModel = group.getNames()
            groupModel.clear()
            list = groupsDict[groupList]
            list.sort(key=compareKeys)
            for questName in list:
                groupModel.addString(questName)

            relationModel.addViewModel(group)

        relationModel.invalidate()

    def __saveProgressQuest(self, generalQuestID, taskName, currentVal):
        settings = AccountSettings.getPersonalMissions(PersonalMissions.CURR_QUESTS_STATEMENT)
        settings.setdefault(generalQuestID, {})
        settings[generalQuestID][taskName] = currentVal
        AccountSettings.setPersonalMissions(PersonalMissions.CURR_QUESTS_STATEMENT, settings)

    def __getPrevProgressQuest(self, generalQuestID, taskName):
        settings = AccountSettings.getPersonalMissions(PersonalMissions.CURR_QUESTS_STATEMENT)
        return settings.get(generalQuestID, {}).get(taskName, 0)
