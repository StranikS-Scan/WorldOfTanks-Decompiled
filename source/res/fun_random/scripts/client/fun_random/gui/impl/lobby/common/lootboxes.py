# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/common/lootboxes.py
import typing
from constants import LOOTBOX_TOKEN_PREFIX
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_lootbox import FunRandomLootbox
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.lobby.awards.packers import MultiAwardVehiclesBonusUIPacker
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.server_events.bonuses import getNonQuestBonuses, CreditsBonus, GoldBonus, CrystalBonus
from gui.shared.missions.packers.bonus import TokenBonusUIPacker
from gui.shared.money import Money, Currency
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus
FEP_CATEGORY = 'FEPLootBoxes'

class FunRandomLootBoxTypes(object):
    ORDINARY = 'fep_ordinary'
    UNUSUAL = 'fep_unusual'
    RARE = 'fep_rare'
    EPIC = 'fep_epic'
    LEGENDARY = 'fep_legendary'
    ALL = (ORDINARY,
     UNUSUAL,
     RARE,
     EPIC,
     LEGENDARY)
    ORDERED = tuple(reversed(ALL))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def sortTokenFunc(token, itemsCache=IItemsCache):
    if token.id.startswith(LOOTBOX_TOKEN_PREFIX):
        lootBox = itemsCache.items.tokens.getLootBoxByTokenID(token.id)
        if lootBox and lootBox.getType() in FunRandomLootBoxTypes.ORDERED:
            return FunRandomLootBoxTypes.ORDERED.index(lootBox.getType())


class FunRandomLootBoxTokenBonusPacker(TokenBonusUIPacker, FunAssetPacksMixin):
    itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _pack(cls, bonus):
        result = super(FunRandomLootBoxTokenBonusPacker, cls)._pack(bonus)
        for token in sorted(bonus.getTokens().itervalues(), key=sortTokenFunc):
            if cls.__isSuitable(token.id, token):
                model = TokenBonusModel()
                cls._packCommon(bonus, model)
                cls.__packLootBox(token.id, model, bonus)
                result.append(model)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(FunRandomLootBoxTokenBonusPacker, cls)._getToolTip(bonus)
        for token in sorted(bonus.getTokens().itervalues(), key=sortTokenFunc):
            if cls.__isSuitable(token.id, token):
                result.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[token.id]))

        return result

    @classmethod
    def _getContentId(cls, bonus):
        result = super(FunRandomLootBoxTokenBonusPacker, cls)._getContentId(bonus)
        for token in sorted(bonus.getTokens().itervalues(), key=sortTokenFunc):
            if cls.__isSuitable(token.id, token):
                result.append(R.views.fun_random.lobby.tooltips.FunRandomLootBoxTooltipView())

        return result

    @classmethod
    def _getIconPath(cls, iconSize, rarity):
        return cls.getModeIconsResRoot().progression.bonuses.dyn(iconSize).dyn(rarity)()

    @classmethod
    def __packLootBox(cls, tokenID, model, bonus):
        lootBox = cls.itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
        rarity = lootBox.getType().split('_')[-1]
        model.setIconSmall(backport.image(cls._getIconPath(AWARDS_SIZES.SMALL, rarity)))
        model.setIconBig(backport.image(cls._getIconPath(AWARDS_SIZES.BIG, rarity)))
        model.setLabel(backport.text(cls.getModeLocalsResRoot().lootbox.dyn(lootBox.getType())()))
        model.setValue(str(bonus.getValue().get(tokenID, {}).get('count', 0)))
        return model

    @classmethod
    def __isSuitable(cls, tokenID, token):
        return tokenID.startswith(LOOTBOX_TOKEN_PREFIX) and token.count >= 0 and cls.__isBoxAvailable(tokenID)

    @classmethod
    def __isBoxAvailable(cls, tokenID):
        lootBox = cls.itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
        return lootBox.getCategory() == FEP_CATEGORY if lootBox else False


