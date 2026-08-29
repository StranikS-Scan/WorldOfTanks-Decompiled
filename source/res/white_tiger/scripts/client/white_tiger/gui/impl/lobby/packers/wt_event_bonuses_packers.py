# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/packers/wt_event_bonuses_packers.py
import logging
import typing
from collections import namedtuple
import constants
from constants import LOOTBOX_TOKEN_PREFIX, PREMIUM_ENTITLEMENTS
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import formatEliteVehicle
from gui.impl.backport import TooltipData, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_rewards.wt_vehicle_bonus_model import WtVehicleBonusModel
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.money import Currency
from gui.shared.missions.packers.bonus import BonusUIPacker, getDefaultBonusPackersMap, TokenBonusUIPacker, ItemBonusUIPacker, CustomizationBonusUIPacker, VehiclesBonusUIPacker, SimpleBonusUIPacker, BaseBonusUIPacker, GroupsBonusUIPacker, CrewBookBonusUIPacker, CrewSkinBonusUIPacker, GoodiesBonusUIPacker
from gui.shared.utils.functions import replaceHyphenToUnderscore, makeTooltip
from helpers import dependency, int2roman
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.gui.shared import IItemsCache
from shared_utils import first
from gui.server_events.formatters import parseComplexToken
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_INDICES
from skeletons.gui.customization import ICustomizationService
from white_tiger.gui.impl.lobby.packers import isStyle3D
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_portal_bonus_model import WtPortalBonusModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_portal_bonus_model import VehicleType
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import TokensBonus, CrewBooksBonus
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
_GroupedBonuses = namedtuple('_GroupedBonuses', ('main', 'additional', 'vehicle'))
_LootboxTooltip = namedtuple('_LootboxTooltip', ('tooltip', 'isSpecial', 'specialAlias', 'specialArgs', 'isHunterLootBox'))
_MAX_MAIN_BONUSES = 3
BOSS_ALL_BONUSES_ORDER = ('vehicles',
 'customizations',
 'battleToken',
 Currency.GOLD,
 Currency.CREDITS,
 'crewBooks',
 'goodies',
 PREMIUM_ENTITLEMENTS.PLUS,
 'items',
 'slots')
TICKET_UI_NAME = 'wtevent_ticket'

class WtItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        iconName = item.getGUIEmblemID()
        if item.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER:
            iconName += 'BattleBooster'
        model.setName(iconName)
        model.setValue(str(count))
        model.setLabel(item.userName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return WtPortalBonusModel()


class WtCustomizationBonusUIPacker(CustomizationBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return WtPortalBonusModel()

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = cls._getBonusModel()
        cls._packCommon(bonus, model)
        model.setValue(str(item.get('value', 0)))
        model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        customizationItem = bonus.getC11nItem(item)
        is3D = bool(isStyle3D(customizationItem))
        if is3D:
            model.setIcon('style_3d')
        else:
            model.setIcon(str(bonus.getC11nItem(item).itemTypeName))
        model.setIsCollected(is3D and customizationItem.inventoryCount > 0)
        model.setLabel(label)
        return model


class WTGoldPacker(SimpleBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(tooltip=makeTooltip(backport.text(R.strings.event.bonusTooltip.gold.header()), backport.text(R.strings.event.bonusTooltip.gold.body())))]


class WtSimpleBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return WtPortalBonusModel()


class WtGoodiesBonusUIPacker(GoodiesBonusUIPacker):

    @classmethod
    def _getBonusModel(cls):
        return WtPortalBonusModel()


def getWtEventBonusPacker():
    mapping = getDefaultBonusPackersMap()
    mapping.update({'items': WtItemBonusUIPacker(),
     'lootBoxToken': WtLootboxTokenBonusPacker(),
     'ticket': WtTicketTokenBonusPacker(),
     'customizations': WtCustomizationBonusUIPacker(),
     'stamp': WtStampTokenBonusPacker(),
     'mainPrizeDiscount': WtMainPrizeDiscountTokenBonusPacker,
     'vehicles': WtVehiclesBonusUIPacker(),
     'slots': WtSlotBonusPacker(),
     'tmanToken': WtTmanTemplateBonusPacker(),
     'groups': WTEventGroupsBonusUIPacker()})
    return BonusUIPacker(mapping)


def getWtHiddenCustomizationIconUIPacker():
    mapping = getWtEventBonusPacker().getPackers()
    mapping.update({'customizations': WtHiddenCustomizationIconUIPacker()})
    return BonusUIPacker(mapping)


class WTCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        for book, count in sorted(bonus.getItems()):
            if book is None or not count:
                continue
            return [cls._packSingleBonus(bonus, book, count)]

        return

    @classmethod
    def _getToolTip(cls, bonus):
        bookType = bonus.getBookType()
        return [createTooltipData(tooltip=makeTooltip(backport.text(R.strings.tooltips.crewBooks.storage.filters.dyn(bookType).title()), backport.text(R.strings.tooltips.WTAnyCrewbook.info())))]


class WTCrewSkinBonusUIPacker(CrewSkinBonusUIPacker):
    pass


class WtSlotBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        label = cls._getLocalizedBonusName(bonus.getName(), bonus.getValue())
        return [cls._packSingleBonus(bonus, label if label else '')]

    @classmethod
    def _getLocalizedBonusName(cls, name, count):
        labelStr = R.strings.quests.bonusName.slots if count > 1 else R.strings.event.bonusName.slots
        if labelStr.exists():
            return backport.text(labelStr())
        _logger.warning('Localized text for the label for %s reward was not found', name)


class WtHiddenCustomizationIconUIPacker(WtCustomizationBonusUIPacker):

    @classmethod
    def _getIcon(cls, item):
        itemTypeName = cls._getTypeIcon(item)
        return itemTypeName


class WtTokenBonusPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = []
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if cls._isSuitable(tokenID, token):
                model = cls._getBonusModel()
                cls._packToken(token, model)
                result.append(model)

        return result

    @classmethod
    def _isSuitable(cls, tokenID, token):
        return False

    @classmethod
    def _packToken(cls, token, model):
        pass

    @classmethod
    def _getToolTip(cls, bonus):
        result = super(WtTokenBonusPacker, cls)._getToolTip(bonus)
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if cls._isSuitable(tokenID, token):
                result.append(cls._packTokenTooltip(token))

        return result

    @classmethod
    def _packTokenTooltip(cls, token):
        pass

    @classmethod
    def _getBonusModel(cls):
        return WtPortalBonusModel()


class WtLootboxTokenBonusPacker(WtTokenBonusPacker):
    _itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def _isSuitable(cls, tokenID, token):
        return tokenID.startswith(LOOTBOX_TOKEN_PREFIX) and token.count >= 0 and cls.__isBoxAvailable(tokenID)

    @classmethod
    def _packToken(cls, token, model):
        lootBox = cls._itemsCache.items.tokens.getLootBoxByTokenID(token.id)
        if lootBox is not None:
            model.setName(lootBox.getType())
            model.setLabel(lootBox.getUserName())
            if token.count > 1:
                model.setValue(str(token.count))
            lootBoxRes = R.views.white_tiger.lobby.tooltips.LootBoxTooltipView
            if not lootBoxRes.exists():
                return
            model.setTooltipContentId(str(lootBoxRes()))
        return

    @classmethod
    def _packTokenTooltip(cls, token):
        lootBox = cls._itemsCache.items.tokens.getLootBoxByTokenID(token.id)
        return createTooltipData(specialAlias=TOOLTIPS_CONSTANTS.EVENT_LOOTBOX, specialArgs=(lootBox.getType(),))

    @classmethod
    def _getToolTip(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        for tokenID, token in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            tokenType = cls._getTokenBonusType(tokenID, complexToken)
            if tokenType == '':
                continue
            tooltip = cls.__packLootboxToolTip(complexToken, token)
            result.append(tooltip)

        return result

    @classmethod
    def _getTooltipsPackers(cls):
        return {constants.LOOTBOX_TOKEN_PREFIX: cls.__packLootboxToolTip}

    @classmethod
    def __packLootboxToolTip(cls, complexToken, token):
        lootBox = cls._itemsCache.items.tokens.getLootBoxByTokenID(token.id)
        return _LootboxTooltip(tooltip=None, isSpecial=None, specialAlias=TOOLTIPS_CONSTANTS.EVENT_LOOTBOX, specialArgs=None, isHunterLootBox=lootBox.getType() == WhiteTigerLootBoxes.WT_HUNTER)

    @classmethod
    def _getContentId(cls, bonus):
        result = []
        bonusTokens = bonus.getTokens()
        for token in bonusTokens:
            if token.startswith(constants.LOOTBOX_TOKEN_PREFIX):
                lootBoxRes = R.views.white_tiger.lobby.tooltips.LootBoxTooltipView
                if lootBoxRes.exists():
                    result.append(lootBoxRes())
                else:
                    result.append(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent())
            result.append(R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent())

        return result

    @classmethod
    def __isBoxAvailable(cls, tokenID):
        return cls._itemsCache.items.tokens.getLootBoxByTokenID(tokenID) is not None


class WtTicketTokenBonusPacker(WtTokenBonusPacker):
    _gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    @classmethod
    def _isSuitable(cls, tokenID, token):
        isSuitable = tokenID == cls._gameEventCtrl.getConfig().ticketToken
        return isSuitable

    @classmethod
    def _packToken(cls, token, model):
        tokenName = token.id.replace(':', '_')
        model.setName(tokenName)
        model.setLabel(backport.text(R.strings.white_tiger.ticketTooltip.title()))
        model.setTooltipContentId(str(R.views.white_tiger.lobby.tooltips.TicketTooltipView()))
        model.setValue(str(token.count))

    @classmethod
    def _packTokenTooltip(cls, token):
        return createTooltipData(specialAlias=TOOLTIPS_CONSTANTS.EVENT_BATTLES_TICKET)

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.white_tiger.lobby.tooltips.TicketTooltipView()]


class WtStampTokenBonusPacker(WtTokenBonusPacker):
    _gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    @classmethod
    def _isSuitable(cls, tokenID, token):
        return tokenID == cls._gameEventCtrl.getConfig().stamp

    @classmethod
    def _packToken(cls, token, model):
        model.setValue(str(token.count))
        stampNameArray = token.id.split(':')
        model.setName(stampNameArray[1] if len(stampNameArray) > 1 else token.id)
        model.setTooltipContentId(str(R.views.white_tiger.lobby.tooltips.StampTooltipView()))

    @classmethod
    def _packTokenTooltip(cls, token):
        return createTooltipData(specialAlias=TOOLTIPS_CONSTANTS.EVENT_STAMP, specialArgs=[])


class WtMainPrizeDiscountTokenBonusPacker(WtTokenBonusPacker):
    _gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    @classmethod
    def _isSuitable(cls, tokenID, token):
        return tokenID == cls._gameEventCtrl.getConfig().mainPrizeDiscountToken

    @classmethod
    def _packToken(cls, token, model):
        model.setValue(str(token.count))
        discountNameArray = token.id.split(':')
        discountName = discountNameArray[1] if len(discountNameArray) > 1 else token.id
        model.setName(discountName)
        discountTokenCount = cls._gameEventCtrl.getCurrentMainPrizeDiscountTokensCount()
        discount = discountTokenCount * cls._gameEventCtrl.getMainPrizeDiscountPerToken()
        model.setIcon(discountName + '_' + str(discount))
        model.setLabel(backport.text(R.strings.event.WTEventAwardsView.mainRewards.dyn(discountName)(), discount=discount))

    @classmethod
    def _packTokenTooltip(cls, token):
        return createTooltipData(specialAlias=TOOLTIPS_CONSTANTS.EVENT_MAIN_PRIZE_DISCOUNT, specialArgs=[])

    @classmethod
    def _getContentId(cls, bonus):
        return [R.views.white_tiger.lobby.tooltips.MainPrizeDiscountTooltipView()]


class WtVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _getLabel(cls, vehicle):
        return vehicle.userName

    @classmethod
    def _getCompensationPacker(cls):
        return WtCompensationBonusPacker()

    @classmethod
    def _packTooltip(cls, bonus, vehicle, vehInfo):
        compensation = bonus.compensation(vehicle, bonus)
        return first(cls._packCompensationTooltip(first(compensation), vehicle)) if bonus.compensation(vehicle, bonus) else super(WtVehiclesBonusUIPacker, cls)._packTooltip(bonus, vehicle, vehInfo)

    @classmethod
    def _packCompensationTooltip(cls, bonusComp, vehicle):
        tooltipDataList = super(WtVehiclesBonusUIPacker, cls)._packCompensationTooltip(bonusComp, vehicle)
        return [ cls.__convertCompensationTooltip(bonusComp, vehicle, tooltipData) for tooltipData in tooltipDataList ]

    @classmethod
    def __convertCompensationTooltip(cls, bonusComp, vehicle, _):
        normalizeVehicleName = getNationLessName(replaceHyphenToUnderscore(vehicle.name))
        vehicleIcon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(normalizeVehicleName)()
        specialArgs = {'iconBefore': backport.image(vehicleIcon),
         'labelBefore': '',
         'iconAfter': backport.image(R.images.gui.maps.icons.quests.bonuses.big.dyn(bonusComp.getName())()),
         'labelAfter': bonusComp.getIconLabel(),
         'bonusName': bonusComp.getName(),
         'vehicleName': vehicle.shortUserName,
         'vehicleType': formatEliteVehicle(vehicle.isElite, vehicle.type),
         'isElite': vehicle.isElite,
         'vehicleLvl': int2roman(vehicle.level)}
        return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_VEHICLE_COMPENSATION, specialArgs=specialArgs)

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = WtVehicleBonusModel()
        model.setName(bonus.getName())
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(cls._getLabel(vehicle))
        model.setType(vehicle.type)
        model.setLevel(vehicle.level)
        model.setSpecName(getNationLessName(vehicle.name))
        model.setNation(vehicle.nationName)
        model.setIsElite(vehicle.isElite)
        model.setIntCD(vehicle.intCD)
        if isRent:
            model.setRentBattles(bonus.getRentBattles(vehInfo))
        return model


class WtCompensationBonusPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = super(WtCompensationBonusPacker, cls)._packSingleBonus(bonus, label)
        compensationBonus = bonus.getCompensationReason()
        if compensationBonus is not None:
            vehicle = first([ vehicle for vehicle, _ in compensationBonus.getVehicles() ])
            model.setLabel(vehicle.shortUserName)
        return model

    @classmethod
    def _getBonusModel(cls):
        return BonusModel()


class LootBoxAwardsManager(BattlePassAwardsManager):

    @classmethod
    def processCompensation(cls, rewards):
        bonuses, goldBonuses = [], []
        totalCompensation = 0
        for reward in rewards:
            if reward.getName() == Currency.GOLD:
                goldBonuses.append(reward)
            bonuses.append(reward)
            if reward.getName() == 'vehicles':
                totalCompensation += sum(reward.getCompensation())

        if goldBonuses and totalCompensation > 0:
            totalGold = sum((bonus.getValue() for bonus in goldBonuses))
            if totalGold > totalCompensation:
                goldBonus = first(goldBonuses)
                goldBonus.setValue(totalGold - totalCompensation)
                bonuses.append(goldBonus)
        else:
            bonuses.extend(goldBonuses)
        return bonuses

    @classmethod
    def getBossGroupedBonuses(cls, bonuses):
        main, additional, bonusVehicle = [], [], None
        for bonus in bonuses:
            bonusName = bonus.getName()
            if bonusName == 'vehicles' and bonusVehicle is None:
                bonusVehicle = cls.__getVehicleBonus(bonus)
            if cls._isSpecialAward(bonus):
                main.append(bonus)
            additional.append(bonus)

        if not main and additional and len(additional) <= _MAX_MAIN_BONUSES:
            main.extend(additional)
            additional = []
        return _GroupedBonuses(main=main, additional=additional, vehicle=bonusVehicle)

    @classmethod
    def __getVehicleBonus(cls, bonus):
        return first([ vehicle for vehicle, _ in bonus.getVehicles() ])

    @classmethod
    def _isSpecialAward(cls, bonus):
        bonusName = bonus.getName()
        if bonusName == 'vehicles':
            return True
        if bonusName == 'customizations':
            for item in bonus.getCustomizations():
                customizationItem = bonus.getC11nItem(item)
                if isStyle3D(customizationItem):
                    return True

        return False


class WtTmanTemplateBonusPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        result = super(WtTmanTemplateBonusPacker, cls)._pack(bonus)
        bonusTokens = bonus.getTokens()
        for tokenID, token in bonusTokens.iteritems():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                model = cls._getBonusModel()
                cls._packToken(token, model)
                result.append(model)

        return result

    @classmethod
    def _packToken(cls, token, model):
        recruitInfo = getRecruitInfo(token.id)
        if recruitInfo is None:
            return
        else:
            model.setIcon(recruitInfo.getSourceID())
            model.setName(recruitInfo.getSourceID())
            model.setLabel(recruitInfo.getFullUserName())
            return

    @classmethod
    def _getBonusModel(cls):
        return IconBonusModel()

    @classmethod
    def _getToolTip(cls, bonus):
        tooltipData = []
        for tokenID in bonus.getTokens().iterkeys():
            if tokenID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
                tooltipData.append(TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[tokenID]))

        return tooltipData


