# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/helpers/bonuses/bonus_packers.py
import logging
import typing
from battle_pass_common import CurrencyBP
from constants import PREMIUM_ENTITLEMENTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.customization.shared import getSingleVehicleForCustomization
from gui.impl import backport
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, CREW_BONUS_X3_TOKEN
from gui.server_events.bonuses import getNonQuestBonuses, BlueprintsBonusSubtypes, mergeBonuses, splitBonuses
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.Vehicle import getUnicName
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.missions.packers.bonus import SimpleBonusUIPacker, getDefaultBonusPackersMap, BonusUIPacker, VehiclesBonusUIPacker, BaseBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, CrewSkinBonusUIPacker, CurrenciesBonusUIPacker, GoodiesBonusUIPacker, TokenBonusUIPacker, ItemBonusUIPacker, BlueprintBonusUIPacker, CrewBookBonusUIPacker
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from open_bundle.gui.impl.gen.view_models.views.lobby.bonus_model import BonusModel, VehicleType
from open_bundle.helpers.bonuses.bonuses_constants import ATTACHMENTS_TOKEN_PREFIX, ATTACHMENTS_TOKEN_NAME
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.server_events.bonuses import SimpleBonus
    from typing import Dict, List, Optional
_logger = logging.getLogger(__name__)

def composeBonuses(rewards):
    bonuses = []
    for reward in rewards:
        for key, value in reward.iteritems():
            bonuses.extend(getNonQuestBonuses(key, value))

    return bonuses


@dependency.replace_none_kwargs(openBundle=IOpenBundleController)
def hideInvisible(bonuses, openBundle=None):
    return list(filter(openBundle.isBonusVisible, bonuses))


@dependency.replace_none_kwargs(openBundle=IOpenBundleController)
def sortBonuses(bonuses, reverse=True, openBundle=None):
    bonuses = mergeBonuses(bonuses)
    bonuses = splitBonuses(bonuses)
    bonuses.sort(key=openBundle.getBonusPriority, reverse=reverse)
    return bonuses


def processAttachmentTokens(bonuses, showAttachmentSet):
    if not showAttachmentSet:
        return [ bonus for bonus in bonuses if not isAttachmentToken(bonus) ]
    else:
        finalBonuses = []
        attachmentIDs = set()
        for bonus in bonuses:
            if isAttachmentToken(bonus):
                tokenID = bonus.getTokens().keys()[0]
                attachmentIDs.update(tokenID.split(':')[2:])

        for bonus in bonuses:
            if bonus.getName() == 'customizations':
                customizations = bonus.getCustomizations()
                for item in customizations:
                    customizationItem = bonus.getC11nItem(item)
                    if not (customizationItem is not None and customizationItem.itemTypeName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ATTACHMENT] and str(customizationItem.id) in attachmentIDs):
                        finalBonuses.append(bonus)

            finalBonuses.append(bonus)

        return finalBonuses


def isAttachmentToken(bonus):
    if bonus.getName() != 'battleToken':
        return False
    tokenID = bonus.getTokens().keys()[0]
    return tokenID.startswith(ATTACHMENTS_TOKEN_PREFIX)


def parseAttachmentToken(token):
    if not token.startswith(ATTACHMENTS_TOKEN_PREFIX):
        return ('', [])
    tokenParts = token.split(':')
    attachmentSetName = tokenParts[1]
    attachmentIDs = [ int(attachmentID) for attachmentID in tokenParts[2:] ]
    return (attachmentSetName, attachmentIDs)


