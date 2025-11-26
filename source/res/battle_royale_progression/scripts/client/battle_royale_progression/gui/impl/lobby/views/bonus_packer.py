# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/gui/impl/lobby/views/bonus_packer.py
import typing
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from gui.battle_pass.battle_pass_bonuses_packers import getBattlePassBonusPacker
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.conditions.condition_group_model import ConditionGroupModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.server_events.formatters import COMPLEX_TOKEN
from gui.server_events.bonuses import mergeBonuses, splitBonuses
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.shared.missions.packers.bonus import SimpleBonusUIPacker, getLocalizedBonusName, TokenBonusUIPacker, BattlePassPointsBonusPacker
from gui.shared.missions.packers.conditions import CONDITION_GROUP_AND, CONDITION_GROUP_OR
from gui.shared.missions.packers.events import findFirstConditionModel, getEventUIDataPacker
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import List, Union
    from gui.server_events.bonuses import CurrenciesBonus
    from gui.shared.missions.packers.bonus import BonusUIPacker
    from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel

class ExtendedCurrencyBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setUserName(getLocalizedBonusName(bonus.getName()))
        model.setBigIcon(bonus.getName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class CurrenciesBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = getLocalizedBonusName(bonus.getCode())
        return [cls._packSingleBonus(bonus, label if label else '')]

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getCode())
        model.setIsCompensation(bonus.isCompensation())
        return model

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(bonus.getValue()))
        model.setLabel(label)
        model.setUserName(label)
        model.setBigIcon(bonus.getName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class BRBattlePassPointsBonusPacker(BattlePassPointsBonusPacker):

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(BRBattlePassPointsBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setUserName(getLocalizedBonusName(bonus.getName()))
        return model


BR_PROGRESSION_TOKEN = 'BRProgressionToken'

class BRTokenBonusUIPacker(TokenBonusUIPacker):
    _brProgressionController = dependency.descriptor(IBRProgressionOnTokensController)

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if tokenID.startswith(cls._brProgressionController.progressionToken):
            return BR_PROGRESSION_TOKEN
        super(BRTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def _getTooltipsPackers(cls):
        pakers = super(BRTokenBonusUIPacker, cls)._getTooltipsPackers()
        pakers.update({BR_PROGRESSION_TOKEN: cls.__getBRProgressionTooltip})
        return pakers

    @classmethod
    def __getBRProgressionTooltip(cls, *_):
        tokenBase = R.strings.battle_royale_progression.quests.bonuses.progressionToken
        return createTooltipData(makeTooltip(backport.text(tokenBase.header()), backport.text(tokenBase.body())))

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(BRTokenBonusUIPacker, cls)._getTokenBonusPackers()
        complexPaker = tokenBonusPackers.get(COMPLEX_TOKEN)
        tokenBonusPackers.update({BR_PROGRESSION_TOKEN: complexPaker})
        return tokenBonusPackers


def getBonusPacker():
    packer = getBattlePassBonusPacker()
    currencyBonusUIPacker = ExtendedCurrencyBonusUIPacker()
    tokenBonusPacker = BRTokenBonusUIPacker()
    packer.getPackers().update({'currencies': CurrenciesBonusUIPacker(),
     Currency.CREDITS: currencyBonusUIPacker,
     Currency.CRYSTAL: currencyBonusUIPacker,
     Currency.EQUIP_COIN: currencyBonusUIPacker,
     'token': tokenBonusPacker,
     'battleToken': tokenBonusPacker,
     'battlePassPoints': BRBattlePassPointsBonusPacker()})
    return packer


def packQuestBonuses(bonuses, bonusPacker, order=None):
    packedBonuses = []
    packedToolTips = []
    bonuses = mergeBonuses(bonuses)
    bonuses = splitBonuses(bonuses)
    if order is not None:
        bonuses.sort(key=_getSortKey(order))
    for bonus in bonuses:
        if bonus.isShowInGUI():
            packedBonuses.extend(bonusPacker.pack(bonus))
            packedToolTips.extend(bonusPacker.getToolTip(bonus))

    return (packedBonuses, packedToolTips)


def _getSortKey(order):

    def getSortKey(bonus):
        bonusName = bonus.getName()
        try:
            return order.index(bonusName)
        except ValueError:
            return len(order)

    return getSortKey


def getFirstConditionModelFromQuestModel(dailyQuestModel):
    postBattleModel = findFirstConditionModel(dailyQuestModel.postBattleCondition)
    bonusConditionModel = findFirstConditionModel(dailyQuestModel.bonusCondition)
    if postBattleModel and bonusConditionModel:
        if postBattleModel.getTotal() > 0:
            return postBattleModel
        return bonusConditionModel
    return postBattleModel or bonusConditionModel


def _buildDescription(conditionalModel):
    items = conditionalModel.getItems()
    descriptions = []
    for item in items:
        if isinstance(item, ConditionGroupModel):
            descriptions.append(_buildDescription(item))
        descriptions.append(item.getDescrData())

    if conditionalModel.getConditionType() == CONDITION_GROUP_AND:
        separator = ' {} '.format(backport.text(R.strings.quests.dailyQuests.postBattle.conditionTypeAnd()))
        result = separator.join(descriptions)
    elif conditionalModel.getConditionType() == CONDITION_GROUP_OR:
        separator = ' {} '.format(backport.text(R.strings.quests.dailyQuests.postBattle.conditionTypeOr()))
        result = separator.join(descriptions)
    else:
        result = descriptions[0] if descriptions else ''
    return result


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def packMissionItem(model, raw, questPacker=None, eventsCache=None):

    def setDescription(viewModel, questModel):
        condinionalModel = questModel.postBattleCondition if questModel.postBattleCondition.getItems() else questModel.bonusCondition
        result = _buildDescription(condinionalModel)
        viewModel.setDescription(result)

    def setProgress(viewModel, questModel):
        progressModel = getFirstConditionModelFromQuestModel(questModel)
        viewModel.setCurrentProgress(progressModel.getCurrent())
        viewModel.setTotalProgress(progressModel.getTotal())
        viewModel.setEarned(progressModel.getEarned())

    questUIPacker = questPacker(raw) if questPacker else getEventUIDataPacker(raw)
    fullQuestModel = questUIPacker.pack()
    isCompleted = fullQuestModel.getStatus().value == MISSIONS_STATES.COMPLETED
    model.setIsCompleted(isCompleted)
    model.setAnimateCompletion(eventsCache.questsProgress.getQuestCompletionChanged(raw.getID()))
    model.setIcon(fullQuestModel.getIcon())
    preFormattedConditionModel = getFirstConditionModelFromQuestModel(fullQuestModel)
    if preFormattedConditionModel:
        setDescription(model, fullQuestModel)
        setProgress(model, fullQuestModel)
    fullQuestModel.unbind()
    return (isCompleted, model.getCurrentProgress())
