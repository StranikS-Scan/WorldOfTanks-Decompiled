# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/missions/packers/events.py
import logging
import typing
import constants
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getMissionInfoData
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
from gui.impl.gen.view_models.common.missions.daily_quest_model import DailyQuestModel
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel
from gui.impl.gen.view_models.views.lobby.rts.rts_quest_model import RtsQuestModel, GameMode as RtsQuestGameMode
from gui.impl.lobby.rts.rts_bonuses_packers import getRTSBonusPacker
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.events_helpers import isPremium, isDailyQuest, isRts
from gui.server_events.formatters import DECORATION_SIZES
from gui.shared.missions.packers.bonus import getDefaultBonusPacker, packBonusModelAndTooltipData, BonusUIPacker
from gui.shared.missions.packers.conditions import BonusConditionPacker
from gui.shared.missions.packers.conditions import PostBattleConditionPacker
from helpers import dependency
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.server_events import IEventsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import ServerEventAbstract
    from gui.server_events.bonuses import SimpleBonus
    from gui.server_events.conditions import BattleResults
_logger = logging.getLogger(__name__)
DEFAULT_AWARDS_COUNT = 10
DAILY_QUEST_AWARDS_COUNT = 1000

class _EventUIDataPacker(object):

    def __init__(self, event):
        self._event = event

    def pack(self, model=None):
        raise SoftException('This function should be overriden.')

    def _packModel(self, model):
        self._packEvent(model)

    def _packEvent(self, model):
        with model.transaction() as ts:
            ts.setId(self._event.getID())
            ts.setGroupId(self._event.getGroupID())
            ts.setType(self._event.getType())
            ts.setTitle(self._event.getUserName())
            ts.setDescription(self._event.getDescription())
            ts.setStatus(self._getStatus())
            ts.setDecoration(self._event.getIconID())
        return model

    def _getStatus(self):
        if self._event.isCompleted():
            return MISSIONS_STATES.COMPLETED
        return MISSIONS_STATES.NONE if self._event.isAvailable()[0] else MISSIONS_STATES.NOT_AVAILABLE


class BattleQuestUIDataPacker(_EventUIDataPacker):

    def __init__(self, event, bonusFormatter=CurtailingAwardsComposer(DEFAULT_AWARDS_COUNT)):
        super(BattleQuestUIDataPacker, self).__init__(event)
        self._tooltipData = {}
        self._bonusFormatter = bonusFormatter

    def pack(self, model=None):
        if model is not None and not isinstance(model, QuestModel):
            _logger.error("Provided model type doesn't match the required quest type. Expected QuestModel")
            return
        else:
            model = model if model is not None else QuestModel()
            self._packModel(model)
            return model

    def getTooltipData(self):
        return self._tooltipData

    @staticmethod
    def getBonusPacker():
        return getDefaultBonusPacker()

    def _packModel(self, model):
        super(BattleQuestUIDataPacker, self)._packModel(model)
        self._packBonuses(model)
        self._packPostBattleConds(model)
        self._packBonusConds(model)
        self._packDefaultConds(model)
        self._setCompletionCounts(model)

    def _packBonuses(self, model):
        packer = self.getBonusPacker()
        self._tooltipData = {}
        packQuestBonusModelAndTooltipData(packer, model.getBonuses(), self._event, tooltipData=self._tooltipData)

    def _packPostBattleConds(self, model):
        postBattleContitionPacker = PostBattleConditionPacker()
        postBattleContitionPacker.pack(self._event, model.postBattleCondition)

    def _packBonusConds(self, model):
        bonusConditionPacker = BonusConditionPacker()
        bonusConditionPacker.packWithPostBattleCondCheck(self._event, model.bonusCondition, bool(model.postBattleCondition.getItems()))

    @staticmethod
    def _packDefaultConds(model):
        if not model.bonusCondition.getItems() and not model.postBattleCondition.getItems():
            postBattleContitionPacker = PostBattleConditionPacker()
            postBattleContitionPacker.packDefaultCondition(model.postBattleCondition)

    def _setCompletionCounts(self, model):
        bonusConditions = getattr(self._event, 'bonusCond', None)
        getBonusCount = getattr(self._event, 'getBonusCount', None)
        if not bonusConditions or not getBonusCount:
            return
        else:
            bonusLimit = bonusConditions.getBonusLimit()
            bonusCount = min(getBonusCount(), bonusLimit)
            model.setTotalCount(bonusLimit)
            model.setCompletedCount(bonusCount)
            return


class TokenUIDataPacker(_EventUIDataPacker):

    def pack(self, model=None):
        if model is not None and not isinstance(model, QuestModel):
            _logger.error("Provided model type doesn't match the required quest type. Expected QuestModel")
            return
        else:
            model = model if model is not None else QuestModel()
            self._packModel(model)
            return model


class PrivateMissionUIDataPacker(_EventUIDataPacker):
    pass


