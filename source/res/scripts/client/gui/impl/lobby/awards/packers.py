# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/awards/packers.py
import logging
import typing
from adisp import adisp_async, adisp_process
from constants import RentType, OFFER_TOKEN_PREFIX
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport import createTooltipData, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.awards.reward_model import RewardModel, RentTypeEnum
from gui.impl.lobby.awards import SupportedTokenTypes
from gui.impl.lobby.awards.prefetch import TokenDataPrefetcher
from gui.impl.lobby.awards.tooltip import VEH_FOR_CHOOSE_ID
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.missions.packers.bonus import VehiclesBonusUIPacker, getDefaultBonusPackersMap, BaseBonusUIPacker, AsyncBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, Customization3Dand2DbonusUIPacker, CustomizationBonusUIPacker, BonusUIPacker
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from items import tankmen
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.platform.catalog_service.controller import _PurchaseDescriptor
    from gui.server_events.bonuses import VehiclesBonus, TokensBonus, TmanTemplateTokensBonus
    from gui.server_events.recruit_helper import _BaseRecruitInfo
    from gui.shared.gui_items.Vehicle import Vehicle
    from typing import Optional, Callable
VEH_COMP_R_ID = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()
_GAMEPLAY_TO_UI_RENT_MAPPING = {RentType.NO_RENT: RentTypeEnum.NONE,
 RentType.TIME_RENT: RentTypeEnum.DAYS,
 RentType.BATTLES_RENT: RentTypeEnum.BATTLES,
 RentType.WINS_RENT: RentTypeEnum.WINS}
_LOCAL_FOLDER_NAME = 'multiple_awards'
_logger = logging.getLogger(__name__)

def _convertRentType(gpRentType):
    uiRentType = _GAMEPLAY_TO_UI_RENT_MAPPING.get(gpRentType)
    if uiRentType is None:
        _logger.warning('Unsupported on UI rent type: %d', gpRentType)
        uiRentType = RentTypeEnum.NONE
    return uiRentType


def _getOffersTokenStateData(offers):
    vehicles = []
    rentData = []
    offersIDs = []
    for offer in offers:
        offersIDs.append(offer.id)
        for gift in offer.getAllGifts():
            if gift.isVehicle:
                vehicles.append(gift.bonus.displayedItem.intCD)
                if gift.rentType != RentType.NO_RENT:
                    incomingRentType = (gift.rentType, gift.rentValue)
                    for rD in rentData:
                        if rD == incomingRentType:
                            break
                    else:
                        rentData.append(incomingRentType)

    rentTypesCount = len(rentData)
    return (offersIDs[0] if len(offersIDs) == 1 else 0,
     vehicles,
     rentTypesCount > 0,
     rentData[0] if rentTypesCount == 1 else None)


def getVehicleUIData(vehicle):
    return {'vehicleName': vehicle.shortUserName,
     'vehicleType': getIconResourceName(vehicle.type),
     'isElite': vehicle.isElite,
     'vehicleLvl': int2roman(vehicle.level),
     'vehicleLvlNum': vehicle.level}


