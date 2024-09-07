# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_bonuses_packers.py
import logging
from contextlib import contextmanager
import typing
from battle_pass_common import BATTLE_PASS_Q_CHAIN_BONUS_NAME, BATTLE_PASS_RANDOM_QUEST_BONUS_NAME, BATTLE_PASS_SELECT_BONUS_NAME, BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift, getSingleVehicleForCustomization, getStyleForChapter
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.token_bonus_model import TokenBonusModel
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.impl.gen.view_models.views.lobby.battle_pass.vehicle_bonus_model import VehicleBonusModel
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, CREW_BONUS_X3_TOKEN
from gui.server_events.bonuses import BlueprintsBonusSubtypes
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, BaseBonusUIPacker, BlueprintBonusUIPacker, BonusUIPacker, CrewBookBonusUIPacker, DossierBonusUIPacker, GoodiesBonusUIPacker, ItemBonusUIPacker, SimpleBonusUIPacker, TokenBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPackersMap
from gui.shared.money import Currency
from helpers import dependency
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from shared_utils import first
from skeletons.gui.game_control import IBattlePassController, ISpecialSoundCtrl
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import BattlePassQuestChainTokensBonus, BattlePassRandomQuestTokensBonus, SimpleBonus, TmanTemplateTokensBonus, CustomizationsBonus, PlusPremiumDaysBonus, DossierBonus, BattlePassSelectTokensBonus, BattlePassStyleProgressTokenBonus, VehicleBlueprintBonus, GoodiesBonus
    from account_helpers.offers.events_data import OfferEventData, OfferGift
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.goodies.goodie_items import Booster
    from gui.server_events.bonuses import TokensBonus
_logger = logging.getLogger(__name__)

def getBattlePassBonusPacker():
    mapping = getDefaultBonusPackersMap()
    currencyBonusUIPacker = ExtendedCurrencyBonusUIPacker()
    mapping.update({'berths': BattlePassBerthsBonusPacker(),
     'blueprints': BattlePassBlueprintsBonusPacker(),
     'crewBooks': ExtendedCrewBookBonusUIPacker(),
     'customizations': BattlePassCustomizationsBonusPacker(),
     'dossier': BattlePassDossierBonusPacker(),
     'freeXP': BattlePassFreeXPPacker(),
     'goodies': BattlePassGoodiesBonusPacker(),
     'items': ExtendedItemBonusUIPacker(),
     'premium_plus': BattlePassPremiumDaysPacker(),
     'slots': BattlePassSlotsBonusPacker(),
     'tmanToken': TmanTemplateBonusPacker(),
     'tokens': BattlePassTokenBonusPacker(),
     'vehicles': BattlePassVehiclesBonusUIPacker(),
     BATTLE_PASS_Q_CHAIN_BONUS_NAME: QuestChainBonusPacker(),
     BATTLE_PASS_RANDOM_QUEST_BONUS_NAME: RandomQuestBonusPacker(),
     BATTLE_PASS_SELECT_BONUS_NAME: SelectBonusPacker(),
     BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME: BattlePassStyleProgressTokenBonusPacker(),
     Currency.BPCOIN: CoinBonusPacker(),
     Currency.CREDITS: currencyBonusUIPacker,
     Currency.CRYSTAL: currencyBonusUIPacker,
     Currency.GOLD: currencyBonusUIPacker,
     Currency.EQUIP_COIN: currencyBonusUIPacker})
    return BonusUIPacker(mapping)


