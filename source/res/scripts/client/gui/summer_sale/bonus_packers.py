# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/summer_sale/bonus_packers.py
from copy import deepcopy
import constants
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.summer_sale.compensation_bonus_model import CompensationBonusModel
from gui.impl.gen.view_models.views.lobby.summer_sale.summer_sale_tokens_bonus_model import SummerSaleTokensBonusModel
from gui.impl.gen.view_models.views.lobby.summer_sale.vehicle_bonus_model import VehicleBonusModel, VehicleType
from gui.impl.lobby.loot_box.loot_box_helper import R_LOOTBOX_TOOLTIP
from gui.server_events.bonuses import getServiceBonuses
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.missions.packers.bonus import BACKPORT_TOOLTIP_CONTENT_ID, BonusUIPacker, CurrenciesBonusUIPacker, SimpleBonusUIPacker, TokenBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPackersMap
from gui.shared.money import Currency
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import ISummerSaleController
from skeletons.gui.shared import IItemsCache

def getSummerSaleRewardsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': SummerSaleVehiclesBonusUIPacker,
     'lootBoxToken': SummerSaleTokenBonusUIPacker,
     'currencies': SummerSaleCurrenciesBonusUIPacker,
     Currency.CREDITS: SummerSaleCreditsBonusUIPacker})
    return BonusUIPacker(mapping)


class SummerSaleCompensationBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(SummerSaleCompensationBonusUIPacker, cls)._packSingleBonus(bonus, label)
        model.setCompensatedBonus(bonus.getCompensationReason().getName() if bonus.getCompensationReason() else '')
        return model

    @classmethod
    def _getBonusModel(cls):
        return CompensationBonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(tooltip=None, isSpecial=True, specialAlias=None, specialArgs=[cls._getCompensatedBonus(bonus), bonus])]

    @classmethod
    def _getCompensatedBonus(cls, bonus):
        compensatedBonus = bonus.getCompensationReason()
        if compensatedBonus and compensatedBonus.getName() == 'vehicles':
            bonusValue = deepcopy(compensatedBonus.getValue())
            for item in bonusValue:
                for vehInfo in item.values():
                    if vehInfo.get('compensatedNumber', 0) > 0:
                        vehInfo['compensatedNumber'] -= 1

            return getServiceBonuses(compensatedBonus.getName(), bonusValue)[0]
        return compensatedBonus

    @classmethod
    def _getContentId(cls, bonus):
        tooltipRes = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes').dyn('tooltips').dyn('CompensationTooltip')
        return [tooltipRes()] if tooltipRes.exists() else SimpleBonusUIPacker._getContentId(bonus)


class SummerSalePossibleCompensationBonusUIPacker(SummerSaleCompensationBonusUIPacker):

    @classmethod
    def _getCompensatedBonus(cls, bonus):
        return bonus.getCompensationReason()


class SummerSaleVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = VehicleBonusModel()
        model.setName(bonus.getName())
        model.setVehicleName(getNationLessName(vehicle.name))
        model.setType(VehicleType(vehicle.type))
        model.setNationTag(vehicle.nationName)
        model.setLevel(vehicle.level)
        model.setIsCompensation(bonus.isCompensation())
        model.setIsElite(vehicle.isElite)
        model.setIsRent(vehicle.isRented)
        model.setInInventory(vehicle.isInInventory)
        model.setWasSold(vehicle.restoreInfo is not None)
        model.setIntCD(vehicle.intCD)
        if isRent:
            model.setRentDays(bonus.getRentDays(vehInfo) or 0)
            model.setRentBattles(bonus.getRentBattles(vehInfo) or 0)
        model.setLabel(cls._getLabel(vehicle))
        model.setShortVehicleLabel(vehicle.shortUserName)
        if 'price' in vehInfo:
            model.price.setCurrency(vehInfo['price'].get('currency', ''))
            model.price.setAmount(vehInfo['price'].get('amount', 0))
        model.setProductCode(vehInfo.get('productCode', ''))
        return model

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                packer = SummerSaleCompensationBonusUIPacker()
                for bonusComp in compensation:
                    packedVehicles.extend(packer.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        return SummerSaleCompensationBonusUIPacker().getToolTip(bonusComp)

    @classmethod
    def _getContentId(cls, bonus):
        contentIds = []
        vehicles = bonus.getVehicles()
        for vehicle, _ in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                for bonusComp in compensation:
                    packer = SummerSaleCompensationBonusUIPacker()
                    contentIds.extend(packer.getContentId(bonusComp))

            contentIds.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return contentIds


class SummerSaleTokenBonusUIPacker(TokenBonusUIPacker):
    __itemsCache = dependency.descriptor(IItemsCache)
    __summerSale = dependency.descriptor(ISummerSaleController)

    @classmethod
    def _packToken(cls, bonusPacker, bonus, *args):
        model = SummerSaleTokensBonusModel()
        cls._packCommon(bonus, model)
        ctx = bonus.getContext()
        if 'price' in ctx:
            model.price.setCurrency(ctx['price'].get('currency', ''))
            model.price.setAmount(ctx['price'].get('amount', 0))
        model.setProductCode(ctx.get('productCode', ''))
        model.setInInventory(cls.__summerSale.isRandomVehicleObtained())
        return bonusPacker(model, bonus, *args)

    @classmethod
    def _getToolTip(cls, bonus):
        getLootBox = cls.__itemsCache.items.tokens.getLootBoxByTokenID
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            lootbox = getLootBox(tokenID)
            if lootbox:
                result.append({'lootBoxID': lootbox.getID()})

        return result

    @classmethod
    def _getContentId(cls, bonus):
        getLootBox = cls.__itemsCache.items.tokens.getLootBoxByTokenID
        result = []
        for tokenID in bonus.getTokens().iterkeys():
            lootbox = getLootBox(tokenID)
            if lootbox and lootbox.isImmediatelyOpen():
                result.append(R.views.lobby.summer_sale.RandomVehicleTooltip())
            if tokenID.startswith(constants.LOOTBOX_TOKEN_PREFIX):
                if R_LOOTBOX_TOOLTIP.exists():
                    result.append(R_LOOTBOX_TOOLTIP())
            result.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return result


class SummerSaleCurrenciesBonusUIPacker(CurrenciesBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        result = []
        wrapped = first(bonus.getWrappedEpicBonusList())
        if wrapped:
            result.append({'currencyType': wrapped['type']})
        return result

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.summer_sale.EventCurrencyTooltip()]


class SummerSaleCreditsBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        result = []
        wrapped = first(bonus.getWrappedEpicBonusList())
        if wrapped:
            result.append({'currencyType': wrapped['type']})
        return result

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.lobby.summer_sale.EventCurrencyTooltip()]