class _MultiProductAwardTokenBonusUIPacker(BaseBonusUIPacker):
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __purchaseCache = dependency.descriptor(IPurchaseCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, productID):
        super(_MultiProductAwardTokenBonusUIPacker, self).__init__()
        self.__productID = productID

    def isAsync(self):
        return True

    @adisp_async
    @adisp_process
    def asyncPack(self, bonus, callback=None):
        yield lambda callback: callback(True)
        result = []
        bonusTokens = bonus.getTokens()
        for tID in bonusTokens.iterkeys():
            if tID.startswith(OFFER_TOKEN_PREFIX):
                offers = self.__offersProvider.getAvailableOffersByToken(tID)
                if not offers:
                    continue
                offerID, vehicles, _, rentData = _getOffersTokenStateData(offers)
                model = RewardModel()
                model.setItemID(offerID)
                if vehicles:
                    model.setIsVehicleOnChoice(True)
                if rentData:
                    model.setVehicleRentType(_convertRentType(rentData[0]))
                    model.setVehicleRentValue(rentData[1])
            else:
                model = RewardModel()
            self._packCommon(bonus, model)
            prefetcher = TokenDataPrefetcher(self.__productID)
            iconSmallPath, iconBigPath = yield prefetcher.getImageData(tID)
            if not iconSmallPath:
                _logger.warning("Couldn't obtain big image for %s!", tID)
            if not iconBigPath:
                _logger.warning("Couldn't obtain small image for %s!", tID)
            model.setIconBig(iconBigPath)
            model.setIconSmall(iconSmallPath)
            result.append(model)

        callback(result)

    @adisp_async
    @adisp_process
    def asyncGetToolTip(self, bonus, callback=None):
        yield lambda callback: callback(True)
        result = []
        bonusTokens = bonus.getTokens()
        for tID in bonusTokens.iterkeys():
            if tID.startswith(OFFER_TOKEN_PREFIX):
                offers = self.__offersProvider.getAvailableOffersByToken(tID)
                if not offers:
                    continue
                _, vehicles, hasRent, _ = _getOffersTokenStateData(offers)
                if hasRent:
                    uiVehs = []
                    for vIntCD in vehicles:
                        uiVehs.append(getVehicleUIData(self.__itemsCache.items.getItemByCD(vIntCD)))

                    result.append(createTooltipData(isSpecial=True, specialAlias=VEH_FOR_CHOOSE_ID, specialArgs={'vehicles': uiVehs}))
                    continue
            purchase = yield self.__purchaseCache.requestPurchaseByID(self.__productID)
            tokenData = purchase.getTokenData(tID)
            result.append(createTooltipData(makeTooltip(tokenData.title, tokenData.description)))

        callback(result)

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        bonusTokens = bonus.getTokens()
        for tID in bonusTokens.iterkeys():
            if tID.startswith(OFFER_TOKEN_PREFIX):
                offers = cls.__offersProvider.getAvailableOffersByToken(tID)
                if not offers:
                    continue
                _, _, hasRent, _ = _getOffersTokenStateData(offers)
                if hasRent:
                    result.append(VEH_FOR_CHOOSE_ID)
                    continue
            result.append(super(_MultiProductAwardTokenBonusUIPacker, cls)._getContentId(bonus))

        return result


class MultiAwardVehiclesBonusUIPacker(VehiclesBonusUIPacker):
    _SPECIAL_ALIAS = TOOLTIPS_CONSTANTS.EXTENDED_AWARD_VEHICLE

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vInfo, isRent, vehicle):
        model = RewardModel()
        gpRentType, rentValue = bonus.getRentInfo(vInfo)
        model.setVehicleRentType(_convertRentType(gpRentType))
        model.setVehicleRentValue(rentValue)
        model.setName(cls._createUIName(bonus, isRent))
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(vehicle.userName)
        vehIconName = getIconResourceName(getNationLessName(vehicle.name))
        model.setItemID(vehicle.intCD)
        model.setUserName(vehicle.userName)
        model.setIcon(vehIconName)
        model.setVehicleLevel(vehicle.level)
        model.setVehicleType(vehicle.type)
        wasInHangarBeforeRent = gpRentType != RentType.NO_RENT and not vehicle.isRented and vehicle.isInInventory
        model.setIsFromStorage(wasInHangarBeforeRent)
        return model

    @classmethod
    def _getContentId(cls, bonus):
        outcome = []
        for vehicle, _ in bonus.getVehicles():
            compensation = cls._getCompensation(vehicle, bonus)
            if compensation:
                for _ in compensation:
                    outcome.append(cls._getVehicleCompensationTooltipContent())

            outcome.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return outcome

    @classmethod
    def _getVehicleCompensationTooltipContent(cls):
        return R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        tooltipDataList = super(MultiAwardVehiclesBonusUIPacker, cls)._packCompensationTooltip(bonusComp, vehicle)
        return [ cls.__convertCompensationTooltip(bonusComp, vehicle, tooltipData) for tooltipData in tooltipDataList ]

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        tooltipData = super(MultiAwardVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)
        tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
        tooltipData.specialArgs.extend([tmanRoleLevel > 0, False, False])
        return tooltipData

    @classmethod
    def __convertCompensationTooltip(cls, bonusComp, vehicle, tooltipData):
        iconAfterRes = R.images.gui.maps.icons.quests.bonuses.big.dyn(bonusComp.getName())
        if not iconAfterRes.exists():
            iconAfterRes = R.images.gui.maps.icons.quests.bonuses.big.gold
        specialArgs = {'labelBefore': '',
         'iconAfter': backport.image(iconAfterRes()),
         'labelAfter': bonusComp.getIconLabel(),
         'bonusName': bonusComp.getName()}
        uiData = getVehicleUIData(vehicle)
        formattedTypeName = uiData['vehicleType']
        isElite = vehicle.isElite
        uiData['vehicleType'] = '{}_elite'.format(formattedTypeName) if isElite else formattedTypeName
        specialArgs.update(uiData)
        vehicleName = getNationLessName(vehicle.name)
        vehIcon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(vehicleName)()
        if vehIcon < 1:
            vehicleName = vehicleName.replace('-', '_')
            vehIcon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(vehicleName)()
        specialArgs['iconBefore'] = backport.image(vehIcon) if vehIcon > 0 else ''
        return createTooltipData(tooltip=tooltipData.tooltip, specialAlias=VEH_COMP_R_ID, specialArgs=specialArgs)