class WTEventGroupsBonusUIPacker(GroupsBonusUIPacker):
    __gameEventCtrl = dependency.descriptor(IWhiteTigerController)

    @classmethod
    def _getBonusModel(cls):
        return BonusModel()

    @classmethod
    def _pack(cls, bonus):
        model = cls._getBonusModel()
        cls._packModel(model, bonus)
        return [model]

    @classmethod
    def _packModel(cls, model, bonus):
        model.setName('hunter_collection')
        model.setIsCompensation(bonus.isCompensation())

    @classmethod
    def _getToolTip(cls, _):
        collectionRes = R.strings.event.bonuses.random_collection_element_WT
        return [createTooltipData(makeTooltip(backport.text(collectionRes.tooltip.header()), backport.text(collectionRes.tooltip.body())))]


class WtVehiclesBonusPacker(VehiclesBonusUIPacker):
    c11n = dependency.descriptor(ICustomizationService)

    @classmethod
    def _getBonusModel(cls):
        return WtPortalBonusModel()

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = WtPortalBonusModel()
        model.setName(bonus.getName())
        model.setVehicleCD(vehicle.compactDescr)
        model.setStyleCD(0)
        model.setVehicleLvl(vehicle.level)
        model.setVehicleType(VehicleType(vehicle.type))
        model.setIsCompensation(bonus.isCompensation())
        model.setLabel(vehicle.shortUserName)
        model.setIsCollected((vehicle.isInInventory or vehicle.isRestorePossible()) and not vehicle.rentInfo.isRented)
        wtExtendData = getattr(bonus, 'wtExtendData', None)
        vehicles = wtExtendData.get('vehicles') if wtExtendData else None
        if vehicles:
            model.setIsSpecial(vehicles.get('isSpecial', False))
            iconName = vehicles.get('icon')
            vehicleIcon = R.images.white_tiger.gui.maps.icons.portals.customReward.s110x80.dyn(iconName)()
            model.setName(iconName)
            styleId = vehicles.get('styleId')
            if styleId > 0:
                itemTypeID = GUI_ITEM_TYPE_INDICES.get('style')
                c11nItem = WtVehiclesBonusPacker.c11n.getItemByID(itemTypeID, styleId)
                model.setStyleCD(c11nItem.intCD)
        else:
            vehicleIcon = R.images.gui.maps.icons.quests.bonuses.s180x135.vehicles()
        model.setIcon(backport.image(vehicleIcon))
        return model


class EmptyPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return []


def getWtUIBonusPacker():
    packers = {}
    packers.update({Currency.GOLD: WTGoldPacker(),
     Currency.CREDITS: WtSimpleBonusUIPacker(),
     Currency.CRYSTAL: WtSimpleBonusUIPacker(),
     'goodies': WtGoodiesBonusUIPacker(),
     'freeXP': WtSimpleBonusUIPacker(),
     'premium_plus': WtSimpleBonusUIPacker(),
     'slots': WtSimpleBonusUIPacker(),
     'items': WtItemBonusUIPacker(),
     'customizations': WtCustomizationBonusUIPacker(),
     'ticket': WtTicketTokenBonusPacker(),
     'vehicles': WtVehiclesBonusPacker(),
     'crewBooks': CrewBookBonusUIPacker(),
     'battleToken': EmptyPacker(),
     'lootBoxToken': EmptyPacker()})
    return BonusUIPacker(packers)
