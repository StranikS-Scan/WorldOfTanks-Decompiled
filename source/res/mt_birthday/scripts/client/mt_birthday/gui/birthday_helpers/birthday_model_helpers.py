# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/birthday_helpers/birthday_model_helpers.py
import time
import typing
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL, ARENA_BONUS_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events import formatters
from gui.server_events.cond_formatters import FormattableField, FORMATTER_IDS
from gui.shared.missions.packers.conditions import CONDITION_GROUP_AND, PreFormattedConditionModelPacker
from gui.shared.missions.packers.events import BattleQuestUIDataPacker
from gui.shared.money import Currency
from helpers import dependency
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker
from helpers.time_utils import getCurrentLocalServerTimestamp
from mt_birthday.gui.birthday_bonus_packers import BirthdayEntitlementBonusUIPacker, BirthdayTmanBonusUIPacker, BirthdayVehiclesBonusUIPacker, BirthdayCurrencyBonusUIPacker, BirthdayCustomizationBonusUIPacker
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.mt_birthday_quest_model import MtBirthdayQuestModel as QuestModel, QuestStatus
from mt_birthday.gui.impl.gen.view_models.views.lobby.common.player_online_status_model import PlayerOnlineStatus
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.progression_level import ProgressionLevel
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday_common.constants import MT_BIRTHDAY_INFINITY_COMPLETE_TOKEN, MT_BIRTHDAY_INFINITY_PROGRESSION_TOKEN
from messenger.proto.entities import LobbyUserEntity
from personal_missions_constants import CONDITION_ICON
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from typing import Dict, Tuple, Iterable, List
    from gui.server_events.event_items import Quest
    from frameworks.wulf import Array
    ArrayQuestModel = Array[QuestModel]
_BONUSES_ORDER = ('vehicles',
 'lootBoxToken',
 Currency.CRYSTAL,
 Currency.GOLD,
 'premium',
 'premium_plus',
 'tmanToken',
 'customizations',
 'goodies',
 'crewBooks',
 Currency.CREDITS,
 'entitlements',
 'currencies',
 'items',
 'dossier')
_MAX_LEN_MAIN_REWARDS = 3
_BATTLE_TYPES_ORDER = (ARENA_BONUS_TYPE.REGULAR,
 ARENA_BONUS_TYPE.EPIC_RANDOM,
 ARENA_BONUS_TYPE.SORTIE_2,
 ARENA_BONUS_TYPE.FORT_BATTLE_2,
 ARENA_BONUS_TYPE.VERSUS_AI)
_BATTLE_TYPES_ORDER_SET = {bonusType:order for order, bonusType in enumerate(_BATTLE_TYPES_ORDER)}

def birthdayBonusesSortKeyFunc(bonus):
    bonusName = bonus.getName()
    return _BONUSES_ORDER.index(bonusName) if bonusName in _BONUSES_ORDER else len(_BONUSES_ORDER)


def getBirthdayBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'entitlements': BirthdayEntitlementBonusUIPacker,
     'tmanToken': BirthdayTmanBonusUIPacker,
     'vehicles': BirthdayVehiclesBonusUIPacker,
     'currencies': BirthdayCurrencyBonusUIPacker,
     'customizations': BirthdayCustomizationBonusUIPacker})
    return BonusUIPacker(mapping)


@dependency.replace_none_kwargs(birthdayController=ITanksBirthdayController)
def fillChapterLevelsModel(model, birthdayController=None, tooltipData=None):
    currentLevel, _ = birthdayController.progression.getCurrentProgressionLevel()
    if currentLevel is None:
        return
    else:
        levelModels = model.getLevels()
        levelModels.clear()
        levelsCount = len(birthdayController.progression.progressionConfig)
        for levelID in range(1, levelsCount + 1):
            levelModel = model.getLevelsType()()
            with levelModel.transaction() as tx:
                tx.setNumber(levelID)
                tx.setIsCompleted(currentLevel > levelID)
                _fillLevelRewardModels(tx, levelID, birthdayController, tooltipData)
            levelModels.addViewModel(levelModel)

        levelModels.invalidate()
        return