def getOpenBundleBonusPacker():
    mapping = getDefaultBonusPackersMap()
    currencyPacker = OpenBundleCurrencyBonusUIPacker()
    mapping.update({'blueprints': OpenBundleBlueprintBonusUIPacker(),
     'crewBooks': OpenBundleCrewBookBonusUIPacker(),
     'crewSkins': OpenBundleCrewSkinBonusUIPacker(),
     'customizations': OpenBundleCustomizationsBonusUIPacker(),
     'currencies': OpenBundleCurrenciesBonusUIPacker(),
     'goodies': OpenBundleGoodiesBonusUIPacker(),
     'items': OpenBundleItemBonusUIPacker(),
     'slots': OpenBundleSlotsBonusUIPacker(),
     'tmanToken': OpenBundleTmanTemplateBonusUIPacker(),
     'tokens': OpenBundleTokenBonusUIPacker(),
     'battleToken': OpenBundleTokenBonusUIPacker(),
     'vehicles': OpenBundleVehiclesBonusUIPacker(),
     'lootBox': OpenBundleLootBoxBonusUIPacker(),
     Currency.FREE_XP: currencyPacker,
     Currency.CREDITS: currencyPacker,
     Currency.GOLD: currencyPacker,
     Currency.EQUIP_COIN: currencyPacker,
     Currency.CRYSTAL: currencyPacker,
     Currency.BPCOIN: OpenBundleBPCoinBonusUIPacker(),
     PREMIUM_ENTITLEMENTS.PLUS: OpenBundlePremiumBonusUIPacker()})
    return BonusUIPacker(mapping)


def packBonusModelAndTooltipData(bonuses, bonusModelsList, tooltipData=None, packer=None, showAttachmentSet=False):
    if packer is None:
        packer = getOpenBundleBonusPacker()
    bonusIndexTotal = len(tooltipData) if tooltipData is not None else 0
    bonuses = processAttachmentTokens(bonuses, showAttachmentSet=showAttachmentSet)
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


class OpenBundleSlotsBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(bonus.getValue())
        model.setIcon(bonus.getName())
        model.setLabel(backport.text(R.strings.tooltips.awardItem.slots.header()))
        return model


class OpenBundleCurrencyBonusUIPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setLabel(str(bonus.getValue()))
        return model


class OpenBundleVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        return [ cls._packVehicle(bonus, vehInfo, vehicle) for vehicle, vehInfo in vehicles ]

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = BonusModel()
        model.setName(bonus.getName())
        styleID = vehInfo.get('customization', {}).get('styleId')
        if styleID is not None and vehicle.isOutfitLocked:
            model.setStyleID(styleID)
        model.setName(bonus.getName())
        model.setIsRent(isRent)
        cls.__fillVehicleInfo(model, vehicle)
        return model

    @classmethod
    def __fillVehicleInfo(cls, model, vehicle):
        model.setIsInHangar(vehicle.isInInventory)
        model.setId(vehicle.intCD)
        model.setLabel(vehicle.userName)
        model.setVehicleShortName(vehicle.shortUserName)
        model.setType(VehicleType(vehicle.type))
        model.setLevel(vehicle.level)
        model.setIsElite(vehicle.isElite)
        model.setIcon(getUnicName(vehicle.name))


class OpenBundleLootBoxBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        model.setName(bonus.getName())
        box = bonus.getBox()
        model.setId(bonus.lootBoxID)
        model.setIcon('lootBox_' + box.getCategory() if box else bonus.getName())
        model.setCount(bonus.getCount())
        model.setLabel(box.getUserName() if box else '')
        return model

    @classmethod
    def _getContentId(cls, _):
        return [R.views.mono.lootbox.tooltips.box_tooltip()]

    @classmethod
    def _getToolTip(cls, bonus):
        box = bonus.getBox()
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[box.getCategory(), box.getType()])]


class OpenBundleCustomizationsBonusUIPacker(BaseBonusUIPacker):
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item, data in zip(bonus.getCustomizations(), bonus.getList()):
            if item is None or cls.__isLockedStyle(bonus, item):
                continue
            result.append(cls._packSingleBonus(bonus, item, data))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, data):
        model = BonusModel()
        model.setName(bonus.getName())
        custItem = bonus.getC11nItem(item)
        itemName = custItem.itemTypeName
        if itemName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.ATTACHMENT]:
            model.setName(itemName)
            model.setIcon(custItem.name)
            model.setOverlayType(custItem.rarity)
        else:
            if itemName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE]:
                vehicleCD = getSingleVehicleForCustomization(custItem)
                model.setIsInHangar(vehicleCD is not None and custItem.fullInventoryCount() > 0)
                if custItem.is3D:
                    itemName = 'style_3d'
            model.setIcon(itemName)
        model.setId(custItem.id)
        model.setCount(item.get('value', 0))
        itemType = backport.text(R.strings.open_bundle.bonuses.itemTypes.dyn(itemName)())
        model.setLabel(backport.text(R.strings.open_bundle.bonuses.customization(), itemType=itemType, userName=custItem.userName))
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
            if itemCustomization.itemTypeName in (GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE], GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.CAMOUFLAGE]):
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
    def __isLockedStyle(cls, bonus, item):
        item = bonus.getC11nItem(item)
        return item.itemTypeName == GUI_ITEM_TYPE_NAMES[GUI_ITEM_TYPE.STYLE] and item.isLockedOnVehicle


