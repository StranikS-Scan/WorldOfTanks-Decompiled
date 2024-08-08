# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wot_anniversary/tooltips/random_reward_tooltip.py
from collections import defaultdict
from typing import List, Dict
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.tooltips.random_reward_tooltip_model import RandomRewardTooltipModel
from gui.impl.pub import ViewImpl
from gui.server_events.bonuses import getNonQuestBonuses, CustomizationsBonus
from gui.shared.money import Currency
from gui.wot_anniversary.bonuses import getWotAnniversaryBonusPacker, SetOfCustomizationBonus
BONUS_ORDER = ('tokens',
 'goodies',
 Currency.CREDITS,
 'items',
 'customizations',
 Currency.EVENT_COIN)

class RandomRewardTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.tooltips.RandomRewardTooltip(), model=RandomRewardTooltipModel(), args=args, kwargs=kwargs)
        super(RandomRewardTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RandomRewardTooltip, self).getViewModel()

    def _onLoading(self, groupsBonusData, *args, **kwargs):
        super(RandomRewardTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__packRewards(groupsBonusData, model.getRewards(), getWotAnniversaryBonusPacker())

    def __packRewards(self, groupsBonusData, rewardsModel, packer):
        rewardsModel.clear()
        bonuses = self.__filterCustomization(self.__parseBonusesWithProbabilities(groupsBonusData))
        for bonus, probability in sorted(bonuses, key=self.__getSortKey, reverse=True):
            if bonus.isShowInGUI():
                bonusList = packer.pack(bonus)
                for bIndex, bModel in enumerate(bonusList):
                    bModel.setIndex(bIndex)
                    bModel.setProbability(probability)
                    rewardsModel.addViewModel(bModel)

        rewardsModel.invalidate()

    def __parseBonusesWithProbabilities(self, data):
        bonuses = []
        for groupData in data:
            if 'oneof' in groupData:
                oneOf = groupData['oneof']
                if oneOf and len(oneOf) == 2:
                    _, items = oneOf
                    bonuses.extend(self.__readItems(items))
            if 'allof' in groupData:
                bonuses.extend(self.__readItems(groupData['allof']))
            if 'groups' in groupData:
                bonuses.extend(self.__parseBonusesWithProbabilities(groupData['groups']))

        return bonuses

    @staticmethod
    def __filterCustomization(data):
        bonusesWithProbability = []
        customizationBonusesByProbability = defaultdict(list)
        for b, p in data:
            if isinstance(b, CustomizationsBonus):
                customizationBonusesByProbability[p].append(b)
            bonusesWithProbability.append((b, p))

        for p, bonuses in customizationBonusesByProbability.items():
            setCustomizations = defaultdict(lambda : [0, 0])
            for b in bonuses:
                for item in b.getCustomizations():
                    if item.get('custType') != 'projection_decal':
                        bonusesWithProbability.append((b, p))
                        continue
                    itemTypeName = b.getC11nItem(item).itemTypeName
                    setCustomizations[itemTypeName][0] = item.get('value', 0)
                    setCustomizations[itemTypeName][1] += 1

            for v in setCustomizations.items():
                bonusesWithProbability.append((SetOfCustomizationBonus(v), p))

        return bonusesWithProbability

    @staticmethod
    def __getSortKey(elem):
        bonus, probability = elem
        bonusName = bonus.getName()
        bonusOrder = BONUS_ORDER.index(bonusName) if bonusName in BONUS_ORDER else len(BONUS_ORDER) + 1
        return (probability, bonusOrder)

    @classmethod
    def __readItems(cls, data):
        bonuses = []
        for item in data:
            if item and len(item) == 4:
                probabilities, _, _, rawData = item
                if rawData:
                    bonuses.extend([ (b, cls.__roundProbability(p)) for b, p in zip([ b for k, v in rawData.iteritems() for b in getNonQuestBonuses(k, v) ], probabilities) ])

        return bonuses

    @staticmethod
    def __roundProbability(value):
        return 0 if value == -1 else int(round(value * 100, 2))
