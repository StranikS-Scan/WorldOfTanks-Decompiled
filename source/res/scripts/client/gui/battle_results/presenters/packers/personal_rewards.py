# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/personal_rewards.py
from gui.battle_results.presenters.packers.interfaces import IBattleResultsPacker
from gui.battle_results.pbs_helpers.economics import hasAogasFine
from gui.impl.gen.view_models.views.lobby.battle_results.reward_item_model import RewardItemModel

class PersonalRewards(IBattleResultsPacker):
    __slots__ = ()
    _AVAILABLE_REWARDS = []
    _ITEM_MODEL_CLS = RewardItemModel
    _REWARD_GETTERS = {}
    _REWARDS_TO_CONDITION_MAP = {}

    @classmethod
    def packModel(cls, model, battleResults):
        model.clear()
        reusable = battleResults.reusable
        shownRewards = cls._getShownRewards(reusable)
        for rewardType, rewardValue in shownRewards:
            item = cls._ITEM_MODEL_CLS()
            item.setType(rewardType.value)
            item.setValue(rewardValue)
            model.addViewModel(item)

        model.invalidate()

    @classmethod
    def _getAllRewardValues(cls, reusable):
        rewardValues = {}
        for rewardType in cls._AVAILABLE_REWARDS:
            getter = cls._REWARD_GETTERS.get(rewardType)
            if getter is None:
                continue
            value = getter(reusable)
            rewardValues[rewardType] = value

        return rewardValues

    @classmethod
    def _getShownRewards(cls, reusable):
        shownRewards = []
        rewardValues = cls._getAllRewardValues(reusable)
        hasFines = cls._hasFines(reusable)
        for rewardType in cls._AVAILABLE_REWARDS:
            value = rewardValues.get(rewardType)
            if value is None:
                continue
            condition = cls._REWARDS_TO_CONDITION_MAP.get(rewardType)
            if condition is not None and not condition(value, hasFines, rewardValues, reusable):
                continue
            shownRewards.append((rewardType, value))

        return shownRewards

    @classmethod
    def _hasFines(cls, reusable):
        return reusable.personal.avatar.hasPenalties() or hasAogasFine(reusable)
