# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/vehicle.py
import logging
from itertools import chain
import typing
import constants
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockProps
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import getItemUnlockPricesVO, getItemRestorePricesVO, getItemSellPricesVO
from gui.shared.gui_items.gui_item_economics import getMinRentItemPrice, ItemPrice
from gui.shared.formatters import text_styles, moneyWithIcon, getItemPricesVO
from gui.shared.formatters.time_formatters import RentLeftFormatter, getTimeLeftInfo
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.Tankman import Tankman, getRoleUserName, CrewTypes, NO_TANKMAN
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from gui.shared.gui_items.Vehicle import Vehicle, getBattlesLeft, getTypeBigIconPath
from gui.shared.gui_items.fitting_item import RentalInfoProvider
from gui.shared.items_parameters import RELATIVE_PARAMS, params_helper
from gui.shared.items_parameters import formatters as param_formatter
from gui.shared.items_parameters.comparator import PARAM_STATE
from gui.shared.items_parameters.params_helper import SimplifiedBarVO
from gui.shared.money import Currency
from gui.shared.tooltips import formatters, ToolTipBaseData
from gui.shared.tooltips import getComplexStatus, getUnlockPrice, TOOLTIP_TYPE
from gui.shared.tooltips.common import BlocksTooltipData, makeCompoundPriceBlock, CURRENCY_SETTINGS
from gui.shared.utils import MAX_STEERING_LOCK_ANGLE, WHEELED_SWITCH_TIME, WHEELED_SPEED_MODE_SPEED, SHOT_DISPERSION_ANGLE, DUAL_GUN_CHARGE_TIME, TURBOSHAFT_SPEED_MODE_SPEED, ROCKET_ACCELERATION_SPEED_LIMITS, DUAL_ACCURACY_COOLING_DELAY
from gui.impl.lobby.crew.tooltips.vehicle_params_tooltip_view import BaseVehicleParamsTooltipView, BaseVehicleAdvancedParamsTooltipView, VehicleAdvancedParamsTooltipView, VehicleAvgParamsTooltipView
from helpers import i18n, time_utils, int2roman, dependency
from helpers.i18n import makeString as _ms
from renewable_subscription_common.settings_constants import WotPlusState
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import ITradeInController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import List, Tuple
    from gui.shared.tooltips.contexts import ExtendedAwardContext
_logger = logging.getLogger(__name__)
_EQUIPMENT = 'equipment'
_OPTION_DEVICE = 'optionalDevice'
_BATTLE_BOOSTER = 'battleBooster'
_IS_SENIORITY = 'isSeniority'
_HIDE_STATUS = 'hideStatus'
_ARTEFACT_TYPES = (_EQUIPMENT, _OPTION_DEVICE)
_SKILL_BONUS_TYPE = 'skill'
_PERK_BONUS_TYPE = 'perk'
_ROLE_BONUS_TYPE = 'role'
_EXTRA_BONUS_TYPE = 'extra'
_TOOLTIP_MIN_WIDTH = 420
_TOOLTIP_MAX_WIDTH = 460
_TOOLTIP_ANNOUNCEMENT_MAX_WIDTH = 310
_CREW_TOOLTIP_PARAMS = {Tankman.ROLES.COMMANDER: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_RECONNAISSANCE,
                           'commanderPercents': '10%',
                           'crewPercents': '1%'},
 Tankman.ROLES.GUNNER: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_FIREPOWER},
 Tankman.ROLES.DRIVER: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_MOBILITY},
 Tankman.ROLES.RADIOMAN: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_RECONNAISSANCE},
 Tankman.ROLES.LOADER: {'paramName': TOOLTIPS.VEHICLEPREVIEW_CREW_INFLUENCE_FIREPOWER}}

def _makeModuleFitTooltipError(reason):
    return '#tooltips:moduleFits/{}'.format(reason)


_SHORTEN_TOOLTIP_CASES = ('shopVehicle',)

class VehicleInfoTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wotPlusController = dependency.descriptor(IWotPlusController)
    _LEFT_PADDING = 20
    _RIGHT_PADDING = 20

    def __init__(self, context):
        super(VehicleInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self.item = None
        self._setContentMargin(top=0, left=0, bottom=12, right=20)
        self._setMargins(10, 15)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        items = super(VehicleInfoTooltipData, self)._packBlocks()
        vehicle = self.item
        statsConfig = self.context.getStatsConfiguration(vehicle)
        paramsConfig = self.context.getParamsConfiguration(vehicle)
        statusConfig = self.context.getStatusConfiguration(vehicle)
        leftPadding = self._LEFT_PADDING
        rightPadding = self._RIGHT_PADDING
        bottomPadding = 12
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        valueWidth = 77
        textGap = -2
        headerItems = [formatters.packBuildUpBlockData(HeaderBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct(), padding=leftRightPadding, blockWidth=410), formatters.packBuildUpBlockData(self._getCrewIconBlock(), gap=2, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(top=34, right=0), blockWidth=20)]
        headerBlockItems = [formatters.packBuildUpBlockData(headerItems, layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, padding=formatters.packPadding(bottom=-16))]
        telecomBlock = TelecomBlockConstructor(vehicle, valueWidth, leftPadding, rightPadding).construct()
        if telecomBlock:
            headerBlockItems.append(formatters.packBuildUpBlockData(telecomBlock, padding=leftRightPadding))
        self.__createStatusBlock(vehicle, headerBlockItems, statsConfig, paramsConfig, valueWidth)
        items.append(formatters.packBuildUpBlockData(headerBlockItems, gap=-4, padding=formatters.packPadding(bottom=-12)))
        if vehicle.isWotPlus:
            wotPlusBlock, linkage = WotPlusBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct()
            if wotPlusBlock:
                items.append(formatters.packBuildUpBlockData(wotPlusBlock, linkage=linkage, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=0, bottom=0)))
        if vehicle.isEarnCrystals and statsConfig.showEarnCrystals:
            crystalBlock, linkage = CrystalBlockConstructor(vehicle, statsConfig, leftPadding, rightPadding).construct()
            if crystalBlock:
                items.append(formatters.packBuildUpBlockData(crystalBlock, linkage=linkage, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=-3, bottom=-3)))
        simplifiedStatsBlock = SimplifiedStatsBlockConstructor(vehicle, paramsConfig, leftPadding, rightPadding).construct()
        if simplifiedStatsBlock:
            items.append(formatters.packBuildUpBlockData(simplifiedStatsBlock, gap=-4, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=leftRightPadding))
        if not vehicle.isRotationGroupLocked:
            commonStatsBlock = CommonStatsBlockConstructor(vehicle, paramsConfig, valueWidth, leftPadding, rightPadding).construct()
            if commonStatsBlock:
                items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=textGap, padding=formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding, bottom=-3)))
        if self.context.getParams().get(_IS_SENIORITY, False):
            awardCrewAndHangarBlock = VehicleAdditionalItems(vehicle, paramsConfig, leftPadding, rightPadding, showVehicleSlot=True, crewLevel=100).construct()
            if awardCrewAndHangarBlock:
                items.append(formatters.packBuildUpBlockData(awardCrewAndHangarBlock))
        statsBlockConstructor = None
        if vehicle.isRotationGroupLocked:
            statsBlockConstructor = RotationLockAdditionalStatsBlockConstructor
        elif vehicle.isDisabledInRoaming:
            statsBlockConstructor = RoamingLockAdditionalStatsBlockConstructor
        elif vehicle.clanLock and vehicle.clanLock > time_utils.getCurrentTimestamp():
            statsBlockConstructor = ClanLockAdditionalStatsBlockConstructor
        if statsBlockConstructor is not None:
            items.append(formatters.packBuildUpBlockData(statsBlockConstructor(vehicle, paramsConfig, self.context.getParams(), valueWidth, leftPadding, rightPadding).construct(), gap=textGap, padding=blockPadding))
        priceBlock, invalidWidth = PriceBlockConstructor(vehicle, statsConfig, self.context.getParams(), valueWidth, leftPadding, rightPadding).construct()
        shouldBeCut = self.calledBy and self.calledBy in _SHORTEN_TOOLTIP_CASES or vehicle.isOnlyForEpicBattles or vehicle.isOnlyForClanWarsBattles
        if priceBlock and not shouldBeCut:
            self._setWidth(_TOOLTIP_MAX_WIDTH if invalidWidth else _TOOLTIP_MIN_WIDTH)
            items.append(formatters.packBuildUpBlockData(priceBlock, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, gap=5, padding=formatters.packPadding(left=98), layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL))
        if not vehicle.isRotationGroupLocked and not self.context.getParams().get(_HIDE_STATUS, False):
            statusBlock, operationError, _ = StatusBlockConstructor(vehicle, statusConfig).construct()
            if statusBlock and not (operationError and shouldBeCut):
                items.append(formatters.packBuildUpBlockData(statusBlock, padding=blockPadding, blockWidth=440))
            else:
                self._setContentMargin(bottom=bottomPadding)
        return items

    def _getCrewIconBlock(self):
        block = []
        vehicle = self.item
        crewSorted = sorted(vehicle.crew, key=lambda tankman: tankman[1], reverse=True)
        for _, tankman in crewSorted:
            tImg = RES_ICONS.MAPS_ICONS_MESSENGER_ICONCONTACTS
            tAlpha = 0.5 if tankman is not None else 0.25
            block.append(formatters.packImageBlockData(img=tImg, alpha=tAlpha))

        return block

    def __createStatusBlock(self, vehicle, items, statsConfig, paramsConfig, valueWidth):
        ctxParams = self.context.getParams()
        frontlineBlock = FrontlineRentBlockConstructor(vehicle, statsConfig, ctxParams, valueWidth - 1, leftPadding=20, rightPadding=20).construct()
        if frontlineBlock:
            items.append(formatters.packBuildUpBlockData(frontlineBlock, gap=-4, padding=formatters.packPadding(left=25, right=20, top=0, bottom=-11)))
        if vehicle.canTradeIn:
            items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_TRADE), value='', icon=ICON_TEXT_FRAMES.TRADE, valueWidth=valueWidth, padding=formatters.packPadding(left=-5, top=0, bottom=-10)))
        if not vehicle.isPremiumIGR and not frontlineBlock and vehicle.getRentPackage() and (vehicle.rentalIsOver or not vehicle.isRented):
            items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main('#tooltips:vehicle/rentAvailable'), value='', icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, valueWidth=valueWidth, padding=formatters.packPadding(left=-5, top=0, bottom=-10)))
        if statsConfig.rentals and not vehicle.isPremiumIGR and not frontlineBlock and vehicle.isTelecomRent and not vehicle.rentExpiryState:
            rentInfo = vehicle.rentInfo
            timeKey, formattedTime = getTimeLeftInfo(rentInfo.getTimeLeft())
            rentText = R.strings.tooltips.vehicle.telecomRentalsRenting()
            items.append(formatters.packTextParameterBlockData(name=text_styles.main(backport.text(rentText)), value='', valueWidth=valueWidth + 18))
            if formattedTime:
                items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.gold(backport.text(R.strings.tooltips.vehicle.telecomRental.remainingTime.dyn(timeKey)()) % {'time': formattedTime}), value='', icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, gap=0, valueWidth=valueWidth, padding=formatters.packPadding(left=2, bottom=-10)))
        if statsConfig.rentals and not vehicle.isPremiumIGR and not frontlineBlock and not vehicle.isTelecomRent:
            if statsConfig.futureRentals:
                rentLeftKey = '#tooltips:vehicle/rentLeftFuture/%s'
                rentInfo = RentalInfoProvider(time=ctxParams.get('rentExpiryTime'), battles=ctxParams.get('rentBattlesLeft'), wins=ctxParams.get('rentWinsLeft'), seasonRent=ctxParams.get('rentSeason'), isRented=True)
            else:
                rentLeftKey = '#tooltips:vehicle/rentLeft/%s'
                rentInfo = vehicle.rentInfo
            descrStr = RentLeftFormatter(rentInfo).getRentLeftStr(rentLeftKey)
            leftStr = ''
            rentTimeLeft = rentInfo.getTimeLeft()
            if rentTimeLeft:
                _, formattedTime = getTimeLeftInfo(rentTimeLeft)
                leftStr = str(formattedTime)
            elif rentInfo.battlesLeft:
                leftStr = str(rentInfo.battlesLeft)
            elif rentInfo.winsLeft > 0:
                leftStr = str(rentInfo.winsLeft)
            if descrStr or leftStr:
                items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(descrStr), value=text_styles.expText(leftStr), icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, gap=0, valueWidth=valueWidth, padding=formatters.packPadding(left=2, bottom=-10)))
        if statsConfig.showRankedBonusBattle:
            items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(backport.text(R.strings.tooltips.vehicle.rankedBonusBattle())), value='', icon=ICON_TEXT_FRAMES.BONUS_BATTLE, iconYOffset=2, valueWidth=valueWidth, gap=0, padding=formatters.packPadding(left=0, top=-2, bottom=5)))
        if statsConfig.dailyXP and not vehicle.isWotPlus:
            attrs = self.__itemsCache.items.stats.attributes
            if attrs & constants.ACCOUNT_ATTR.DAILY_MULTIPLIED_XP and vehicle.dailyXPFactor > 0:
                dailyXPText = text_styles.main(text_styles.expText(''.join(('x', backport.getIntegralFormat(vehicle.dailyXPFactor)))))
                items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_DAILYXPFACTOR), value=dailyXPText, icon=ICON_TEXT_FRAMES.DOUBLE_XP_FACTOR, iconYOffset=2, valueWidth=valueWidth + 1, gap=0, padding=formatters.packPadding(left=2, top=-2, bottom=5)))
        if statsConfig.restorePrice:
            if vehicle.isRestorePossible() and vehicle.hasLimitedRestore():
                timeKey, formattedTime = getTimeLeftInfo(vehicle.restoreInfo.getRestoreTimeLeft(), None)
                items.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(''.join(('#tooltips:vehicle/restoreLeft/', timeKey))), value=text_styles.stats(formattedTime), icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, gap=0, valueWidth=valueWidth, padding=formatters.packPadding(left=0, bottom=-10)))
        return