@dependency.replace_none_kwargs(birthdayController=ITanksBirthdayController)
def fillProgression(model, tooltipData=None, birthdayController=None):
    packer = getBirthdayBonusPacker()
    with model.transaction() as tx:
        progression = tx.progression
        progressionController = birthdayController.progression
        currentPoints = progressionController.getProgressionTokensCount()
        progression.setCurrentPoints(currentPoints)
        progression.setPointsDeltaFrom(currentPoints)
        levelIdx, levelConfig = progressionController.getCurrentProgressionLevel()
        progression.setCurrentLevel(levelIdx)
        levels = progression.getLevels()
        levels.clear()
        for levelIdx, levelConfig in progressionController.getSimpleLevels():
            levelModel = ProgressionLevel()
            levelModel.setNumber(levelIdx)
            levelModel.setMaxPoints(levelConfig['maxProgressionPoints'])
            levelModel.setSubstagesCount(levelConfig['maxProgressionPoints'] - levelConfig['minProgressionPoints'])
            levelRewards = levelConfig['bonuses']
            levelRewards.sort(key=birthdayBonusesSortKeyFunc)
            rewardsModels = levelModel.getRewards()
            rewardsModels.clear()
            packBonusModelAndTooltipData(levelRewards, rewardsModels, tooltipData=tooltipData, packer=packer)
            rewardsModels.invalidate()
            levels.addViewModel(levelModel)

        levels.invalidate()
        _, infinityLevelConfig = progressionController.getInfinityLevel()
        progression.setInfinityMaxPoints(infinityLevelConfig['maxProgressionPoints'])
        progression.setInfinityStartPoints(infinityLevelConfig['minProgressionPoints'])
        progression.setInfinityDeltaFrom(currentPoints)
        progression.setInfinityLevelCompleteCount(progressionController.getInfinityProgressionTokensCount())
        progression.setInfinitySubstagesCount(infinityLevelConfig['maxProgressionPoints'] - infinityLevelConfig['minProgressionPoints'])
        levelRewards = infinityLevelConfig['bonuses']
        levelRewards.sort(key=birthdayBonusesSortKeyFunc)
        infinityRewardsModels = progression.getInfinityRewards()
        infinityRewardsModels.clear()
        packBonusModelAndTooltipData(levelRewards, infinityRewardsModels, tooltipData=tooltipData, packer=packer)
        infinityRewardsModels.invalidate()


def _fillLevelRewardModels(levelModel, levelID, birthdayCtrl, tooltipData=None):
    levelRewards = birthdayCtrl.progression.progressionConfig.get(levelID, {}).get('bonuses')
    levelRewards.sort(key=birthdayBonusesSortKeyFunc)
    packer = getBirthdayBonusPacker()
    rewardsModel = levelModel.getRewards()
    rewardsModel.clear()
    packBonusModelAndTooltipData(levelRewards, rewardsModel, tooltipData=tooltipData, packer=packer)
    rewardsModel.invalidate()


def battleTokenFilter(bonus):
    if bonus.getName() == 'battleToken':
        value = bonus.getValue()
        if value.get(MT_BIRTHDAY_INFINITY_COMPLETE_TOKEN) or value.get(MT_BIRTHDAY_INFINITY_PROGRESSION_TOKEN):
            return False
    return True


@dependency.replace_none_kwargs(birthdayController=ITanksBirthdayController)
def makeRewardModels(bonuses, mainRewards, otherRewards, tooltipData=None, birthdayController=None):
    bonuses = [ bonus for bonus in bonuses if battleTokenFilter(bonus) ]
    bonuses.sort(key=birthdayBonusesSortKeyFunc)
    packer = getBirthdayBonusPacker()
    mainBonuses = bonuses[:_MAX_LEN_MAIN_REWARDS]
    otherBonuses = bonuses[_MAX_LEN_MAIN_REWARDS:]
    if len(mainBonuses) == _MAX_LEN_MAIN_REWARDS:
        mainBonuses[0], mainBonuses[1] = mainBonuses[1], mainBonuses[0]
    packBonusModelAndTooltipData(mainBonuses, mainRewards, packer=packer, tooltipData=tooltipData)
    packBonusModelAndTooltipData(otherBonuses, otherRewards, packer=packer, tooltipData=tooltipData)
    mainRewards.invalidate()
    otherRewards.invalidate()