class OpenBundleCrewSkinBonusUIPacker(CrewSkinBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, crewSkin, count, label):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(count)
        model.setIcon(str(crewSkin.itemTypeName + str(crewSkin.getRarity())))
        model.setLabel(backport.text(R.strings.open_bundle.bonuses.crewSkin(), appearance=label))
        return model


class OpenBundleCurrenciesBonusUIPacker(CurrenciesBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = BonusModel()
        model.setName(bonus.getCode())
        model.setValue(str(bonus.getValue()))
        model.setIcon(bonus.getCode())
        model.setLabel(str(bonus.getValue()))
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.battle_pass.tooltips.BattlePassTalerTooltip()] if bonus.getCode() == CurrencyBP.TALER.value else super(OpenBundleCurrenciesBonusUIPacker, cls)._getContentId(bonus)


class OpenBundleBPCoinBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setValue(str(bonus.getValue()))
        model.setCount(str(bonus.getValue()))
        model.setIcon(bonus.getName())
        model.setLabel(backport.text(R.strings.open_bundle.bonuses.bpcoin()))
        return model

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView()]


class OpenBundleItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(count)
        icon, overlay = (item.name, '') if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER else (item.getGUIEmblemID(), item.getOverlayType())
        model.setIcon(icon)
        model.setOverlayType(overlay)
        model.setLabel(item.userName)
        return model


class OpenBundleGoodiesBonusUIPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packSingleBoosterBonus(cls, bonus, booster, count):
        return cls._packIconBonusModel(bonus, booster.getFullNameForResource(), count, backport.text(R.strings.menu.booster.label.dyn(booster.boosterGuiType)(), effectValue=booster.getFormattedValue()))

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label, description=''):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(count)
        model.setIcon(icon)
        model.setLabel(label)
        return model


class OpenBundlePremiumBonusUIPacker(BaseBonusUIPacker):
    _ICONS_AVAILABLE = (1, 2, 3, 7, 14, 30, 90, 180, 360)

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus)]

    @classmethod
    def _packSingleBonus(cls, bonus):
        model = BonusModel()
        model.setName(bonus.getName())
        days = bonus.getValue()
        icon = '{}_{}'.format(bonus.getName(), str(days)) if days in cls._ICONS_AVAILABLE else 'premium_plus_universal'
        model.setIcon(icon)
        model.setIsCompensation(bonus.isCompensation())
        model.setValue(str(days))
        model.setLabel(backport.text(R.strings.open_bundle.bonuses.premiumPlus()))
        return model