class ExtendedVehicleInfoTooltipData(VehicleInfoTooltipData):

    def _packBlocks(self, *args, **kwargs):
        blocks = super(ExtendedVehicleInfoTooltipData, self)._packBlocks(*args, **kwargs)
        context = self.context
        params = context.getParams()
        showCrew = params.get('showCrew', False)
        showVehicleSlot = params.get('showVehicleSlot', False)
        if showCrew or showVehicleSlot:
            vehicle = self.item
            awardCrewAndHangarBlock = VehicleAdditionalItems(vehicle, self.context.getParamsConfiguration(vehicle), self._LEFT_PADDING, self._RIGHT_PADDING, showVehicleSlot, params.get('tmanRoleLevel', CrewTypes.SKILL_100) if showCrew else VehicleAdditionalItems.NO_CREW, params.get('allModulesAvailable', False)).construct()
            if awardCrewAndHangarBlock:
                blocks.append(formatters.packBuildUpBlockData(awardCrewAndHangarBlock))
        showDiscount = params.get('showDiscount', False)
        if showDiscount:
            discountTooltip = R.strings.winback.vehicleDiscountRewardTooltip
            description = text_styles.main(backport.text(discountTooltip.description(), research=text_styles.stats(backport.text(discountTooltip.description.research())), purchase=text_styles.stats(backport.text(discountTooltip.description.purchase()))))
            blocks.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.winback.tooltip.info()), desc=description, imgPadding=formatters.packPadding(left=20, top=4, right=10)))
        return blocks


class VehicleAnnouncementParametersTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleAnnouncementParametersTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setWidth(_TOOLTIP_ANNOUNCEMENT_MAX_WIDTH)

    def _packBlocks(self, *args, **kwargs):
        announcement = self.context.buildItem(*args, **kwargs)
        items = super(VehicleAnnouncementParametersTooltipData, self)._packBlocks()
        items.append(formatters.packTextBlockData(text_styles.main(_ms(announcement.tooltip))))
        return items


class BaseVehicleParametersTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(BaseVehicleParametersTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)

    @staticmethod
    def getTooltipView():
        return BaseVehicleParamsTooltipView

    def getDisplayableData(self, paramName, *args, **kwargs):
        tooltipView = self.getTooltipView()
        return DecoratedTooltipWindow(tooltipView(paramName, self.context, self.readyForAdvanced(paramName)), useDecorator=False)

    @staticmethod
    def readyForAdvanced(*args, **_):
        return param_formatter.isRelativeParameter(args[0])


class BaseVehicleAdvancedParametersTooltipData(BaseVehicleParametersTooltipData):

    @staticmethod
    def getTooltipView():
        return BaseVehicleAdvancedParamsTooltipView


class VehicleAdvancedParametersTooltipData(BaseVehicleParametersTooltipData):

    @staticmethod
    def getTooltipView():
        return VehicleAdvancedParamsTooltipView


class VehicleAvgParameterTooltipData(BaseVehicleParametersTooltipData):

    @staticmethod
    def getTooltipView():
        return VehicleAvgParamsTooltipView


class DefaultCrewMemberTooltipData(BlocksTooltipData):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(DefaultCrewMemberTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setWidth(360)
        self._setMargins(13, 13)

    def _packBlocks(self, tankmanID, slotIdx):
        blocks = []
        if tankmanID == NO_TANKMAN:
            roles = list(self.context.getVehicle().descriptor.type.crewRoles[slotIdx])
        else:
            roles = list(self.__itemsCache.items.getTankman(tankmanID).vehicleNativeDescr.type.crewRoles[slotIdx])
        mainRole = roles[0]
        bodyStr = '{}/{}'.format(TOOLTIPS.VEHICLEPREVIEW_CREW, mainRole)
        crewParams = {k:text_styles.neutral(v) for k, v in _CREW_TOOLTIP_PARAMS[mainRole].iteritems()}
        blocks.append(formatters.packTitleDescBlock(text_styles.highTitle(ITEM_TYPES.tankman_roles(mainRole)), text_styles.main(_ms(bodyStr, **crewParams))))
        roles.remove(mainRole)
        if roles:
            rolesStr = ', '.join([ text_styles.stats(_ms(ITEM_TYPES.tankman_roles(r))) for r in roles ])
            blocks.append(formatters.packTextBlockData(text_styles.main(_ms(TOOLTIPS.VEHICLEPREVIEW_CREW_ADDITIONALROLES, roles=rolesStr))))
        return blocks


class VehiclePreviewCrewMemberTooltipData(DefaultCrewMemberTooltipData):

    def __init__(self, context):
        super(VehiclePreviewCrewMemberTooltipData, self).__init__(context)
        self._setWidth(295)

    def _packBlocks(self, role, tankmanID, slotIdx, name, vehicleName, icon, description, skillsItems, *args, **kwargs):
        blocks = []
        defaultBlocks = super(VehiclePreviewCrewMemberTooltipData, self)._packBlocks(tankmanID, slotIdx)
        roleStr = getRoleUserName(role)
        if name and icon:
            bodyStr = '{}, {}'.format(roleStr, vehicleName)
            blocks.append(formatters.packImageTextBlockData(title=text_styles.highTitle(name), desc=text_styles.main(bodyStr)))
            blocks.append(formatters.packImageBlockData(img=icon, padding=formatters.packPadding(left=63)))
            blocks.append(formatters.packSeparatorBlockData())
            if description:
                blocks.append(formatters.packTextBlockData(text_styles.main(description), useHtml=True, padding=formatters.packPadding(top=20, bottom=7)))
        else:
            blocks.extend(defaultBlocks)
        if skillsItems:
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.VEHICLEPREVIEW_TANKMAN_SKILLSTITLE), padding=formatters.packPadding(top=10, bottom=10)))
            for skillItem in skillsItems:
                blocks.append(formatters.packImageTextBlockData(img=skillItem[0], title=text_styles.main(skillItem[1]), txtPadding=formatters.packPadding(left=10), titleAtMiddle=True))

        return [formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=10))]


