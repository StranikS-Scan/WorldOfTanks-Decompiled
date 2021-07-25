# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/awards/packers.py
import logging
import typing
from WebBrowser import getWebCache
from adisp import async, process
from constants import RentType, OFFER_TOKEN_PREFIX
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.awards.reward_model import RewardModel, RentTypeEnum
from gui.impl.lobby.awards.tooltip import VEH_FOR_CHOOSE_ID
from gui.impl.lobby.offers import getGfImagePath
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.missions.packers.bonus import VehiclesBonusUIPacker, getDefaultBonusPackersMap, TokenBonusUIPacker, BaseBonusUIPacker, AsyncBonusUIPacker, VEHICLE_RENT_ICON_POSTFIX, BACKPORT_TOOLTIP_CONTENT_ID
from gui.shared.utils.functions import makeTooltip
from gui.wgnc.image_notification_helper import WebImageHelper
from helpers import dependency, int2roman
from skeletons.gui.cdn import IPurchaseCache
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import VehiclesBonus, TokensBonus
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.impl.backport import TooltipData
    from gui.cdn.controller import _PurchaseDescriptor
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
    displayRentData = None
    hasRent = False
    for offer in offers:
        for gift in offer.getAllGifts():
            if gift.isVehicle:
                vehicles.append(gift.bonus.displayedItem.intCD)
                if gift.rentType != RentType.NO_RENT:
                    hasRent = True
                    newRentData = (gift.rentType, gift.rentValue)
                    if displayRentData is None:
                        displayRentData = newRentData
                    elif displayRentData != newRentData:
                        return (vehicles, hasRent, None)

    return (vehicles, hasRent, displayRentData)


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

    @async
    @process
    def asyncPack(self, bonus, callback=None):
        purchase = yield self.__purchaseCache.requestPurchaseByID(self.__productID)
        result = []
        bonusTokens = bonus.getTokens()
        for tID in bonusTokens.iterkeys():
            if tID.startswith(OFFER_TOKEN_PREFIX):
                offers = self.__offersProvider.getAvailableOffersByToken(tID)
                if not offers:
                    continue
                vehicles, _, rentData = _getOffersTokenStateData(offers)
                model = RewardModel()
                if vehicles:
                    model.setIsVehicleOnChoice(True)
                if rentData:
                    model.setVehicleRentType(_convertRentType(rentData[0]))
                    model.setVehicleRentValue(rentData[1])
            else:
                model = RewardModel()
            self._packCommon(bonus, model)
            tokenData = purchase.getTokenData(tID)
            smallImglocalPath = yield WebImageHelper(_LOCAL_FOLDER_NAME).getLocalPath(tokenData.imgSmall)
            bigImglocalPath = yield WebImageHelper(_LOCAL_FOLDER_NAME).getLocalPath(tokenData.imgBig)
            if bigImglocalPath:
                model.setIconBig(getGfImagePath(getWebCache().getRelativeFromAbsolute(bigImglocalPath)))
            if smallImglocalPath:
                model.setIconSmall(getGfImagePath(getWebCache().getRelativeFromAbsolute(smallImglocalPath)))
            result.append(model)

        callback(result)

    @async
    @process
    def asyncGetToolTip(self, bonus, callback=None):
        yield lambda callback: callback(True)
        result = []
        bonusTokens = bonus.getTokens()
        for tID in bonusTokens.iterkeys():
            if tID.startswith(OFFER_TOKEN_PREFIX):
                offers = self.__offersProvider.getAvailableOffersByToken(tID)
                if not offers:
                    continue
                vehicles, hasRent, _ = _getOffersTokenStateData(offers)
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
                _, hasRent, _ = _getOffersTokenStateData(offers)
                if hasRent:
                    result.append(VEH_FOR_CHOOSE_ID)
                    continue
            result.append(super(_MultiAwardTokenBonusUIPacker, cls)._getContentId(bonus))

        return result


class _MultiAwardVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, isRent, label):
        model = RewardModel()
        gpRentType, rentValue = bonus.getRentInfo()
        model.setVehicleRentType(_convertRentType(gpRentType))
        model.setVehicleRentValue(rentValue)
        model.setName(bonus.getName() + VEHICLE_RENT_ICON_POSTFIX if isRent else bonus.getName())
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(label)
        vehicle = bonus.getVehicles()[0][0]
        vehIconName = getIconResourceName(getNationLessName(vehicle.name))
        model.setUserName(vehicle.userName)
        model.setIcon(vehIconName)
        model.setVehicleLevel(vehicle.level)
        model.setVehicleType(vehicle.type)
        model.setIsFromStorage(vehicle.isInInventory)
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
    mapping = getDefaultBonusPackersMap()
    for k, packer in mapping.iteritems():
        if isinstance(packer, TokenBonusUIPacker):
            mapping[k] = _MultiAwardTokenBonusUIPacker(productCode)

    mapping['vehicles'] = _MultiAwardVehiclesBonusUIPacker()
    return AsyncBonusUIPacker(mapping)


@async
@process
def packBonusModelAndTooltipData(bonuses, productCode, callback=None):
    bonusIndexTotal = 0
    tooltipData = {}
    bonusModelsList = []
    yield lambda callback: callback(True)
    packer = getMultipleAwardsBonusPacker(productCode)
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = yield packer.requestData(bonus)
            bonusTooltipList = []
            bonusContentIdList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = yield packer.requestToolTip(bonus)
                bonusContentIdList = packer.getContentId(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusModelsList.append(item)
                if tooltipData is not None:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    if bonusTooltipList:
                        tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    if bonusContentIdList:
                        item.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
                    bonusIndexTotal += 1

    callback((bonusModelsList, tooltipData))
    return