def entProcessor(rewardsData, rewardTemplate, makeQuestsAchieve):
    entitlements = rewardsData.get('entitlements', {})
    for entitlement, data in entitlements.iteritems():
        count = data.get('count', 0)
        if count > 0:
            return makeQuestsAchieve(rewardTemplate, text=backport.text(R.strings.messenger.serviceChannelMessages.epicReward.dyn(entitlement)()), count=count)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def _createSimpleBattleCondition(quest, eventsCache=None):
    playBattleCondition = formatters.packMissionIconCondition(FormattableField(FORMATTER_IDS.SIMPLE_TITLE, ('',)), '', FormattableField(FORMATTER_IDS.DESCRIPTION, ('',)), CONDITION_ICON.BATTLES, current=1 if quest.isCompleted() else 0, total=1, earned=1 if eventsCache.questsProgress.getQuestCompletionChanged(quest.getID()) else 0)
    return PreFormattedConditionModelPacker.pack(playBattleCondition, 'battles')


class BirthdayBattleQuestUIDataPacker(BattleQuestUIDataPacker):

    def __init__(self, event, bonusPackerGetter=getBirthdayBonusPacker, tooltipData=None):
        super(BirthdayBattleQuestUIDataPacker, self).__init__(event, bonusPackerGetter)
        if tooltipData is not None:
            self._tooltipData = tooltipData
        self.__bonusPackerGetter = bonusPackerGetter
        return

    def _packDefaultConds(self, model):
        bonusConditions = model.bonusCondition.getItems()
        if not bonusConditions:
            model.bonusCondition.setConditionType(CONDITION_GROUP_AND)
            bonusConditions.addViewModel(_createSimpleBattleCondition(self._event))

    def _packModel(self, model):
        super(BirthdayBattleQuestUIDataPacker, self)._packModel(model)
        model.setBonusCount(self._event.getBonusCount())
        bonusLimit = self._event.bonusCond.getBonusLimit()
        if bonusLimit is not None:
            model.setBonusLimit(bonusLimit)
        return

    def _packBonuses(self, model):
        packer = self.__bonusPackerGetter()
        packBonusModelAndTooltipData(self._event.getBonuses(), model.getBonuses(), tooltipData=self._tooltipData, packer=packer, startIndex=len(self._tooltipData))


def _createQuestGiverQuestModel(quest, tooltipData):
    minLevel, maxLevel = MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
    packer = BirthdayBattleQuestUIDataPacker(quest, bonusPackerGetter=getBirthdayBonusPacker, tooltipData=tooltipData)
    questModel = packer.pack(model=QuestModel())
    bonusTypes = quest.preBattleCond.getConditions().find('bonusTypes').getValue()
    _, levels, _ = quest.getRequiredVehicleDescr()
    if levels:
        minLevel, maxLevel = min(levels), max(levels)
    return (questModel,
     minLevel,
     maxLevel,
     bonusTypes)


class _FirstActiveQuest(object):

    def __init__(self):
        self.quest = None
        return

    def trySetQuest(self, quest):
        if self.quest is None:
            self.quest = quest
        return