class VehicleTradeInTooltipData(ToolTipBaseData):
    tradeIn = dependency.descriptor(ITradeInController)

    def __init__(self, context):
        super(VehicleTradeInTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)

    def getDisplayableData(self, *args, **kwargs):
        vehicle = self.context.buildItem(*args, **kwargs)
        tradeInDiscounts = self.tradeIn.getTradeInDiscounts(vehicle)
        if tradeInDiscounts is None:
            discount = i18n.makeString(TOOLTIPS.TRADE_NODISCOUNT)
        else:
            discountValue = moneyWithIcon(tradeInDiscounts.maxDiscountPrice, currType=Currency.GOLD)
            if tradeInDiscounts.hasMultipleTradeOffs:
                discountValue = i18n.makeString(TOOLTIPS.TRADE_SEVERALDISCOUNTS, discountValue=discountValue)
            discount = i18n.makeString(TOOLTIPS.TRADE_DISCOUNT, discountValue=discountValue)
        return {'header': i18n.makeString(TOOLTIPS.TRADE_HEADER),
         'body': i18n.makeString(TOOLTIPS.TRADE_BODY, discount=discount)}


class VehicleTradeInPriceTooltipData(ToolTipBaseData):
    tradeIn = dependency.descriptor(ITradeInController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(VehicleTradeInPriceTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)

    def getDisplayableData(self, tradeInVehicleCD, tradeOffVehicleCD):
        if tradeInVehicleCD < 0:
            return {}
        tradeInVehicle = self.context.buildItem(tradeInVehicleCD)
        itemPrice = tradeInVehicle.buyPrices.itemPrice
        bodyParts = []
        if tradeInVehicle.buyPrices.itemPrice.isActionPrice():
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_OLDPRICE, gold=moneyWithIcon(itemPrice.defPrice, currType=Currency.GOLD)))
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_NEWPRICE, gold=moneyWithIcon(itemPrice.price, currType=Currency.GOLD)))
        else:
            bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_PRICE, gold=moneyWithIcon(itemPrice.price, currType=Currency.GOLD)))
        if tradeOffVehicleCD < 0:
            tradeOffVehicleName = i18n.makeString(TOOLTIPS.TRADE_VEHICLE_NOVEHICLE)
            resultPrice = itemPrice.price
        else:
            tradeOffVehicle = self.context.buildItem(tradeOffVehicleCD)
            tradeOffVehicleName = tradeOffVehicle.userName
            resultPrice = itemPrice.price - tradeOffVehicle.tradeOffPrice
        bodyParts.append(i18n.makeString(TOOLTIPS.TRADE_VEHICLE_TOCHANGE, vehicleName=text_styles.playerOnline(tradeOffVehicleName)))
        return {'header': i18n.makeString(TOOLTIPS.TRADE_VEHICLE_HEADER, vehicleName=tradeInVehicle.userName),
         'body': '\n'.join(bodyParts),
         'result': i18n.makeString(TOOLTIPS.TRADE_VEHICLE_RESULT, gold=moneyWithIcon(resultPrice, currType=Currency.GOLD))}


class VehicleStatusTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(VehicleStatusTooltipData, self).__init__(context, TOOLTIP_TYPE.VEHICLE)
        self._setWidth(346)

    def _packBlocks(self, *args, **kwargs):
        vehicle = self.context.buildItem(*args, **kwargs)
        items = super(VehicleStatusTooltipData, self)._packBlocks()
        statusConfig = self.context.getStatusConfiguration(vehicle)
        if not vehicle.isRotationGroupLocked:
            statusBlock, operationError, _ = SimpleFormattedStatusBlockConstructor(vehicle, statusConfig).construct()
            if statusBlock and not operationError:
                items.append(formatters.packBuildUpBlockData(statusBlock, padding=formatters.packPadding(bottom=-16)))
        return items


class VehicleTooltipBlockConstructor(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vehicle, configuration, leftPadding=20, rightPadding=20):
        self.vehicle = vehicle
        self.configuration = configuration
        self.leftPadding = leftPadding
        self.rightPadding = rightPadding

    def construct(self):
        return None


class HeaderBlockConstructor(VehicleTooltipBlockConstructor):

    def construct(self):
        block = []
        headerBlocks = []
        if self.vehicle.isElite:
            vehicleType = TOOLTIPS.tankcaruseltooltip_vehicletype_elite(self.vehicle.type)
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_ELITE_VEHICLE_BG_LINKAGE
        else:
            vehicleType = TOOLTIPS.tankcaruseltooltip_vehicletype_normal(self.vehicle.type)
            bgLinkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE
        userName = self.vehicle.userName
        nameStr = text_styles.highTitle(userName)
        typeStr = text_styles.main(vehicleType)
        icon = getTypeBigIconPath(self.vehicle.type, self.vehicle.isElite)
        leftOffset = 101
        description = text_styles.standard(backport.text(R.strings.tooltips.vehicle.level_and_type(), vehicleLevel=text_styles.stats(int2roman(self.vehicle.level)), vehicleType=typeStr))
        headerBlocks.append(formatters.packImageTextBlockData(title=nameStr, desc=description, descPadding=formatters.packPadding(top=7), img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-9, txtOffset=leftOffset, padding=formatters.packPadding(top=15, bottom=-15 if self.vehicle.isFavorite else -21)))
        if self.vehicle.role != constants.ROLE_TYPE.NOT_DEFINED:
            roleLabel = self.vehicle.roleLabel
            headerBlocks.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.menu.roleExp.roleLabel()) + ' ' + backport.text(R.strings.menu.roleExp.roleName.dyn(roleLabel)(), groupName=backport.text(R.strings.menu.roleExp.roleGroupName.dyn(roleLabel)()))), padding=formatters.packPadding(top=-9, left=leftOffset, bottom=9)))
        block.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=bgLinkage, padding=formatters.packPadding(left=-self.leftPadding)))
        return block


class CrystalBlockConstructor(VehicleTooltipBlockConstructor):

    def construct(self):
        block = []
        current, limit = self.vehicle.getCrystalsEarnedInfo()
        icon = backport.image(R.images.gui.maps.icons.library.crystal_23x22())
        linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_VIOLET_LINKAGE
        imgPaddingLeft = -4
        imgPaddingTop = 0
        if current == 0:
            limitStatus = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.common.description(), max=text_styles.stats(limit))
        elif current >= limit:
            daysLeft = time_utils.getServerRegionalDaysLeftInGameWeek() * time_utils.ONE_DAY
            timeLeft = daysLeft + time_utils.getDayTimeLeft()
            timeLeftStr = time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUESHORT, isRoundUp=True, removeLeadingZeros=True)
            limitStatus = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.limitReached.description(), timeLeft=text_styles.neutral(timeLeftStr))
            icon = backport.image(R.images.gui.maps.icons.library.time_icon())
            linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_GRAY_LINKAGE
            imgPaddingLeft = 4
            imgPaddingTop = 4
        else:
            limitStatus = backport.text(R.strings.tooltips.vehicleCrystal.limitStatus.progress.description(), current=text_styles.stats(current), max=limit)
        block.append(formatters.packImageTextBlockData(img=icon, desc=text_styles.main(limitStatus), imgPadding=formatters.packPadding(left=imgPaddingLeft, top=imgPaddingTop, right=6), padding=formatters.packPadding(left=54, top=2, bottom=2), titleAtMiddle=True))
        return (block, linkage)


