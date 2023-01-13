# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/battle_pass_bonuses_packers.py
import logging
from contextlib import contextmanager
import typing
from battle_pass_common import BATTLE_PASS_Q_CHAIN_BONUS_NAME, BATTLE_PASS_SELECT_BONUS_NAME, BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_helpers import getOfferTokenByGift, getSingleVehicleForCustomization, getStyleForChapter
from gui.impl import backport
from gui.impl.backport import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
from gui.impl.gen.view_models.views.lobby.battle_pass.vehicle_bonus_model import VehicleBonusModel
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, BaseBonusUIPacker, BlueprintBonusUIPacker, BonusUIPacker, CrewBookBonusUIPacker, DossierBonusUIPacker, ItemBonusUIPacker, SimpleBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPackersMap
from gui.shared.money import Currency
from helpers import dependency
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from shared_utils import first
from skeletons.gui.offers import IOffersDataProvider
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import BattlePassQuestChainTokensBonus, SimpleBonus, TmanTemplateTokensBonus, CustomizationsBonus, PlusPremiumDaysBonus, DossierBonus, BattlePassSelectTokensBonus, BattlePassStyleProgressTokenBonus, VehicleBlueprintBonus
    from account_helpers.offers.events_data import OfferEventData, OfferGift
    from gui.shared.gui_items.Vehicle import Vehicle
_logger = logging.getLogger(__name__)

def getBattlePassBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'tmanToken': TmanTemplateBonusPacker(),
     'customizations': BattlePassCustomizationsBonusPacker(),
     'premium_plus': BattlePassPremiumDaysPacker(),
     'dossier': BattlePassDossierBonusPacker(),
     'items': ExtendedItemBonusUIPacker(),
     'crewBooks': ExtendedCrewBookBonusUIPacker(),
     'blueprints': BattlePassBlueprintsBonusPacker(),
     'slots': BattlePassSlotsBonusPacker(),
     'vehicles': BattlePassVehiclesBonusUIPacker(),
     'freeXP': BattlePassFreeXPPacker(),
     Currency.CREDITS: ExtendedCreditsBonusUIPacker(),
     BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME: BattlePassStyleProgressTokenBonusPacker(),
     BATTLE_PASS_SELECT_BONUS_NAME: SelectBonusPacker(),
     BATTLE_PASS_Q_CHAIN_BONUS_NAME: QuestChainBonusPacker(),
     Currency.BPCOIN: CoinBonusPacker()})
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

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                packed = cls.__packTmanTemplateToken(tokenID, bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def __packTmanTemplateToken(cls, tokenID, bonus):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return
        else:
            recruitGroupName = recruitInfo.getGroupName()
            bonusImageName = 'tankman'
            model = RewardItemModel()
            cls._packCommon(bonus, model)
            model.setIcon('_'.join([bonusImageName, recruitGroupName]))
            model.setUserName(recruitInfo.getFullUserName())
            model.setBigIcon('_'.join([bonusImageName, recruitGroupName]))
            cls._injectAwardID(model, recruitGroupName)
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
        model = RewardItemModel()
        cls._packCommon(bonus, model)
        customizationItem = bonus.getC11nItem(item)
        iconName = customizationItem.itemTypeName
        if iconName == 'style' and customizationItem.modelsSet:
            iconName = 'style_3d'
        model.setValue(str(data.get('value', '')))
        model.setIcon(iconName)
        model.setUserName(customizationItem.userName)
        if customizationItem.itemTypeName == 'style':
            bigIcon = iconName
        else:
            bigIcon = '_'.join([iconName, str(customizationItem.intCD)])
        model.setBigIcon(bigIcon)
        cls._injectAwardID(model, str(customizationItem.intCD))
        return model

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
            dossierIconName = achievement.getName()
            dossierValue = achievement.getValue()
            dossierNamePostfix = '_achievement'
            userName = achievement.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, dossierNamePostfix, dossierValue, userName))

        for badge in bonus.getBadges():
            dossierIconName = 'badge_' + str(badge.badgeID)
            dossierValue = 0
            dossierNamePostfix = '_badge'
            userName = badge.getUserName()
            result.append(cls._packSingleBonus(bonus, dossierIconName, dossierNamePostfix, dossierValue, userName))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, dossierIconName, dossierNamePostfix, dossierValue, userName=''):
        model = RewardItemModel()
        model.setName(bonus.getName() + dossierNamePostfix)
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(dossierValue))
        model.setIcon(dossierIconName)
        model.setUserName(userName)
        model.setBigIcon(dossierIconName)
        return model


class SelectBonusPacker(BaseBonusUIPacker):
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = RewardItemModel()
        model.setName(bonus.getName())
        model.setValue(str(cls.getValue(bonus)))
        model.setIcon(bonus.getType())
        model.setBigIcon(bonus.getType())
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
        else:
            postfix = 'undefined'
        cls._injectAwardID(model, postfix)
        return model

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
        if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
            model.setUserName(item.userName)
        model.setBigIcon(item.getGUIEmblemID())
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


class ExtendedCreditsBonusUIPacker(BaseBonusUIPacker):

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
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.battle_pass.tooltips.BattlePassQuestsChainTooltipView()]

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[bonus.tokenID])]


class BattlePassSlotsBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(BattlePassSlotsBonusPacker, cls)._packSingleBonus(bonus, label)
        model.setBigIcon(bonus.getName())
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
        model.setVehicleNation(vehicle.nationName)


class BattlePassFreeXPPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(BattlePassFreeXPPacker, cls)._packSingleBonus(bonus, label)
        model.setBigIcon(bonus.getName())
        return model

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()


class BattlePassBlueprintsBonusPacker(BlueprintBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return RewardItemModel()

    @classmethod
    def _pack(cls, bonus):
        models = super(BattlePassBlueprintsBonusPacker, cls)._pack(bonus)
        for model in models:
            model.setBigIcon('blueprint_' + bonus.getImageCategory())

        return models


@contextmanager
def useBigAwardInjection():
    _BattlePassFinalBonusPacker.setIsBigAward(True)
    yield
    _BattlePassFinalBonusPacker.setIsBigAward(False)