def updateQuestGiverQuestsModel(questsModel, challengesModel, quests, challenges, tooltipData):
    levels = set()
    battleTypes = set()
    quests = sorted(quests, key=lambda q: (q.isCompleted(), q.getStartTime(), int(q.getID().split(':')[2])))
    challenges = sorted(challenges, key=lambda c: (c.isCompleted(), c.getStartTime()))
    nextQuestUnlock = None
    nextChallengeUnlock = None
    firstActiveQuest = _FirstActiveQuest()
    now = getCurrentLocalServerTimestamp()
    for quest in quests:
        if quest.getStartTime() <= now <= quest.getFinishTime():
            questModel, minLevel, maxLevel, bonusTypes = _createQuestGiverQuestModel(quest, tooltipData)
            levels.update((minLevel, maxLevel))
            battleTypes.update(bonusTypes)
            if quest.isCompleted():
                questModel.setStatus(QuestStatus.DONE)
            else:
                questModel.setStatus(QuestStatus.ACTIVE)
                firstActiveQuest.trySetQuest(quest)
            questsModel.addViewModel(questModel)
        if now < quest.getStartTime():
            if not nextQuestUnlock:
                nextQuestUnlock = quest.getStartTimeLeft()

    for challenge in challenges:
        questModel, minLevel, maxLevel, bonusTypes = _createQuestGiverQuestModel(challenge, tooltipData)
        levels.update((minLevel, maxLevel))
        battleTypes.update(bonusTypes)
        if challenge.getStartTime() <= time.time() <= challenge.getFinishTime():
            questModel.setStatus(QuestStatus.ACTIVE)
        elif time.time() < challenge.getStartTime():
            questModel.setStatus(QuestStatus.DISABLED)
            if not nextChallengeUnlock:
                questModel.setStatus(QuestStatus.LOCKED)
                nextChallengeUnlock = challenge.getStartTimeLeft()
        if challenge.isCompleted():
            questModel.setStatus(QuestStatus.DONE)
        if questModel.getStatus() == QuestStatus.ACTIVE:
            firstActiveQuest.trySetQuest(challenge)
        challengesModel.addViewModel(questModel)

    questsModel.invalidate()
    challengesModel.invalidate()
    if not levels:
        levels.update((MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL))
    return (min(levels),
     max(levels),
     sorted(battleTypes, key=lambda b: _BATTLE_TYPES_ORDER_SET.get(b, float('inf'))),
     nextQuestUnlock,
     nextChallengeUnlock,
     firstActiveQuest.quest)


def getQuestsRefreshTime(quests, challenges):
    quests = sorted(quests, key=lambda q: (q.isCompleted(), q.getStartTime(), int(q.getID().split(':')[2])))
    challenges = sorted(challenges, key=lambda c: (c.isCompleted(), c.getStartTime()))
    nextQuestUnlock = None
    nextChallengeUnlock = None
    now = getCurrentLocalServerTimestamp()
    for quest in quests:
        if now < quest.getStartTime() and not nextQuestUnlock:
            nextQuestUnlock = quest.getStartTimeLeft()
            break

    for challenge in challenges:
        if now < challenge.getStartTime() and not nextChallengeUnlock:
            nextChallengeUnlock = challenge.getStartTimeLeft()
            break

    return (nextQuestUnlock, nextChallengeUnlock)


def getQuestsFinishTimeLeft(quests, challenges):
    quests = sorted(quests, key=lambda q: (q.isCompleted(), q.getStartTime(), int(q.getID().split(':')[2])))
    challenges = sorted(challenges, key=lambda c: (c.isCompleted(), c.getStartTime()))
    currentQuestFinish = 0
    currentChallengeFinish = 0
    if not quests or not challenges:
        return (currentQuestFinish, currentChallengeFinish)
    now = getCurrentLocalServerTimestamp()
    quest = quests[-1]
    challenge = challenges[-1]
    if quest and quest.getStartTime() < now < quest.getFinishTime() and not currentQuestFinish:
        currentQuestFinish = quest.getFinishTimeLeft()
    if challenge and challenge.getStartTime() < now < challenge.getFinishTime() and not currentChallengeFinish:
        currentChallengeFinish = challenge.getFinishTimeLeft()
    return (currentQuestFinish, currentChallengeFinish)


def getPlayerOnlineStatus(player):
    if not player:
        return PlayerOnlineStatus.OFFLINE
    if player.getClientInfo() and player.getClientInfo().arenaLabel:
        return PlayerOnlineStatus.IN_BATTLE
    return PlayerOnlineStatus.ONLINE if player.isOnline() else PlayerOnlineStatus.OFFLINE


@dependency.replace_none_kwargs(birthdayController=ITanksBirthdayController)
def getIsPlayerWaitResponse(playerID, birthdayController=None):
    return playerID in birthdayController.getWaitResponsePlayers()