def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None, packer=None):
    if packer is None:
        packer = getBattlePassBonusPacker()
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            bonusContentIdList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
                bonusContentIdList = packer.getContentId(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusModelsList.addViewModel(item)
                if tooltipData is not None:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    if bonusTooltipList:
                        tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    if bonusContentIdList:
                        item.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
                    bonusIndexTotal += 1

    return


def packSpecialTooltipData(specialReward, specialRewardItems, *args):
    specialRewardItems[specialReward] = TooltipData(tooltip=None, isSpecial=True, specialAlias=specialReward, specialArgs=args)
    return


def changeBonusTooltipData(bonusData, tooltipData):
    packer = getBattlePassBonusPacker()
    for bonus, tooltipId in bonusData:
        tooltip = first(packer.getToolTip(bonus))
        tooltipData[tooltipId] = tooltip


class _BattlePassFinalBonusPacker(BaseBonusUIPacker):
    __isBigImageUsed = False

    @classmethod
    def setIsBigAward(cls, isBig):
        cls.__isBigImageUsed = isBig

    @classmethod
    def _injectAwardID(cls, item, postfix=None):
        if cls.__isBigImageUsed and postfix:
            item.setIcon('_'.join([item.getIcon(), postfix]))


class TmanTemplateBonusPacker(_BattlePassFinalBonusPacker):
    __battlePass = dependency.descriptor(IBattlePassController)
    __specialSounds = dependency.descriptor(ISpecialSoundCtrl)

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls._packTmanTemplateToken(tokenID, bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            groupName = recruitInfo.getGroupName()
            bonusImageName = '_'.join([cls.__getBonusImageName(recruitInfo), groupName])
            tankManFullName = recruitInfo.getFullUserName()
            model = RewardItemModel()
            cls._packCommon(bonus, model)
            model.setIcon(bonusImageName)
            model.setUserName(tankManFullName)
            model.setLabel(tankManFullName)
            model.setBigIcon(bonusImageName)
            model.setIsCollectionEntity(cls._isCollectionItem(groupName))
            cls._injectAwardID(model, recruitInfo.getGroupName())
            return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def __getBonusImageName(cls, recruitInfo):
        baseName = 'tank{}man'.format('wo' if recruitInfo.isFemale() else '')
        return baseName


class BattlePassCustomizationsBonusPacker(_BattlePassFinalBonusPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item, data in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None:
                continue
            result.append(cls._packSingleBonus(bonus, item, data))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, data):
        model = cls._createBonusModel()
        cls._packCommon(bonus, model)
        customizationItem = bonus.getC11nItem(item)
        iconName = customizationItem.itemTypeName
        if iconName == 'style':
            if customizationItem.modelsSet:
                iconName = 'style_3d'
            elif customizationItem.isQuestsProgression:
                iconName = 'progressionStyle'
        bigIcon = '_'.join([iconName, str(customizationItem.intCD)])
        if not R.images.gui.maps.icons.battlePass.rewards.dyn(bigIcon).exists():
            bigIcon = iconName
        model.setValue(str(data.get('value', '')))
        model.setIcon(iconName)
        model.setBigIcon(bigIcon)
        model.setUserName(cls._getUserName(customizationItem))
        model.setLabel(cls._getLabel(customizationItem))
        model.setIsCollectionEntity(cls._isCollectionItem(customizationItem.intCD))
        cls._injectAwardID(model, str(customizationItem.intCD))
        return model

    @classmethod
    def _createBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for item, _ in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None:
                continue
            itemCustomization = bonus.getC11nItem(item)
            specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM_AWARD
            specialArgs = CustomizationTooltipContext(itemCD=itemCustomization.intCD)
            if itemCustomization.itemTypeName in ('camouflage', 'style'):
                vehicle = getSingleVehicleForCustomization(itemCustomization)
                if vehicle is not None:
                    specialAlias = TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM
                    specialArgs = CustomizationTooltipContext(itemCD=itemCustomization.intCD, vehicleIntCD=vehicle)
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=specialAlias, specialArgs=specialArgs))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for item, _ in zip(bonus.getCustomizations(), bonus.getList()):
            if item is not None:
                result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result

    @classmethod
    def _getLabel(cls, customizationItem):
        return customizationItem.userName

    @classmethod
    def _getUserName(cls, customizationItem):
        return customizationItem.userName


class BattlePassPremiumDaysPacker(BaseBonusUIPacker):
    _ICONS_AVAILABLE = (1, 2, 3, 7, 14, 30, 90, 180, 360)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        days = bonus.getValue()
        model = RewardItemModel()
        if days in cls._ICONS_AVAILABLE:
            model.setName(bonus.getName())
            model.setBigIcon('_'.join([bonus.getName(), str(days)]))
        else:
            model.setName('premium_universal')
            model.setBigIcon('premium_universal')
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(bonus.getValue()))
        model.setUserName(backport.text(R.strings.tooltips.awardItem.premium_plus.header()))
        return model


class BattlePassDossierBonusPacker(DossierBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for achievement in bonus.getAchievements():
            recordName = achievement.getRecordName()
            dossierIconName = achievement.getName()
            dossierValue = achievement.getValue()
            dossierNamePostfix = '_achievement'
            userName = achievement.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, dossierNamePostfix, dossierValue, userName, recordName))

        for badge in bonus.getBadges():
            dossierIconName = 'badge_' + str(badge.badgeID)
            dossierValue = 0
            dossierNamePostfix = '_badge'
            userName = badge.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, dossierNamePostfix, dossierValue, userName))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, dossierIconName, dossierNamePostfix, dossierValue, userName, recordName=None):
        model = RewardItemModel()
        model.setName(bonus.getName() + dossierNamePostfix)
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(dossierValue))
        model.setIcon(dossierIconName)
        model.setUserName(userName)
        model.setBigIcon(dossierIconName)
        model.setIsCollectionEntity(cls._isCollectionItem(recordName))
        return model