class WotPlusBlockConstructor(VehicleTooltipBlockConstructor):
    __itemsCache = dependency.descriptor(IItemsCache)
    __wotPlusController = dependency.descriptor(IWotPlusController)

    def construct(self):
        blocks = []
        linkage = BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILD_BLOCK_YELLOW_LINKAGE
        state = self.__wotPlusController.getState()
        if state is WotPlusState.CANCELLED:
            expiryTime = self.__wotPlusController.getExpiryTime()
            localExpiryTime = time_utils.makeLocalServerTime(expiryTime)
            formattedDate = backport.getShortDateFormat(localExpiryTime)
            formattedHour = backport.getShortTimeFormat(localExpiryTime)
            formattedTime = '{}, {}'.format(formattedDate, formattedHour)
            blocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(backport.text(R.strings.tooltips.vehicle.wotPlusRenting.remainingTime()) % {'time': formattedTime}), value='', icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, gap=0, valueWidth=60, padding=formatters.packPadding(top=5, bottom=-15)))
        if state in [WotPlusState.CANCELLED, WotPlusState.ACTIVE]:
            attrs = self.__itemsCache.items.stats.attributes
            if attrs & constants.ACCOUNT_ATTR.DAILY_MULTIPLIED_XP and self.vehicle.dailyXPFactor > 0:
                dailyXPText = text_styles.main(text_styles.expText('x{}'.format(backport.getIntegralFormat(self.vehicle.dailyXPFactor))))
                blocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_DAILYXPFACTOR), value=dailyXPText, icon=ICON_TEXT_FRAMES.DOUBLE_XP_FACTOR, iconYOffset=2, valueWidth=60, gap=0, padding=formatters.packPadding(left=0, top=0, bottom=10)))
        else:
            blocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_WOTPLUSRENTING_INACTIVE), value='', icon=ICON_TEXT_FRAMES.RENTALS, iconYOffset=2, gap=0, valueWidth=60, padding=formatters.packPadding(left=0, top=0, bottom=-7)))
        blocks.append(formatters.packTextParameterBlockData(name=text_styles.stats(backport.text(R.strings.tooltips.vehicle.wotPlusRenting())), value='', valueWidth=0, padding=formatters.packPadding(left=0, top=0, bottom=10)))
        return (blocks, linkage)


class TelecomBlockConstructor(VehicleTooltipBlockConstructor):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehicle, valueWidth, leftPadding, rightPadding):
        super(TelecomBlockConstructor, self).__init__(vehicle, None, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        return

    def construct(self):
        if self.vehicle.isTelecom:
            telecomConfig = self.lobbyContext.getServerSettings().telecomConfig
            telecomBundleId = self.itemsCache.items.stats.getTelecomBundleId()
            provider = telecomConfig.getInternetProvider(telecomBundleId)
            providerLocRes = R.strings.menu.internet_provider.dyn(provider)
            telecomTextRes = R.strings.tooltips.vehicle.deal.telecom.main.dyn(provider, R.strings.tooltips.vehicle.deal.telecom.main.default)
            return [formatters.packTextBlockData(text=text_styles.main(backport.text(telecomTextRes(), tariff=backport.text(providerLocRes.tariff()) if providerLocRes else '', provider=backport.text(providerLocRes.name()) if providerLocRes else '')))]
        return []


class PriceBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, params, valueWidth, leftPadding, rightPadding):
        super(PriceBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._rentExpiryTime = params.get('rentExpiryTime')
        self._rentBattlesLeft = params.get('rentBattlesLeft')
        self._rentWinsLeft = params.get('rentWinsLeft')
        self._rentSeason = params.get('rentSeason')
        self._blueprintFragmentsCount = params.get('blueprintFragmentsCount', 0)
        self._customPrice = params.get('customPrice')

    def construct(self):
        xp = self.configuration.xp
        buyPrice = self.configuration.buyPrice
        sellPrice = self.configuration.sellPrice
        unlockPrice = self.configuration.unlockPrice
        techTreeNode = self.configuration.node
        minRentPrice = self.configuration.minRentPrice
        neededValue = 0
        actionPrc = 0
        block = []
        vehicle = self.vehicle
        isUnlocked = vehicle.isUnlocked
        isInInventory = vehicle.isInInventory
        isNextToUnlock = False
        parentCD = None
        if techTreeNode is not None:
            isNextToUnlock = bool(int(techTreeNode.state) & NODE_STATE_FLAGS.NEXT_2_UNLOCK)
            parentCD = int(techTreeNode.unlockProps.parentID) or None
        if xp:
            xpValue = vehicle.xp
            if isUnlocked and not vehicle.getRentPackage() or vehicle.isRestorePossible() or vehicle.isInInventory:
                xPText = text_styles.expTextBig(backport.getIntegralFormat(xpValue))
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_ELITEXPICONBIG if vehicle.isElite or vehicle.isPremium else RES_ICONS.MAPS_ICONS_LIBRARY_XPICONBIG_2
                xpBlock = [formatters.packTextBlockData(text_styles.main(TOOLTIPS.VEHICLE_XP)), formatters.packImageTextBlockData(title=xPText, img=icon, imgPadding=formatters.packPadding(left=0, top=4), imgAtLeft=False, snapImage=True, txtGap=-2, txtOffset=0, padding=formatters.packPadding(top=-4, bottom=0))]
                block.append(formatters.packBuildUpBlockData(xpBlock, blockWidth=150, padding=formatters.packPadding(bottom=-8)))
        if unlockPrice:
            isAvailable, cost, need, defCost, discount = getUnlockPrice(vehicle.intCD, parentCD, vehicle.level, self._blueprintFragmentsCount)
            if not isUnlocked and cost >= 0:
                neededValue = None
                if isAvailable and not isUnlocked and need > 0 and techTreeNode is not None:
                    neededValue = need
                block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.UNLOCK_PRICE, getItemUnlockPricesVO(UnlockProps(parentID=-1, unlockIdx=0, xpCost=cost, discount=-discount, xpFullCost=defCost, required=set()))))
        if minRentPrice and vehicle.isRentAvailable:
            if not (vehicle.isRented or vehicle.isRestorePossible() or vehicle.isPremiumIGR):
                minRentItemPrice = getMinRentItemPrice(vehicle)
                if minRentItemPrice is not None:
                    actionPrc = minRentItemPrice.getActionPrc()
                    currency = minRentItemPrice.getCurrency()
                    neededValue = _getNeedValue(minRentItemPrice.price, currency)
                    block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.getRentSetting(currency), getItemPricesVO(minRentItemPrice)))
        if sellPrice:
            if isInInventory and not (vehicle.isRentable or vehicle.isRented or vehicle.isTelecom):
                sellPrice = vehicle.sellPrices.itemPrice.price
                sellCurrency = sellPrice.getCurrency(byWeight=True)
                block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.SELL_PRICE, getItemSellPricesVO(sellCurrency, sellPrice)))
        if buyPrice and not vehicle.isWotPlus:
            if vehicle.isRestorePossible():
                price = vehicle.restorePrice
                currency = price.getCurrency()
                neededValue = _getNeedValue(price, currency)
                if isInInventory or not isInInventory and not isUnlocked and not isNextToUnlock:
                    neededValue = None
                block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.RESTORE_PRICE, getItemRestorePricesVO(price)))
            elif not isInInventory or vehicle.isRentable or vehicle.isRented and not (vehicle.isDisabledForBuy or vehicle.isPremiumIGR or vehicle.isTelecom):
                itemPrice = vehicle.buyPrices.itemPrice
                if self._customPrice:
                    itemPrice = ItemPrice(self._customPrice, itemPrice.defPrice)
                price = itemPrice.price
                currency = price.getCurrency()
                neededValue = _getNeedValue(price, currency)
                if isInInventory or not isInInventory and not isUnlocked and not isNextToUnlock:
                    neededValue = None
                itemPricesVO = getItemPricesVO(itemPrice)
                actionPrc = itemPrice.getActionPrc()
                for itemPriceVO in itemPricesVO:
                    if 'action' in itemPriceVO:
                        itemPriceVO['action'] = tuple(((c, -v) for c, v in itemPriceVO['action']))

                block.append(makeCompoundPriceBlock(CURRENCY_SETTINGS.getBuySetting(currency), itemPricesVO))
        notEnoughMoney = neededValue > 0
        hasAction = actionPrc > 0
        return (block, notEnoughMoney or hasAction)


class FrontlineRentBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, params, valueWidth, leftPadding, rightPadding):
        super(FrontlineRentBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._rentExpiryTime = params.get('rentExpiryTime')
        self._rentBattlesLeft = params.get('rentBattlesLeft')
        self._rentWinsLeft = params.get('rentWinsLeft')
        self._rentSeason = params.get('rentSeason')

    def construct(self):
        block = []
        rentals = self.configuration.rentals
        futureRentals = self.configuration.futureRentals
        paddings = formatters.packPadding(left=-5, bottom=4)
        if rentals and not self.vehicle.isPremiumIGR:
            if futureRentals:
                rentLeftKey = '#tooltips:vehicle/rentLeftFuture/%s'
                rentInfo = RentalInfoProvider(time=self._rentExpiryTime, battles=self._rentBattlesLeft, wins=self._rentWinsLeft, seasonRent=self._rentSeason, isRented=True)
            else:
                rentLeftKey = '#tooltips:vehicle/rentLeft/%s'
                rentInfo = self.vehicle.rentInfo
            if self.vehicle.isOnlyForEpicBattles:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(TOOLTIPS.VEHICLE_DEAL_EPIC_MAIN), value='', valueWidth=self._valueWidth, padding=paddings))
                if rentInfo.getActiveSeasonRent() is not None:
                    rentFormatter = RentLeftFormatter(rentInfo)
                    rentLeftInfo = rentFormatter.getRentLeftStr(rentLeftKey)
                    if rentLeftInfo and not rentInfo.isTelecomRent:
                        block.append(formatters.packTextParameterWithIconBlockData(name=text_styles.neutral(rentLeftInfo), value='', icon=ICON_TEXT_FRAMES.RENTALS, valueWidth=self._valueWidth, padding=paddings))
                return block
        return


class CommonStatsBlockConstructor(VehicleTooltipBlockConstructor):
    PARAMS = {VEHICLE_CLASS_NAME.LIGHT_TANK: ('enginePowerPerTon',
                                     'speedLimits',
                                     TURBOSHAFT_SPEED_MODE_SPEED,
                                     WHEELED_SPEED_MODE_SPEED,
                                     'chassisRotationSpeed',
                                     MAX_STEERING_LOCK_ANGLE,
                                     WHEELED_SWITCH_TIME,
                                     'circularVisionRadius'),
     VEHICLE_CLASS_NAME.MEDIUM_TANK: ('avgDamagePerMinute',
                                      'enginePowerPerTon',
                                      'speedLimits',
                                      TURBOSHAFT_SPEED_MODE_SPEED,
                                      'chassisRotationSpeed'),
     VEHICLE_CLASS_NAME.HEAVY_TANK: ('avgDamage',
                                     'avgPiercingPower',
                                     'hullArmor',
                                     'turretArmor',
                                     DUAL_GUN_CHARGE_TIME),
     VEHICLE_CLASS_NAME.SPG: ('avgDamage', 'stunMinDuration', 'stunMaxDuration', 'reloadTimeSecs', 'aimingTime', 'explosionRadius'),
     VEHICLE_CLASS_NAME.AT_SPG: ('avgPiercingPower', 'shotDispersionAngle', 'avgDamagePerMinute', 'speedLimits', 'chassisRotationSpeed', 'switchTime'),
     'default': ('speedLimits', 'enginePower', 'chassisRotationSpeed')}
    __CONDITIONAL_PARAMS = ((ROCKET_ACCELERATION_SPEED_LIMITS, ('speedLimits', ROCKET_ACCELERATION_SPEED_LIMITS)),)

    def __init__(self, vehicle, configuration, valueWidth, leftPadding, rightPadding):
        super(CommonStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth

    def construct(self):
        paramsDict = params_helper.getParameters(self.vehicle)
        block = []
        highlightedParams = self.__getHighlightedParams()
        comparator = params_helper.similarCrewComparator(self.vehicle)
        if self.configuration.params and not self.configuration.simplifiedOnly:
            for paramName in self.__getShownParameters(paramsDict):
                paramInfo = comparator.getExtendedData(paramName)
                fmtValue = param_formatter.colorizedFormatParameter(paramInfo, param_formatter.BASE_SCHEME)
                if fmtValue is not None:
                    block.append(formatters.packTextParameterBlockData(name=param_formatter.formatVehicleParamName(paramName), value=fmtValue, valueWidth=self._valueWidth, padding=formatters.packPadding(left=-1), highlight=paramName in highlightedParams))

        if block:
            title = text_styles.middleTitle(backport.text(R.strings.tooltips.vehicleParams.common.title()))
            block.insert(0, formatters.packTextBlockData(title, padding=formatters.packPadding(bottom=8)))
        return block

    def __getHighlightedParams(self):
        serverSettings = dependency.instance(ISettingsCore).serverSettings
        descr = self.vehicle.descriptor
        params = []
        if descr.hasTurboshaftEngine and serverSettings.checkTurboshaftHighlights(increase=True):
            params.append(TURBOSHAFT_SPEED_MODE_SPEED)
        if descr.hasRocketAcceleration and serverSettings.checkRocketAccelerationHighlights(increase=True):
            params.append(ROCKET_ACCELERATION_SPEED_LIMITS)
        if descr.hasDualAccuracy and serverSettings.checkDualAccuracyHighlights(increase=True):
            params.append(DUAL_ACCURACY_COOLING_DELAY)
            params.append(SHOT_DISPERSION_ANGLE)
        return params

    def __getShownParameters(self, paramsDict):
        return chain([ p for p in self.PARAMS.get(self.vehicle.type, 'default') if p in paramsDict ], [ p for group in self.__CONDITIONAL_PARAMS if group[0] in paramsDict for p in group[1] ])


class VehicleAdditionalItems(VehicleTooltipBlockConstructor):
    NO_CREW = -1

    def __init__(self, vehicle, configuration, leftPadding=20, rightPadding=20, showVehicleSlot=False, crewLevel=NO_CREW, allModulesAvailable=False):
        super(VehicleAdditionalItems, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._crewLevelValue = crewLevel
        self._showVehicleSlot = showVehicleSlot
        self._allModulesAvailable = allModulesAvailable

    def construct(self):
        block = []
        if self.configuration.params:
            leftPaddingImg = 30
            leftPaddingTxt = 20
            block.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.VEHICLE_ADDITIONAL_HEADER), padding=formatters.packPadding(left=20)))
            if self._allModulesAvailable:
                block.append(formatters.packImageTextBlockData(title='', desc=text_styles.main(TOOLTIPS.VEHICLE_ALLMODULES_HEADER), img=RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_ALLMODULES, imgPadding=formatters.packPadding(left=leftPaddingImg, top=10), txtPadding=formatters.packPadding(left=leftPaddingTxt, top=20)))
            if self._crewLevelValue != self.NO_CREW:
                block.append(formatters.packImageTextBlockData(title='', desc=text_styles.main(_ms(TOOLTIPS.CUSTOMCREW_REFERRAL_BODY, value=self._crewLevelValue)), img=RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_TANKMEN, imgPadding=formatters.packPadding(left=leftPaddingImg, top=10), txtPadding=formatters.packPadding(left=leftPaddingTxt, top=20)))
            if self._showVehicleSlot:
                block.append(formatters.packImageTextBlockData(title='', desc=text_styles.main(TOOLTIPS.VEHICLE_HANGARSLOT_HEADER), img=RES_ICONS.MAPS_ICONS_QUESTS_BONUSES_SMALL_SLOTS, imgPadding=formatters.packPadding(left=leftPaddingImg, top=10), txtPadding=formatters.packPadding(left=leftPaddingTxt, top=20)))
        return block