class OpenBundleTokenBonusUIPacker(TokenBonusUIPacker):
    _ATTACHMENTS_RES = R.strings.open_bundle.bonuses.attachmentsSet

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        model = BonusModel()
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getTokenBonusPackers(cls):
        return {BATTLE_BONUS_X5_TOKEN: cls.__packBattleBonusX5Token,
         CREW_BONUS_X3_TOKEN: cls.__packCrewBonusX3Token,
         ATTACHMENTS_TOKEN_NAME: cls.__packAttachmentsToken}

    @classmethod
    def _getTooltipsPackers(cls):
        packers = super(OpenBundleTokenBonusUIPacker, cls)._getTooltipsPackers()
        return {BATTLE_BONUS_X5_TOKEN: packers[BATTLE_BONUS_X5_TOKEN],
         CREW_BONUS_X3_TOKEN: packers[CREW_BONUS_X3_TOKEN],
         ATTACHMENTS_TOKEN_NAME: cls.__getAttachmentTokenTooltip}

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        return ATTACHMENTS_TOKEN_NAME if tokenID.startswith(ATTACHMENTS_TOKEN_PREFIX) else super(OpenBundleTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def __packBattleBonusX5Token(cls, model, bonus, *args):
        model.setCount(bonus.getCount())
        model.setLabel(backport.text(R.strings.open_bundle.bonuses.battleBonusX5()))
        model.setIcon(BATTLE_BONUS_X5_TOKEN)
        return model

    @classmethod
    def __packCrewBonusX3Token(cls, model, bonus, *args):
        model.setCount(bonus.getCount())
        model.setLabel(backport.text(R.strings.open_bundle.bonuses.crewBonusX3()))
        model.setIcon(CREW_BONUS_X3_TOKEN)
        return model

    @classmethod
    def __packAttachmentsToken(cls, model, bonus, *args):
        tokenName = bonus.getTokens().keys()[0]
        attachmentsName, _ = parseAttachmentToken(tokenName)
        model.setIcon(attachmentsName)
        model.setName(ATTACHMENTS_TOKEN_NAME)
        model.setCount(bonus.getCount())
        model.setValue(tokenName)
        labelRes = cls._ATTACHMENTS_RES.dyn(attachmentsName, cls._ATTACHMENTS_RES.default)
        model.setLabel(backport.text(labelRes()))
        return model

    @classmethod
    def __getAttachmentTokenTooltip(cls, _, token):
        attachmentsName, _ = parseAttachmentToken(token.id)
        nameRes = cls._ATTACHMENTS_RES.dyn(attachmentsName, cls._ATTACHMENTS_RES.default)
        return createTooltipData(makeTooltip(backport.text(nameRes()), backport.text(cls._ATTACHMENTS_RES.tooltip.body())))


class OpenBundleBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = BonusModel()
        model.setName(bonus.getName())
        label = bonus.getBlueprintTooltipName()
        model.setIcon(bonus.getImageCategory())
        blueprintName = bonus.getBlueprintName()
        if blueprintName == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            label = backport.text(R.strings.open_bundle.bonuses.blueprints.nationalFragment(), nation=backport.text(R.strings.blueprints.nations.dyn(bonus.getImageCategory())()))
        elif blueprintName == BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT:
            label = backport.text(R.strings.open_bundle.bonuses.blueprints.universalFragment())
        model.setLabel(label)
        model.setCount(bonus.getCount())
        return [model]

    @staticmethod
    def getTooltip(bonuses):
        fragmentCDs = [ bonus.getBlueprintSpecialArgs() for bonus in bonuses ]
        specialAlias = [ bonus.getBlueprintSpecialAlias() for bonus in bonuses ]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=specialAlias, specialArgs=[fragmentCDs])


class OpenBundleCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = BonusModel()
        model.setName(bonus.getName())
        model.setCount(count)
        model.setLabel(book.userName)
        model.setIcon(book.getBonusIconName())
        return model


class OpenBundleTmanTemplateBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for tokenID, tokenRecord in bonus.getTokens().iteritems():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                count = tokenRecord.count
                packed = cls.__packTmanTemplateToken(tokenID, bonus, count)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        return result

    @classmethod
    def __packTmanTemplateToken(cls, tokenID, bonus, count):
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return
        else:
            model = BonusModel()
            model.setName(bonus.getName())
            model.setCount(count)
            model.setIcon(cls.__getBonusImageName(recruit))
            groupName = recruit.getGroupName()
            if groupName == 'men1':
                label = backport.text(R.strings.open_bundle.bonuses.standardCrewMember.male())
            elif groupName == 'women1':
                label = backport.text(R.strings.open_bundle.bonuses.standardCrewMember.female())
            else:
                label = backport.text(R.strings.open_bundle.bonuses.uniqueCrewMember(), fullName=recruit.getFullUserName())
            model.setLabel(label)
            return model

    @classmethod
    def __getBonusImageName(cls, recruitInfo):
        baseName = 'tank{}man'.format('wo' if recruitInfo.isFemale() else '')
        return baseName

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