class SelectBonusPacker(BaseBonusUIPacker):
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = RewardItemModel()
        bonusType = bonus.getType()
        model.setName(bonus.getName())
        model.setValue(str(cls.getValue(bonus)))
        model.setIcon(bonusType)
        model.setBigIcon(bonusType)
        model.setUserName(backport.text(R.strings.battle_pass.selectBonus.dyn(bonusType)()))
        return model

    @classmethod
    def getValue(cls, bonus):
        giftTokenName = first(bonus.getTokens().keys())
        offer = cls.__offersProvider.getOfferByToken(getOfferTokenByGift(giftTokenName))
        if offer is None:
            return bonus.getCount()
        else:
            gift = first(offer.getAllGifts())
            return bonus.getCount() if gift is None else gift.giftCount * bonus.getCount()

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BATTLE_PASS_GIFT_TOKEN, specialArgs=[tokenID] + [bonus.getContext().get('isReceived', True)]))

        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        for _ in bonus.getTokens().iterkeys():
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result


class BattlePassStyleProgressTokenBonusPacker(_BattlePassFinalBonusPacker):
    _ICON_NAME_TEMPLATE = 'style_3d_{}'
    _STYLE_FIRST_LEVEL = 1
    _STYLE_MAX_LEVEL = 4
    _rStyleProgression = R.strings.battle_pass.styleProgression

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        chapter = bonus.getChapter()
        level = bonus.getLevel()
        customizationItem = getStyleForChapter(chapter)
        model.setIcon(cls._ICON_NAME_TEMPLATE.format(level))
        model.setOverlayType(ItemHighlightTypes.PROGRESSION_STYLE_UPGRADED + str(level))
        if customizationItem is not None:
            if level == cls._STYLE_FIRST_LEVEL:
                userName = backport.text(cls._rStyleProgression.newStyle(), styleName=customizationItem.userName)
            elif level == cls._STYLE_MAX_LEVEL:
                userName = backport.text(cls._rStyleProgression.finalLevel(), styleName=customizationItem.userName)
            else:
                userName = backport.text(cls._rStyleProgression.newLevel(), styleName=customizationItem.userName)
            model.setUserName(userName)
            postfix = str(customizationItem.id)
            model.setBigIcon('_'.join([cls._ICON_NAME_TEMPLATE.format(level), postfix]))
            model.setIsCollectionEntity(cls._isCollectionItem((customizationItem.intCD, level)))
        else:
            postfix = 'undefined'
        cls._injectAwardID(model, postfix)
        return model

    @classmethod
    def _isCollectionItem(cls, validationData):
        collectionItemID, level = validationData
        return super(BattlePassStyleProgressTokenBonusPacker, cls)._isCollectionItem(collectionItemID) and level == cls._STYLE_MAX_LEVEL

    @classmethod
    def _getToolTip(cls, bonus):
        chapter = bonus.getChapter()
        level = bonus.getLevel()
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[chapter, level])]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.battle_pass.tooltips.BattlePassUpgradeStyleTooltipView()]


class ExtendedItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = super(ExtendedItemBonusUIPacker, cls)._packSingleBonus(bonus, item, count)
        model.setUserName(item.userName)
        model.setItemType(item.itemTypeID)
        model.setBigIcon(item.name if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER else item.getGUIEmblemID())
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and item.isModernized:
            model.setOverlayType('{}_{}'.format(ItemHighlightTypes.MODERNIZED, item.level))
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class ExtendedCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = super(ExtendedCrewBookBonusUIPacker, cls)._packSingleBonus(bonus, item, count)
        model.setUserName(item.userName)
        model.setBigIcon(item.getBonusIconName())
        return model


class ExtendedCurrencyBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setUserName(str(bonus.getValue()))
        model.setBigIcon(bonus.getName())
        return model


class CoinBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(CoinBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setBigIcon(bonus.getName())
        model.setUserName(backport.text(R.strings.battle_pass.tooltips.battlePassCoins.title()))
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView()]


class QuestChainBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, None)]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardItemModel()
        model.setName(bonus.getName())
        model.setBigIcon(bonus.getName())
        model.setUserName(backport.text(R.strings.battle_pass.questChainBonus()))
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.battle_pass.tooltips.BattlePassQuestsChainTooltipView()]

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[bonus.tokenID])]


class RandomQuestBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, None)]

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardItemModel()
        model.setName(bonus.getName())
        model.setBigIcon(bonus.getName())
        model.setUserName(backport.text(R.strings.battle_pass.randomQuestBonus(), vehicle=bonus.vehicle.shortUserName if bonus.vehicle is not None else ''))
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.battle_pass.tooltips.RandomQuestTooltip()]

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[bonus.tokenID])]


class BattlePassSlotsBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(BattlePassSlotsBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setBigIcon(bonus.getName())
        model.setUserName(backport.text(R.strings.tooltips.awardItem.slots.header()))
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class BattlePassVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleBonusModel()
        cls.__fillVehicle(model, vehicle)
        model.setBigIcon('vehicle_' + str(vehicle.intCD))
        model.setName(bonus.getName())
        return model

    @classmethod
    def __fillVehicle(cls, model, vehicle):
        model.setIsElite(not vehicle.getEliteStatusProgress().toUnlock or vehicle.isElite)
        model.setVehicleLvl(vehicle.level)
        model.setVehicleName(vehicle.userName)
        model.setVehicleType(vehicle.type)


class BattlePassFreeXPPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(BattlePassFreeXPPacker, cls)._packSingleBonus(bonus, label)
        model.setBigIcon(bonus.getName())
        model.setUserName(str(bonus.getValue()))
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class BattlePassBlueprintsBonusPacker(BlueprintBonusUIPacker):
    __INTELLIGENCE_BLUEPRINT = 'intelligence'
    __ICON_NAME_PREFIX = 'blueprint_{}'

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _pack(cls, bonus):
        models = super(BattlePassBlueprintsBonusPacker, cls)._pack(bonus)
        imageCategory = bonus.getImageCategory()
        userName = ''
        blueprintName = bonus.getBlueprintName()
        if blueprintName == BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT:
            userName = backport.text(R.strings.tooltips.blueprint.BlueprintFragmentTooltip.intelFragment())
        elif blueprintName == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            userName = backport.text(R.strings.blueprints.nations.dyn(imageCategory)())
        for model in models:
            model.setBigIcon(cls.__ICON_NAME_PREFIX.format(imageCategory))
            model.setUserName(userName)

        return models


class BattlePassGoodiesBonusPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        model.setValue(str(count))
        model.setIcon(icon)
        model.setUserName(label)
        model.setBigIcon(icon)
        return model

    @classmethod
    def _packSingleBoosterBonus(cls, bonus, booster, count):
        userName = backport.text(R.strings.tooltips.boostersWindow.booster.activateInfo.title.dyn(booster.boosterGuiType)())
        return cls._packIconBonusModel(bonus, booster.getFullNameForResource(), count, str(userName))


class BattlePassTokenBonusPacker(TokenBonusUIPacker):

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        name = first(bonus.getTokens())
        if name in [BATTLE_BONUS_X5_TOKEN, CREW_BONUS_X3_TOKEN]:
            model = RewardItemModel()
        else:
            model = TokenBonusModel()
        cls._packCommon(bonus, model)
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusPackers(cls):
        tokenBonusPackers = super(BattlePassTokenBonusPacker, cls)._getTokenBonusPackers()
        tokenBonusPackers.update({BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token,
         CREW_BONUS_X3_TOKEN: cls.__packCrewBonusX3Token})
        return tokenBonusPackers

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setName(BATTLE_BONUS_X5_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setUserName(backport.text(R.strings.battle_pass.battleBonusX5()))
        model.setBigIcon(BATTLE_BONUS_X5_TOKEN)
        return model

    @classmethod
    def __packCrewBonusX3Token(cls, model, bonus, *args):
        model.setName(CREW_BONUS_X3_TOKEN)
        model.setValue(str(bonus.getCount()))
        model.setBigIcon(CREW_BONUS_X3_TOKEN)
        return model


class BattlePassBerthsBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(BattlePassBerthsBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setBigIcon(bonus.getName())
        model.setUserName(backport.text(R.strings.tooltips.awardItem.berths.header()))
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


@contextmanager
def useBigAwardInjection():
    _BattlePassFinalBonusPacker.setIsBigAward(True)
    yield
    _BattlePassFinalBonusPacker.setIsBigAward(False)