class DailyQuestUIDataPacker(BattleQuestUIDataPacker):
    eventsCache = dependency.descriptor(IEventsCache)

    def pack(self, model=None):
        if model is not None and not isinstance(model, DailyQuestModel):
            _logger.error("Provided model type doesn't match the required quest type. Expected DailyQuestModel")
            return
        else:
            model = model if model is not None else DailyQuestModel()
            self._packModel(model)
            self.__resolveQuestIcon(model)
            return model

    @staticmethod
    def getFirstAvailableCondition(model):
        postBattleModel = findFirstConditionModel(model.postBattleCondition)
        bonusConditionModel = findFirstConditionModel(model.bonusCondition)
        return postBattleModel if postBattleModel else bonusConditionModel

    def __resolveQuestIcon(self, model):
        iconId = self._event.getIconID()
        if iconId is not None and iconId > 0:
            prefetcher = self.eventsCache.prefetcher
            questIcon = prefetcher.getMissionDecoration(iconId, DECORATION_SIZES.DAILY)
            if not questIcon:
                _logger.error('Failed to prefetch daily quest icon from uiDecorator %s', str(iconId))
        else:
            conditionModel = getQuestConditionModel(model)
            if conditionModel is None:
                _logger.warning('No condition found. Unable to define quest icon.')
                return
            questIcon = conditionModel.getIconKey()
        model.setIcon(questIcon)
        return


class RtsQuestUIDataPacker(DailyQuestUIDataPacker):
    _rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, event, bonusFormatter=CurtailingAwardsComposer(DEFAULT_AWARDS_COUNT), tooltipData=None):
        super(RtsQuestUIDataPacker, self).__init__(event, bonusFormatter)
        if tooltipData is not None:
            self._tooltipData = tooltipData
        return

    def pack(self, model=None):
        if model is not None and not isinstance(model, RtsQuestModel):
            _logger.error("Provided model type doesn't match the required quest type. Expected RtsQuestModel")
            return
        else:
            model = model if model is not None else RtsQuestModel()
            model = super(RtsQuestUIDataPacker, self).pack(model)
            self._packCondition(model)
            model.setGameMode(self._getQuestType())
            startDate = self._event.getStartTime() if self._event.getStartTimeLeft() > 0 else 0
            model.setStartDate(startDate)
            finishDate = self._event.getFinishTime() if self._event.getFinishTime() > 0 else 0
            model.setFinishDate(finishDate)
            return model

    @staticmethod
    def getBonusPacker():
        return getRTSBonusPacker()

    @staticmethod
    def getFirstAvailableCondition(model):
        return model.condition

    def _packBonuses(self, model):
        packQuestBonusModelAndTooltipData(self.getBonusPacker(), model.getBonuses(), self._event, self.getTooltipData())

    def _getQuestType(self):
        conditions = self._event.postBattleCond.getConditions().findAll('results')
        for condition in conditions:
            if condition.keyName == 'isCommander' and condition.relationValue:
                return RtsQuestGameMode.STRATEGIST

        return RtsQuestGameMode.TANKER

    def _packCondition(self, model):
        conditionModel = getQuestConditionModel(model)
        if conditionModel is not None:
            condition = model.condition
            condition.setCurrent(conditionModel.getCurrent())
            condition.setEarned(conditionModel.getEarned())
            condition.setTotal(conditionModel.getTotal())
            condition.setTitleData(conditionModel.getTitleData())
            condition.setDescrData(conditionModel.getDescrData())
        return

    def getConditionTooltipData(self, tooltipData):
        conditions = self._event.bonusCond.getConditions().findAll('cumulative')
        for condition in conditions:
            if condition.keyName == 'rtsEventPoints':
                questType = self._getQuestType()
                questId = self._event.getID()
                if questType == RtsQuestGameMode.STRATEGIST:
                    battleEconomics = self._rtsController.getBattleEconomics()
                    args = {'win': battleEconomics.get('win').get('strategistPointsIncome'),
                     'defeat': battleEconomics.get('defeat').get('strategistPointsIncome')}
                    tooltipData[questId] = (R.strings.rts_battles.metaQuests.tooltips.eventPointsStrategist.body(), args)
                else:
                    tooltipData[questId] = (R.strings.rts_battles.metaQuests.tooltips.eventPointsTanker.body(),)


def packQuestBonusModel(quest, packer, array):
    bonuses = quest.getBonuses()
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            for idx, item in enumerate(bonusList):
                item.setIndex(idx)
                array.addViewModel(item)


def packQuestBonusModelAndTooltipData(packer, array, quest, tooltipData=None, questBonuses=None):
    bonuses = quest.getBonuses() if questBonuses is None else questBonuses
    packBonusModelAndTooltipData(bonuses, packer, array, tooltipData)
    return


def preformatEventBonuses(event, bonusFormatter=CurtailingAwardsComposer(DEFAULT_AWARDS_COUNT)):
    bonuses = getMissionInfoData(event).getSubstituteBonuses()
    return bonusFormatter.getFormattedBonuses(bonuses, size=AWARDS_SIZES.BIG)


def getEventUIDataPacker(event):
    if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
        return TokenUIDataPacker(event)
    elif event.getType() == constants.EVENT_TYPE.PERSONAL_QUEST:
        return PrivateMissionUIDataPacker(event)
    elif isPremium(event.getID()) or isDailyQuest(event.getID()):
        return DailyQuestUIDataPacker(event)
    elif isRts(event.getID()):
        return RtsQuestUIDataPacker(event)
    else:
        return BattleQuestUIDataPacker(event) if event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS else None


def findFirstConditionModel(root):
    if not hasattr(root, 'getItems'):
        return root
    else:
        for item in root.getItems():
            return findFirstConditionModel(item)

        return None


def getQuestConditionModel(model):
    conditionModel = findFirstConditionModel(model.bonusCondition)
    if conditionModel is None:
        conditionModel = findFirstConditionModel(model.postBattleCondition)
    return conditionModel