class FunRandomRewardLootBoxTokenBonusPacker(FunRandomLootBoxTokenBonusPacker):

    @classmethod
    def _getIconPath(cls, iconSize, rarity):
        return cls.getModeIconsResRoot().library.bonuses.dyn(iconSize).dyn(rarity)()


class FunRandomLootBoxVehiclesBonusUIPacker(MultiAwardVehiclesBonusUIPacker):
    COMPENSATION_BONUSES_MAP = {Currency.CREDITS: CreditsBonus,
     Currency.GOLD: GoldBonus,
     Currency.CRYSTAL: CrystalBonus}

    @classmethod
    def _getVehicleCompensationTooltipContent(cls):
        return R.views.lobby.awards.tooltips.RewardCompensationTooltip()

    @classmethod
    def _getCompensation(cls, vehicle, bonus):
        bonuses = []
        for bVehicle, vehInfo in bonus.getVehicles():
            compensation = vehInfo.get('customCompensation')
            if compensation is not None and vehicle == bVehicle and vehicle.isInInventory:
                money = Money(*compensation)
                for currency, value in money.iteritems():
                    if value:
                        bonusCls = cls.COMPENSATION_BONUSES_MAP[currency]
                        bonuses.append(bonusCls(currency, value, isCompensation=True, compensationReason=bonus))

        return bonuses


def packLootboxes(lootboxes, lbConfig, lootboxesModel, packer, visibleLBAwardsNames, localeRes, tooltips=None):
    lootboxesModel.clear()
    for lb in lootboxes:
        lootBoxData = lbConfig.get(lb.getID())
        if lootBoxData:
            lootboxModel = FunRandomLootbox()
            lootboxModel.setLabel(backport.text(localeRes.lootbox.dyn(lb.getType())()))
            lootboxType = lb.getType()
            lootboxModel.setIconKey(lootboxType.split('_')[-1])
            lootboxModel.setShowRewardsNames(lootboxType in visibleLBAwardsNames)
            lootboxesModel.addViewModel(lootboxModel)
            packLootboxRewards(lootBoxData, lootboxModel.getRewards(), packer, tooltips)

    lootboxesModel.invalidate()


def packLootboxRewards(lootBoxData, rewardsModel, packer, tooltipData=None):
    rewardsModel.clear()
    if lootBoxData:
        bonusIndexTotal = 0
        if tooltipData is not None:
            bonusIndexTotal = len(tooltipData)
        items = []
        for data in parseBonusesWithProbabilities(lootBoxData):
            for bonus, probability in zip(data['bonuses'], data['probabilities']):
                if bonus.isShowInGUI():
                    bonusList = packer.pack(bonus)
                    bonusTooltipList = []
                    bonusContentIdList = []
                    if bonusList and tooltipData is not None:
                        bonusTooltipList = packer.getToolTip(bonus)
                        bonusContentIdList = packer.getContentId(bonus)
                    for bonusIndex, item in enumerate(bonusList):
                        item.setIndex(bonusIndex)
                        probability = 0 if probability == -1 else int(round(probability * 100, 2))
                        item.setProbability(probability)
                        if tooltipData is not None:
                            tooltipIdx = str(bonusIndexTotal)
                            item.setTooltipId(tooltipIdx)
                            if bonusTooltipList:
                                tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                            if bonusContentIdList:
                                item.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
                            bonusIndexTotal += 1
                        items.append(item)

        for item in sorted(items, key=lambda i: i.getProbability()):
            rewardsModel.addViewModel(item)

    rewardsModel.invalidate()
    return


def parseBonusesWithProbabilities(data):
    groups = data.get('groups', [])
    bonuses = []
    for groupData in groups:
        oneOf = groupData.get('oneof', ())
        if oneOf and len(oneOf) == 2:
            _, items = oneOf
            for item in items:
                if item and len(item) == 4:
                    probabilities, _, _, rawData = item
                    if rawData:
                        rawDataBonuses = []
                        for k, v in rawData.iteritems():
                            rawDataBonuses.extend(getNonQuestBonuses(k, v))

                        bonuses.append({'probabilities': probabilities,
                         'bonuses': rawDataBonuses})

    return bonuses