class SimplifiedStatsBlockConstructor(VehicleTooltipBlockConstructor):

    def construct(self):
        block = []
        if self.configuration.params:
            comparator = params_helper.similarCrewComparator(self.vehicle)
            stockParams = params_helper.getParameters(self.itemsCache.items.getStockVehicle(self.vehicle.intCD))
            for paramName in RELATIVE_PARAMS:
                paramInfo = comparator.getExtendedData(paramName)
                fmtValue = param_formatter.colorizedFormatParameter(paramInfo, param_formatter.NO_BONUS_SIMPLIFIED_SCHEME)
                if fmtValue is not None:
                    buffIconSrc = ''
                    if self.vehicle.isInInventory:
                        buffIconSrc = param_formatter.getGroupPenaltyIcon(paramInfo, comparator)
                    delta = 0
                    state, diff = paramInfo.state
                    if state == PARAM_STATE.WORSE:
                        delta = -abs(diff)
                    block.append(formatters.packStatusDeltaBlockData(title=param_formatter.formatVehicleParamName(paramName), valueStr=fmtValue, statusBarData=SimplifiedBarVO(value=paramInfo.value, delta=delta, markerValue=stockParams[paramName]), buffIconSrc=buffIconSrc, padding=formatters.packPadding(left=76, top=8)))

        if block:
            block.insert(0, formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.tooltips.vehicleParams.simplified.title())), padding=formatters.packPadding(top=-4)))
        return block


class AdditionalStatsBlockConstructor(VehicleTooltipBlockConstructor):

    def __init__(self, vehicle, configuration, params, valueWidth, leftPadding, rightPadding):
        super(AdditionalStatsBlockConstructor, self).__init__(vehicle, configuration, leftPadding, rightPadding)
        self._valueWidth = valueWidth
        self._roleLevel = params.get('tmanRoleLevel')

    def construct(self):
        block = []
        if self.configuration.crew:
            totalCrewSize = len(self.vehicle.descriptor.type.crewRoles)
            if self.configuration.externalCrewParam and self._roleLevel is not None:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_CREW_AWARD, self._roleLevel)), value=text_styles.stats(str(totalCrewSize)), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-2)))
            elif self.vehicle.isInInventory and not self.configuration.externalCrewParam:
                currentCrewSize = len([ x for _, x in self.vehicle.crew if x is not None ])
                currentCrewSizeStr = str(currentCrewSize)
                if currentCrewSize < totalCrewSize:
                    currentCrewSizeStr = text_styles.error(currentCrewSizeStr)
                block.append(self._makeStatBlock(currentCrewSizeStr, totalCrewSize, TOOLTIPS.VEHICLE_CREW))
            else:
                block.append(formatters.packTextParameterBlockData(name=text_styles.main(_ms(TOOLTIPS.VEHICLE_CREW)), value=text_styles.stats(str(totalCrewSize)), valueWidth=self._valueWidth, padding=formatters.packPadding(left=-2)))
        return block

    def _makeStatBlock(self, current, total, text):
        return formatters.packTextParameterBlockData(name=text_styles.main(_ms(text)), value=text_styles.stats(str(current) + '/' + str(total)), valueWidth=self._valueWidth)


class LockAdditionalStatsBlockConstructor(AdditionalStatsBlockConstructor):

    def construct(self):
        block = super(LockAdditionalStatsBlockConstructor, self).construct()
        lockBlock = self._makeLockBlock()
        if lockBlock is not None:
            block.append(lockBlock)
        return block

    def _makeLockBlock(self):
        header = self._makeLockHeader()
        text = self._makeLockText()
        headerPadding = formatters.packPadding(left=77 + self.leftPadding, top=5)
        textPadding = formatters.packPadding(left=77 + self.leftPadding)
        headerBlock = formatters.packTextBlockData(header, padding=headerPadding)
        textBlock = formatters.packTextBlockData(text, padding=textPadding)
        return formatters.packBuildUpBlockData([headerBlock, textBlock], stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_LOCK_BG_LINKAGE, padding=formatters.packPadding(left=-17, top=20, bottom=0))

    def _makeLockHeader(self):
        return text_styles.warning(_ms(TOOLTIPS.TANKCARUSEL_LOCK_HEADER))

    def _makeLockText(self):
        pass


class RotationLockAdditionalStatsBlockConstructor(LockAdditionalStatsBlockConstructor):

    def _makeLockHeader(self):
        return text_styles.warning(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROTATION_HEADER, groupNum=self.vehicle.rotationGroupNum))

    def _makeLockText(self):
        return text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROTATION, battlesToUnlock=text_styles.stats(self.vehicle.rotationBattlesLeft), unlockedBy=text_styles.stats(', '.join((str(groupNum) for groupNum in self.vehicle.unlockedBy)))))


class RoamingLockAdditionalStatsBlockConstructor(LockAdditionalStatsBlockConstructor):

    def _makeLockText(self):
        return text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_ROAMING))


