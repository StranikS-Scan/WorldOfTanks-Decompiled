# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/awards/packers.py
import logging
import typing
from adisp import adisp_async, adisp_process
from constants import RentType, OFFER_TOKEN_PREFIX
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import TmanTemplateBonusPacker
from gui.impl import backport
from gui.impl.backport import createTooltipData, TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.awards.reward_model import RewardModel, RentTypeEnum
from gui.impl.lobby.awards import SupportedTokenTypes
from gui.impl.lobby.awards.prefetch import TokenDataPrefetcher
from gui.impl.lobby.awards.tooltip import VEH_FOR_CHOOSE_ID
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.missions.packers.bonus import VehiclesBonusUIPacker, getDefaultBonusPackersMap, BaseBonusUIPacker, AsyncBonusUIPacker, BACKPORT_TOOLTIP_CONTENT_ID, Customization3Dand2DbonusUIPacker, CustomizationBonusUIPacker, BonusUIPacker
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, int2roman
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import VehiclesBonus, TokensBonus
    from gui.platform.catalog_service.controller import _PurchaseDescriptor
    from gui.shared.gui_items.Vehicle import Vehicle
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


def _getVehicleUIData(vehicle):
    return {'vehicleName': vehicle.shortUserName,
     'vehicleType': getIconResourceName(vehicle.type),
     'isElite': vehicle.isElite,
     'vehicleLvl': int2roman(vehicle.level),
     'vehicleLvlNum': vehicle.level}


class _MultiAwardTokenBonusUIPacker(BaseBonusUIPacker):
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __purchaseCache = dependency.descriptor(IPurchaseCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, productID):
        super(_MultiAwardTokenBonusUIPacker, self).__init__()
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
                        uiVehs.append(_getVehicleUIData(self.__itemsCache.items.getItemByCD(vIntCD)))

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
            result.append(super(_MultiAwardTokenBonusUIPacker, cls)._getContentId(bonus))

        return result


class _MultiAwardVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vInfo, isRent, vehicle):
        model = RewardModel()
        gpRentType, rentValue = bonus.getRentInfo(vInfo)
        model.setVehicleRentType(_convertRentType(gpRentType))
        model.setVehicleRentValue(rentValue)
        model.setName(cls._createUIName(bonus, isRent, vehicle.isPremium))
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(vehicle.userName)
        vehIconName = getIconResourceName(getNationLessName(vehicle.name))
        model.setItemID(vehicle.intCD)
        model.setUserName(vehicle.userName)
        model.setIcon(vehIconName)
        model.setVehicleLevel(vehicle.level)
        model.setVehicleType(vehicle.type)
        wasInHangarBeforeRent = gpRentType != RentType.NO_RENT and not vehicle.isRented
        model.setIsFromStorage(wasInHangarBeforeRent)
        return model

    @classmethod
    def _getContentId(cls, bonus):
        outcome = []
        for vehicle, _ in bonus.getVehicles():
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                outcome.append(R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent())
            outcome.append(BACKPORT_TOOLTIP_CONTENT_ID)

        return outcome

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        tooltipDataList = super(_MultiAwardVehiclesBonusUIPacker, cls)._packCompensationTooltip(bonusComp, vehicle)
        return [ cls.__convertCompensationTooltip(bonusComp, vehicle, tooltipData) for tooltipData in tooltipDataList ]

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        result = super(_MultiAwardVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)
        tmanRoleLevel = bonus.getTmanRoleLevel(vehInfo)
        result.specialArgs.extend([tmanRoleLevel > 0, False])
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EXTENDED_AWARD_VEHICLE, specialArgs=result.specialArgs)

    @classmethod
    def __convertCompensationTooltip(cls, bonusComp, vehicle, tooltipData):
        specialArgs = {'labelBefore': '',
         'iconAfter': backport.image(R.images.gui.maps.icons.quests.bonuses.big.gold()),
         'labelAfter': bonusComp.getIconLabel(),
         'bonusName': bonusComp.getName()}
        uiData = _getVehicleUIData(vehicle)
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


def getMultipleAwardsBonusPacker(productCode):
    tokenBonus = _MultiAwardTokenBonusUIPacker(productCode)
    mapping = getDefaultBonusPackersMap()
    mapping.update({'vehicles': _MultiAwardVehiclesBonusUIPacker(),
     'tmanToken': TmanTemplateBonusPacker(),
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
