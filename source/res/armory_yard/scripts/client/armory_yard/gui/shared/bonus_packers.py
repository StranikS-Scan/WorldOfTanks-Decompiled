# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/bonus_packers.py
import logging
import typing
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from constants import PREMIUM_ENTITLEMENTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_vehicle_model import ArmoryYardRewardsVehicleModel
from armory_yard_constants import isArmoryYardBattleToken, FEATURE_NAME_BASE, ARMORY_YARD_COIN_NAME
from gui.impl.backport import TooltipData
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses, mergeBonuses, VehiclesBonus, TokensBonus, CurrenciesBonus, CustomizationsBonus
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, BonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, TokenBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPacker, PremiumDaysBonusPacker, getLocalizedBonusName, SimpleBonusUIPacker, CustomizationBonusUIPacker
from items.vehicles import getVehicleClassFromVehicleType
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
if typing.TYPE_CHECKING:
    BonusModelType = typing.TypeVar('BonusModelType', bound=BonusModel)
    from gui.shared.gui_items.Vehicle import Vehicle
    from typing import List
    from frameworks.wulf import Array
    from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
_logger = logging.getLogger(__name__)
_ARMORY_YARD_REST_ICON_NAME = 'default'

class ArmoryYardTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _getTokenBonusPackers(cls):
        packers = super(ArmoryYardTokenBonusUIPacker, cls)._getTokenBonusPackers()
        packers[FEATURE_NAME_BASE] = cls.__packArmoryYardToken
        return packers

    @classmethod
    def _getToolTip(cls, bonus):
        return [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[])]

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.armory_yard.lobby.feature.tooltips.ArmoryYardCurrencyTooltipView()]

    @classmethod
    def _getTokenBonusType(cls, tokenID, complexToken):
        if isArmoryYardBattleToken(tokenID):
            return FEATURE_NAME_BASE
        return '' if tokenID == 'ny24_yaga' else super(ArmoryYardTokenBonusUIPacker, cls)._getTokenBonusType(tokenID, complexToken)

    @classmethod
    def __packArmoryYardToken(cls, model, _, *args):
        model.setIconSmall(backport.image(R.images.armory_yard.gui.maps.icons.token.s20()))
        model.setIconBig(backport.image(R.images.armory_yard.gui.maps.icons.token.s44()))
        return model


class ArmoryYardCurrencyBonusUIPacker(SimpleBonusUIPacker):

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
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = [TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[bonus.getCode()])]
        return tooltipData

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.armory_yard.lobby.feature.tooltips.ArmoryYardCurrencyTooltipView() if bonus.getCode() == ARMORY_YARD_COIN_NAME else BACKPORT_TOOLTIP_CONTENT_ID]


class ArmoryCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        for item in bonus.getCustomizations():
            if item is None:
                continue
            label = cls._getLabel(bonus.getC11nItem(item))
            result.append(cls._packSingleBonus(bonus, item, label))

        return result

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        model.setIcon(cls._getIcon(bonus, bonus.getC11nItem(item)))
        model.setLabel(label)
        return model

    @classmethod
    def _getLabel(cls, c11nItem):
        userName = c11nItem.userName
        elementBonusR = R.strings.vehicle_customization.elementBonus.desc.dyn(c11nItem.itemFullTypeName, R.invalid)
        return backport.text(elementBonusR(), value=userName) if elementBonusR else userName

    @classmethod
    def _getIcon(cls, bonus, c11Item):
        return str(c11Item.itemTypeName) + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else str(c11Item.itemTypeName)


class ArmoryUniqueCustomizationBonusUIPacker(ArmoryCustomizationBonusUIPacker):

    @classmethod
    def _getIcon(cls, bonus, c11Item):
        itemTypeName = str(c11Item.itemTypeName)
        iconName = '{}_{}'.format(itemTypeName + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else itemTypeName, c11Item.innationID)
        if R.images.gui.maps.icons.quests.bonuses.s600x450.dyn(iconName).exists():
            return iconName
        return itemTypeName + '_3d' if c11Item.itemTypeID == GUI_ITEM_TYPE.STYLE and c11Item.is3D else itemTypeName


class ArmoryYardVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicle(cls, bonus, vehInfo, vehicle):
        vehicleModel = ArmoryYardRewardsVehicleModel()
        packVehicleModel(vehicleModel, vehicle)
        rentDays = bonus.getRentDays(vehInfo)
        rentBattles = bonus.getRentBattles(vehInfo)
        rentWins = bonus.getRentWins(vehInfo)
        rentSeason = bonus.getRentSeason(vehInfo)
        rentCycle = bonus.getRentCycle(vehInfo)
        isRent = rentDays or rentBattles or rentWins or rentSeason or rentCycle
        vehicleModel.setName(cls._createUIName(bonus, isRent))
        vehicleModel.setIsCompensation(bonus.isCompensation())
        vehicleModel.setLabel(cls._getLabel(vehicle))
        return vehicleModel

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
        rentDays = bonus.getRentDays(vehInfo)
        rentBattles = bonus.getRentBattles(vehInfo)
        rentWins = bonus.getRentWins(vehInfo)
        rentSeason = bonus.getRentSeason(vehInfo)
        rentCycle = bonus.getRentCycle(vehInfo)
        rentExpiryTime = cls._getRentExpiryTime(rentDays)
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.ARMORY_YARD_AWARD_VEHICLE, specialArgs=[vehicle.intCD,
         tmanRoleLevel,
         rentExpiryTime,
         rentBattles,
         rentWins,
         rentSeason,
         rentCycle])


class ArmoryYardTmanTemplateBonusPacker(TmanTemplateBonusPacker):

    @classmethod
    def _packTmanTemplateToken(cls, tokenID, bonus):
        model = super(ArmoryYardTmanTemplateBonusPacker, cls)._packTmanTemplateToken(tokenID, bonus)
        tokenRecord = bonus.getTokens()[tokenID]
        if tokenRecord.count > 1:
            model.setValue(str(tokenRecord.count))
            model.setIcon('tankman')
            model.setBigIcon('tankman_men1')
            model.setItem('tankman')
            model.setName('items')
        return model


def getArmoryYardBonusPackersMap(hasBattleTokens=True):
    packersMap = getDefaultBonusPackersMap()
    packersMap.update({'vehicles': ArmoryYardVehiclesBonusUIPacker,
     'tmanToken': ArmoryYardTmanTemplateBonusPacker,
     PREMIUM_ENTITLEMENTS.PLUS: PremiumDaysBonusPacker,
     'currencies': ArmoryYardCurrencyBonusUIPacker,
     'customizations': ArmoryCustomizationBonusUIPacker})
    if hasBattleTokens:
        packersMap.update({'battleToken': ArmoryYardTokenBonusUIPacker})
    return packersMap


def getArmoryYardMainRewardBonusPackersMap():
    packersMap = getArmoryYardBonusPackersMap()
    packersMap.update({'customizations': ArmoryUniqueCustomizationBonusUIPacker})
    return packersMap


def getArmoryYardBonusPacker(hasBattleTokens=True):
    return BonusUIPacker(getArmoryYardBonusPackersMap(hasBattleTokens))


def getArmoryYardMainRewardBonusPacker():
    return BonusUIPacker(getArmoryYardMainRewardBonusPackersMap())


def packVehicleModel(vehicleModel, vehicle):
    vehicleModel.setVehicleImg(getNationLessName(vehicle.name))
    vehicleModel.setVehicleName(vehicle.userName)
    vehicleModel.setLevel(vehicle.level)
    vehicleModel.setType(getVehicleClassFromVehicleType(vehicle.descriptor.type))
    vehicleModel.setIsElite(vehicle.isElite)


def packRestModel(rewardsList, rewardListModel, tooltipData, index, restRewardsTextId=None):
    model = BonusModel()
    model.setName(_ARMORY_YARD_REST_ICON_NAME)
    model.setValue(backport.text(restRewardsTextId or R.strings.armory_yard.buyView.reward.rest(), count=len(rewardsList)))
    model.setTooltipContentId(str(R.views.armory_yard.lobby.feature.tooltips.RestRewardTooltipView()))
    tooltipID = str(len(tooltipData))
    tooltipData[tooltipID] = TooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[rewardsList])
    model.setTooltipId(tooltipID)
    model.setIndex(index)
    rewardListModel.addViewModel(model)
    return


def packBonuses(rewards, packer=None):
    bonuses = []
    for rewardType, rewardValue in rewards.items():
        bonuses.extend(getNonQuestBonuses(rewardType, rewardValue))

    bonuses = splitBonuses(mergeBonuses(bonuses))
    bonuses.sort(key=bonusesSortKeyFunc)
    packer = packer or getDefaultBonusPacker()
    return [ packedBonus for bonus in bonuses for packedBonus in packer.pack(bonus) ]