class _TmanTemplateProductBonusPacker(BaseBonusUIPacker):
    __isBigImageUsed = False

    def __init__(self, productID):
        super(_TmanTemplateProductBonusPacker, self).__init__()
        self.__productID = productID

    def isAsync(self):
        return True

    @adisp_async
    @adisp_process
    def asyncPack(self, bonus, callback=None):
        yield lambda callback: callback(True)
        result = []
        tankmenTokens = bonus.getTokens().iterkeys()
        for tokenID in tankmenTokens:
            if tokenID.startswith(tankmen.RECRUIT_TMAN_TOKEN_PREFIX):
                packed = yield self._packTmanTemplateToken(tokenID, bonus)
                if packed is None:
                    _logger.error('Received wrong tman_template token from server: %s', tokenID)
                else:
                    result.append(packed)

        callback(result)
        return

    @adisp_async
    @adisp_process
    def asyncGetToolTip(self, bonus, callback=None):
        yield lambda callback: callback(True)
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(tankmen.RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        callback(tooltipData)
        return

    @classmethod
    def _getContentId(cls, bonus):
        count = len([ tID for tID in bonus.getTokens() if tID.startswith(tankmen.RECRUIT_TMAN_TOKEN_PREFIX) ])
        return [BACKPORT_TOOLTIP_CONTENT_ID] * count

    @adisp_async
    @adisp_process
    def _packTmanTemplateToken(self, tokenID, bonus, callback=None):
        prefetcher = TokenDataPrefetcher(self.__productID)
        iconSmallPath, iconBigPath = yield prefetcher.getImageData(self._getProductToken(tokenID))
        if not iconSmallPath or not iconBigPath:
            iconPath = self._packTmanLocalTemplateToken(tokenID)
            if not iconSmallPath:
                _logger.warning("Couldn't obtain big image for %s!", tokenID)
                iconSmallPath = iconPath
            elif not iconBigPath:
                _logger.warning("Couldn't obtain small image for %s!", tokenID)
                iconBigPath = iconPath
        model = RewardModel()
        self._packCommon(bonus, model)
        model.setIconSmall(iconSmallPath)
        model.setIconBig(iconBigPath)
        callback(model)

    @classmethod
    def _packTmanLocalTemplateToken(cls, tokenID):
        recruitInfo = getRecruitInfo(tokenID)
        if recruitInfo is None:
            return ''
        else:
            groupName = recruitInfo.getGroupName()
            bonusImageName = '_'.join([cls.__getBonusImageName(recruitInfo), groupName])
            return bonusImageName

    @classmethod
    def _getProductToken(cls, tokenName):
        tokenData = tankmen.getRecruitInfoFromToken(tokenName)
        return '{}_{}'.format(tankmen.RECRUIT_TMAN_TOKEN_PREFIX, tokenData['sourceID'])

    @classmethod
    def __getBonusImageName(cls, recruitInfo):
        baseName = 'tank{}man'.format('wo' if recruitInfo.isFemale() else '')
        return baseName


def getMultipleProductAwardsBonusPacker(productCode):
    tokenBonus = _MultiProductAwardTokenBonusUIPacker(productCode)
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': MultiAwardVehiclesBonusUIPacker(),
     'tmanToken': _TmanTemplateProductBonusPacker(productCode),
     'customizations': Customization3Dand2DbonusUIPacker(),
     SupportedTokenTypes.BATTLE_TOKEN: tokenBonus,
     SupportedTokenTypes.TOKENS: tokenBonus,
     SupportedTokenTypes.PROGRESSION_XP_TOKEN: tokenBonus})
    return AsyncBonusUIPacker(mapping)


class _AdditionalCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = super(_AdditionalCustomizationBonusUIPacker, cls)._packSingleBonus(bonus, item, label)
        customization = bonus.getC11nItem(item)
        model.setLabel(customization.userName)
        return model


def getAdditionalAwardsBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'customizations': _AdditionalCustomizationBonusUIPacker()})
    return BonusUIPacker(mapping)