class ClanLockAdditionalStatsBlockConstructor(LockAdditionalStatsBlockConstructor):

    def _makeLockText(self):
        clanLockTime = self.vehicle.clanLock
        time = backport.getDateTimeFormat(clanLockTime)
        timeStr = text_styles.main(text_styles.concatStylesWithSpace(_ms(TOOLTIPS.TANKCARUSEL_LOCK_TO), time))
        return text_styles.concatStylesToMultiLine(timeStr, text_styles.main(_ms(TOOLTIPS.TANKCARUSEL_LOCK_CLAN)))


class StatusBlockConstructor(VehicleTooltipBlockConstructor):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def construct(self):
        block = []
        isClanLock = self.vehicle.clanLock or None
        isDisabledInRoaming = self.vehicle.isDisabledInRoaming
        if isClanLock or isDisabledInRoaming:
            return (block, False)
        else:
            if self.configuration.node is not None:
                result = self.__getTechTreeVehicleStatus(self.configuration, self.vehicle)
            elif self.configuration.isAwardWindow:
                result = None
            else:
                result = self.__getVehicleStatus(self.configuration.showCustomStates, self.vehicle)
            if result is not None:
                headerFormatter = self._getHeaderFormatter(result['level'])
                header = headerFormatter(result['header'])
                text = result['text']
                if text:
                    block.append(formatters.packTextBlockData(text=header))
                    block.append(formatters.packTextBlockData(text=text_styles.standard(text)))
                else:
                    block.append(formatters.packAlignedTextBlockData(header, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
            return (block, result and result.get('operationError') is not None, result)

    @classmethod
    def _getHeaderFormatter(cls, statusLevel):
        if statusLevel == Vehicle.VEHICLE_STATE_LEVEL.INFO:
            headerFormatter = text_styles.statInfo
        elif statusLevel == Vehicle.VEHICLE_STATE_LEVEL.CRITICAL:
            headerFormatter = text_styles.critical
        elif statusLevel == Vehicle.VEHICLE_STATE_LEVEL.WARNING:
            headerFormatter = text_styles.warning
        elif statusLevel == Vehicle.VEHICLE_STATE_LEVEL.ATTENTION:
            headerFormatter = text_styles.statusAttention
        elif statusLevel in (Vehicle.VEHICLE_STATE_LEVEL.RENTED, Vehicle.VEHICLE_STATE_LEVEL.RENTABLE):
            headerFormatter = text_styles.warning
        else:
            _logger.error('Unknown status type "%s"!', statusLevel)
            headerFormatter = text_styles.statInfo
        return headerFormatter

    def __getTechTreeVehicleStatus(self, config, vehicle):
        nodeState = int(config.node.state)
        tooltip, level = None, Vehicle.VEHICLE_STATE_LEVEL.WARNING
        parentCD = None
        if config.node is not None:
            parentCD = int(config.node.unlockProps.parentID) or None
        _, _, need2Unlock, _, _ = getUnlockPrice(vehicle.intCD, parentCD, vehicle.level)
        if not nodeState & NODE_STATE_FLAGS.UNLOCKED and not nodeState & NODE_STATE_FLAGS.COLLECTIBLE:
            if not nodeState & NODE_STATE_FLAGS.NEXT_2_UNLOCK:
                tooltip = TOOLTIPS.RESEARCHPAGE_VEHICLE_STATUS_PARENTMODULEISLOCKED
            elif need2Unlock > 0:
                tooltip = TOOLTIPS.RESEARCHPAGE_MODULE_STATUS_NOTENOUGHXP
            if tooltip is not None:
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
        else:
            if nodeState & NODE_STATE_FLAGS.IN_INVENTORY:
                return self.__getVehicleStatus(False, vehicle)
            mayObtain, reason = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
            if not mayObtain:
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                if GUI_ITEM_ECONOMY_CODE.isCurrencyError(reason):
                    tooltip = _makeModuleFitTooltipError(reason)
                else:
                    tooltip = TOOLTIPS.MODULEFITS_OPERATION_ERROR
        header, text = getComplexStatus(tooltip)
        return None if header is None and text is None else {'header': header,
         'text': text,
         'level': level}

    def __getVehicleStatus(self, showCustomStates, vehicle):
        if showCustomStates:
            isInInventory = vehicle.isInInventory
            level = Vehicle.VEHICLE_STATE_LEVEL.WARNING
            if not isInInventory and vehicle.hasRestoreCooldown() and vehicle.isHidden:
                timeKey, formattedTime = getTimeLeftInfo(self.vehicle.restoreInfo.getRestoreCooldownTimeLeft())
                return {'header': _ms('#tooltips:vehicleStatus/restoreCooldown/%s' % timeKey, time=formattedTime),
                 'text': '',
                 'level': level}
            isUnlocked = vehicle.isUnlocked
            mayObtain, reason = vehicle.mayObtainForMoney(self.itemsCache.items.stats.money)
            msg = None
            operationError = False
            if not isUnlocked:
                msg = 'notUnlocked'
            elif isInInventory:
                msg = 'inHangar'
            elif not mayObtain:
                level = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
                if reason == GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_GOLD:
                    msg = 'notEnoughGold'
                elif reason == GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_CREDITS:
                    msg = 'notEnoughCredits'
                else:
                    msg = 'operationError'
                    operationError = True
            if msg:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % msg)
                return {'header': header,
                 'text': text,
                 'level': level,
                 'operationError': operationError}
            return
        else:
            state, level = vehicle.getState()
            if state == Vehicle.VEHICLE_STATE.SERVER_RESTRICTION:
                return
            if state == Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % state, groupNum=vehicle.rotationGroupNum, battlesLeft=getBattlesLeft(vehicle))
            elif state == Vehicle.VEHICLE_STATE.DEAL_IS_OVER:
                telecomConfig = self.__lobbyContext.getServerSettings().telecomConfig
                telecomBundleId = self.itemsCache.items.stats.getTelecomBundleId()
                provider = telecomConfig.getInternetProvider(telecomBundleId)
                providerLocRes = R.strings.menu.internet_provider.dyn(provider)
                keyString = '#tooltips:vehicleStatus/{}'.format(state)
                if provider != '':
                    keyString = keyString + '/{}'.format(provider)
                header, text = getComplexStatus(keyString, provider=backport.text(providerLocRes.name()) if providerLocRes else '')
            else:
                header, text = getComplexStatus('#tooltips:vehicleStatus/%s' % state)
                if header is None and text is None:
                    return
            return {'header': header,
             'text': text,
             'level': level}


class SimpleFormattedStatusBlockConstructor(StatusBlockConstructor):

    @classmethod
    def _getHeaderFormatter(cls, _):
        return text_styles.middleTitle


def _getNeedValue(price, currency):
    itemsCache = dependency.instance(IItemsCache)
    money = itemsCache.items.stats.money
    neededValue = price.getSignValue(currency) - money.getSignValue(currency)
    return neededValue if neededValue > 0 else None
