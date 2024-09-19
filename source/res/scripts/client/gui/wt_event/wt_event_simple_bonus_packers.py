# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_simple_bonus_packers.py
import logging
from collections import namedtuple
import constants
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.awards.reward_model import RewardModel
from gui.impl.gen.view_models.views.lobby.wt_event.portal_reward import PortalReward, TooltipType
from gui.impl.backport import createTooltipData, TooltipData
from gui.impl.gen.view_models.views.lobby.wt_event.tank_reward import TankReward
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.infotype_reward_model import InfotypeRewardModel
from gui.impl.lobby.wt_event.wt_event_constants import BonusGroup
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN, TokenBonusFormatter, AWARDS_SIZES
from gui.server_events.bonuses import mergeBonuses, getSplitBonusFunction, RandomCrewbook, RandomEventStyle3d, RandomEventStyle2d, RandomEventDecal, LootBoxTokensBonus, RandomEventInscription, RandomEventEmblem, RandomEventCamouflage, WtCustomizationsBonus, BlueprintsBonusSubtypes, IntelligenceBlueprintBonus, VehicleBlueprintBonus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.server_events.formatters import parseComplexToken
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.gui_items.customization.c11n_items import isStyle3D
from gui.shared.money import Currency
from gui.shared.missions.packers.bonus import BaseBonusUIPacker, SimpleBonusUIPacker, GoodiesBonusUIPacker, BonusUIPacker, ItemBonusUIPacker, VehiclesBonusUIPacker, getDefaultBonusPackersMap, BACKPORT_TOOLTIP_CONTENT_ID, CustomizationBonusUIPacker, BlueprintBonusUIPacker, CrewBookBonusUIPacker, TokenBonusUIPacker, VEHICLE_RENT_ICON_POSTFIX
from gui.shared.utils.functions import makeTooltip
from gui.wt_event.wt_event_bonuses_packers import WTCrewBookBonusUIPacker, WTCrewSkinBonusUIPacker
from gui.wt_event.wt_event_helpers import getSpecialVehicles, getEventTankType
from helpers.dependency import replace_none_kwargs
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from skeletons.gui.game_control import IWTLootBoxesController
from shared_utils import findFirst, first
_logger = logging.getLogger(__name__)
_GroupedBonuses = namedtuple('_GroupedBonuses', ('main', 'additional', 'vehicle'))
_RANDOM_STYLE_3D = 'randomStyle3d'
_RANDOM_STYLE_2D = 'randomStyle2d'
_RANDOM_DECAL = 'randomDecal'
_RANDOM_CREWBOOK = 'randomCrewbook'
_INSCRIPTION = 'inscription'
_EMBLEM = 'emblem'
_CAMOUFLAGE = 'camouflage'
_CREWBOOK = 'crewBooks'
_CREWSKINS = 'crewSkins'
_PROJECTION_DECAL = 'projectionDecal'
_DECAL = 'decal'
HUNTER_BONUSES_ORDER = [Currency.CREDITS,
 'goodies',
 'items',
 constants.PREMIUM_ENTITLEMENTS.PLUS,
 'slots',
 'customizations',
 'tmanToken',
 'battleToken']
BOSS_BONUSES_ORDER = [Currency.GOLD,
 Currency.CREDITS,
 Currency.FREE_XP,
 _RANDOM_CREWBOOK,
 'crewBooks',
 'goodies',
 constants.PREMIUM_ENTITLEMENTS.PLUS,
 _RANDOM_STYLE_2D,
 _RANDOM_DECAL,
 'items']
_ICON_PATH = R.images.gui.maps.icons
_BONUS_TYPE_TO_GROUP = {_RANDOM_STYLE_3D: BonusGroup.STYLE_3D,
 'vehicles': BonusGroup.VEHICLES}
NO_SPLITTED_BONUSES = frozenset((_RANDOM_CREWBOOK,
 _RANDOM_DECAL,
 _RANDOM_STYLE_2D,
 _RANDOM_STYLE_3D,
 _EMBLEM,
 _CREWBOOK,
 Currency.CREDITS,
 _INSCRIPTION))

def getWtSplitBonusFunction(bonus):
    return None if bonus.getName() in NO_SPLITTED_BONUSES else getSplitBonusFunction(bonus)


def mergeWtBonuses(bonuses):
    for composer in _BONUS_COMPOSERS:
        bonuses = composer(bonuses)

    return mergeBonuses(bonuses)


def mergeWtProgressionBonuses(bonuses):
    bonuses = _composeProgressionCustomizations(bonuses)
    return bonuses


def getWtBonusGroup(bonuses):
    for bonus in bonuses:
        bonusName = bonus.getName()
        group = _BONUS_TYPE_TO_GROUP.get(bonusName)
        if group is not None:
            return group
        if bonusName == 'battleToken' and isinstance(bonus, LootBoxTokensBonus):
            return BonusGroup.LOOTBOX

    return BonusGroup.OTHER


def fillPortalRewardModel(model, bonuses):
    for bonus in bonuses:
        if not bonus.isShowInGUI():
            continue
        bonusProcessor = _SEGREGATE_BONUSES.get(bonus.getName())
        if bonusProcessor is not None:
            bonusProcessor.pack(model, bonus)

    return


def packRentVehicleBonus(model, bonuses, tooltipItems):
    vehicleGroup = bonuses.get(BonusGroup.RENT)
    for bonus in vehicleGroup:
        if not bonus or not isinstance(bonus, list):
            continue
        for bonusEntry in bonus:
            if bonusEntry.getName() == 'vehicles':
                model.setIcon(_ICON_PATH.wtevent.rewards.rental_tank_icon())
                tooltipID = len(tooltipItems)
                tooltipData = WtEventVehiclesBonusUIPacker().getToolTip(bonusEntry)
                if tooltipData:
                    tooltipItems[str(tooltipID)] = first(tooltipData)
                    model.setIndex(tooltipID)


def packSpecialVehicleBonus(model, bonuses, tooltipItems):
    vehicleGroup = bonuses.get(BonusGroup.LOW)
    if vehicleGroup is None:
        return
    else:
        model.clearItems()
        vehicleBonuses = [ bonus for bonus in vehicleGroup.bonuses if bonus.getName() == 'vehicles' ]
        specialVehicles = getSpecialVehicles()
        vehicleBonusDict = {}
        for bonus in vehicleBonuses:
            for vehicle, _ in bonus.getVehicles():
                vehicleBonusDict[vehicle.name] = bonus

        for specialVeh in specialVehicles:
            item = TankReward()
            tankName = specialVeh.name.split(':')[1]
            item.setIsCollected(specialVeh.isInInventory or specialVeh.isRestorePossible())
            item.setTankType(getEventTankType(tankName.replace('-', '_')))
            tooltipID = len(tooltipItems)
            tooltipData = WtEventVehiclesBonusUIPacker().getToolTip(vehicleBonusDict[specialVeh.name])
            if tooltipData:
                tooltipItems[str(tooltipID)] = first(tooltipData)
                item.setTooltipId(tooltipID)
            model.addViewModel(item)

        model.invalidate()
        return


def sortBonuses(bonus, orderList):
    bonusName = bonus.getName()
    return orderList.index(bonusName) if bonusName in orderList else len(orderList)


@replace_none_kwargs(boxCtrl=IWTLootBoxesController)
def _getBonusStatus(bonusType, bonusGroup, boxCtrl=None):
    rewards = boxCtrl.getLootBoxesRewards(EventLootBoxes.WT_BOSS)
    if not rewards:
        _logger.error('There is not boss rewards')
        return None
    rewards = rewards.get(bonusGroup)
    bonus = findFirst(lambda b: b.getName() == bonusType, rewards.bonuses)
    if not bonus:
        _logger.error('Bonus is absent in the boss lootBox')
        return None
    else:
        return _Status.COLLECTED if all([ bonus.getC11nItem(item).fullCount() > 0 for item in bonus.getValue() ]) else _Status.NOT_COLLECTED


def _getStyles3dStatus():
    return _getBonusStatus(TooltipType.STYLE_3D.value, BonusGroup.AVERAGE)


def _getIsStyleCollected(key):
    status = STATUS_GETTERS.get(key)
    return status() == _Status.COLLECTED if status and callable(status) else False


class _Status(object):
    COLLECTED = 'collected'
    NOT_COLLECTED = 'notCollected'


STATUS_GETTERS = {TooltipType.STYLE_3D.value: _getStyles3dStatus}

def _createBonus(bonusClazz, bonusName, bonuses):
    valueItems = []
    for bonus in bonuses:
        value = bonus.getValue()
        if isinstance(value, list):
            valueItems.extend(value)
        valueItems.append(value)

    return bonusClazz(bonusName, valueItems)


def _composeCrewBooks(bonuses):
    other, commonCrewBooks = [], []
    for bonus in bonuses:
        if bonus.getName() != 'crewBooks':
            other.append(bonus)
            continue
        for book, count in bonus.getItems():
            if book is None or not count:
                continue
            if book.isCommon():
                commonCrewBooks.append(bonus)
            other.append(bonus)

    if len(commonCrewBooks) > 1:
        other.append(_createBonus(RandomCrewbook, _RANDOM_CREWBOOK, commonCrewBooks))
    return other


def _composeCustomization(bonuses):
    styles2d, styles3d, decals, inscriptions, camouflages, emblems, other = ([],
     [],
     [],
     [],
     [],
     [],
     [])
    for bonus in bonuses:
        if bonus.getName() != 'customizations':
            other.append(bonus)
            continue
        for item in bonus.getCustomizations():
            if item is None:
                continue
            customizationItem = bonus.getC11nItem(item)
            itemType = customizationItem.itemTypeName
            if itemType == 'style':
                if isStyle3D(customizationItem):
                    styles3d.append(bonus)
                else:
                    styles2d.append(bonus)
            if itemType in (_DECAL, _PROJECTION_DECAL):
                decals.append(bonus)
            if itemType == _INSCRIPTION:
                inscriptions.append(bonus)
            if itemType == _EMBLEM:
                emblems.append(bonus)
            if itemType == _CAMOUFLAGE:
                camouflages.append(bonus)
            other.append(bonus)

    if styles2d:
        other.append(_createBonus(RandomEventStyle2d, _RANDOM_STYLE_2D, styles2d))
    if styles3d:
        other.append(_createBonus(RandomEventStyle3d, _RANDOM_STYLE_3D, styles3d))
    if decals:
        other.append(_createBonus(RandomEventDecal, _RANDOM_DECAL, decals))
    if inscriptions:
        other.append(_createBonus(RandomEventInscription, _INSCRIPTION, inscriptions))
    if emblems:
        other.append(_createBonus(RandomEventEmblem, _EMBLEM, emblems))
    if camouflages:
        other.append(_createBonus(RandomEventCamouflage, _CAMOUFLAGE, camouflages))
    return other


def _composeProgressionCustomizations(bonuses):
    progBonus = []
    for bonus in bonuses:
        if bonus.getName() != 'customizations':
            progBonus.append(bonus)
            continue
        progBonus.append(WtCustomizationsBonus(bonus.getName(), bonus.getValue()))

    return progBonus


_BONUS_COMPOSERS = (_composeCrewBooks, _composeCustomization)

class StylePacker(object):
    _TOOLTIP_TYPE = None

    @classmethod
    def pack(cls, model, bonus):
        item = PortalReward()
        item.setIcon(bonus.getIcon())
        item.setTooltipType(cls._TOOLTIP_TYPE)
        item.setIsCollected(_getIsStyleCollected(cls._TOOLTIP_TYPE.value))
        model.addViewModel(item)


class Event3dStylePacker(StylePacker):
    _TOOLTIP_TYPE = TooltipType.STYLE_3D


class Event2dStylePacker(StylePacker):
    _TOOLTIP_TYPE = TooltipType.STYLE_2D


class SimpleEventCountablePacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label=''):
        model = PortalReward()
        model.setIcon(_ICON_PATH.quests.bonuses.small.dyn(bonus.getName())())
        model.setTooltipType(TooltipType.DEFAULT)
        model.setAmount(bonus.getValue())
        return model


class SimpleEventGoldPacker(SimpleEventCountablePacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(tooltip=makeTooltip(backport.text(R.strings.event.bonusTooltip.gold.header()), backport.text(R.strings.event.bonusTooltip.gold.body())))]


class SimpleEventPremiumPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label=''):
        model = PortalReward()
        model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        model.setTooltipType(TooltipType.DEFAULT)
        return model


class SimpleEventGoodiesPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = PortalReward()
        model.setIcon(_ICON_PATH.quests.bonuses.small.dyn(icon)())
        model.setTooltipType(TooltipType.DEFAULT)
        return model


class SimpleEventItemPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = PortalReward()
        model.setIcon(_ICON_PATH.quests.bonuses.small.dyn(item.getGUIEmblemID())())
        model.setTooltipType(TooltipType.DEFAULT)
        return model


class SimpleEventCrewBookPacker(WTCrewBookBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = PortalReward()
        model.setIcon(_ICON_PATH.crewBooks.books.small.dyn(book.getBonusIconName())())
        model.setTooltipType(TooltipType.DEFAULT)
        return model


class SimpleEventFreeXPPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = PortalReward()
        model.setIcon(_ICON_PATH.wtevent.rewards.small.freeXP())
        model.setTooltipType(TooltipType.DEFAULT)
        model.setAmount(bonus.getValue())
        return model


class SimpleEventCrewSkinPacker(WTCrewSkinBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count, _=''):
        model = PortalReward()
        model.setIcon(_ICON_PATH.wtevent.rewards.small.crewSkin())
        model.setTooltipType(TooltipType.DEFAULT)
        return model


class SimpleEventRandomElementPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = PortalReward()
        model.setIcon(bonus.getIcon())
        model.setTooltipType(TooltipType.DEFAULT)
        return [model]


class SimpleEventRandomCrewBookPacker(BaseBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = PortalReward()
        model.setIcon(bonus.getIcon())
        model.setTooltipType(bonus.getTooltip())
        return [model]

    @classmethod
    def _getToolTip(cls, bonus):
        xp = bonus.getXP()
        bookType = bonus.getBookType()
        return [createTooltipData(tooltip=makeTooltip(backport.text(R.strings.tooltips.crewBooks.storage.filters.dyn(bookType).title()), backport.text(R.strings.tooltips.selectableCrewbook.info(), exp=xp)))]


class WtEventVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _getTooltipAlias(cls):
        return TOOLTIPS_CONSTANTS.WT_PORTAL_VEHICLE

    @classmethod
    def _getTooltipArgs(cls, bonus, vehicle, vehInfo):
        anyExpires = 'anyExpires' if 'rent' in vehInfo and 'anyExpires' in vehInfo['rent'] else ''
        return [vehicle.intCD, anyExpires]


def getWtEventSimpleBonusPacker():
    result = {Currency.CREDITS: SimpleEventCountablePacker(),
     Currency.GOLD: SimpleEventGoldPacker(),
     'goodies': SimpleEventGoodiesPacker(),
     'items': SimpleEventItemPacker(),
     'slots': SimpleEventCountablePacker(),
     constants.PREMIUM_ENTITLEMENTS.PLUS: SimpleEventPremiumPacker(),
     'crewBooks': SimpleEventCrewBookPacker(),
     'freeXP': SimpleEventFreeXPPacker(),
     _RANDOM_CREWBOOK: SimpleEventRandomCrewBookPacker(),
     _RANDOM_STYLE_2D: SimpleEventRandomElementPacker(),
     _RANDOM_STYLE_3D: SimpleEventRandomElementPacker(),
     _RANDOM_DECAL: SimpleEventRandomElementPacker(),
     _INSCRIPTION: SimpleEventRandomElementPacker(),
     _EMBLEM: SimpleEventRandomElementPacker(),
     _CAMOUFLAGE: SimpleEventRandomElementPacker(),
     _CREWSKINS: SimpleEventCrewSkinPacker()}
    return BonusUIPacker(result)


_SEGREGATE_BONUSES = {_RANDOM_STYLE_3D: Event3dStylePacker(),
 _RANDOM_STYLE_2D: Event2dStylePacker()}

def getEventLootBoxesInfoTypeBonusPacker():
    defaultMapper = getDefaultBonusPackersMap()
    infoTypeRewardPacker = InfoTypeRewardPacker()
    blueprintPacker = InfoTypeBlueprintRewardPacker()
    mapping = {k:infoTypeRewardPacker for k in defaultMapper}
    mapping.update({'battleToken': InfoTypeTokenPacker(),
     'blueprints': blueprintPacker,
     'blueprintsAny': blueprintPacker,
     'finalBlueprints': blueprintPacker,
     'crewBooks': InfoTypeCrewBooksPacker(),
     'crewSkins': InfoTypeCrewSkinsPacker(),
     'customizations': InfoTypeCustomizationPacker(),
     'goodies': InfoTypeGoodiesPacker(),
     'items': InfoTypeItemPacker(),
     'tmanToken': InfoTypeTmanTemplateBonusPacker(),
     'tokens': InfoTypeTokenPacker(),
     'vehicles': InfoTypeVehiclePacker()})
    return BonusUIPacker(mapping)


_R_BONUS_ICONS = R.images.gui.maps.icons.quests.bonuses
_R_CREW_BOOKS_ICONS = R.images.gui.maps.icons.crewBooks

class TmanTemplateBonusPacker(SimpleBonusUIPacker):

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
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return
        else:
            model = RewardModel()
            cls._packCommon(bonus, model)
            model.setIconSource(_R_BONUS_ICONS.s600x450.dyn('tankwoman' if recruit.isFemale() else 'tankman')())
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


class EventLootBoxSimpleBonusUIPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(bonus.getValue())
        model.setIconSource(_R_BONUS_ICONS.s600x450.dyn(bonus.getName())())
        return model


class EventLootBoxCustomizationBonusUIPacker(CustomizationBonusUIPacker):
    _3D_STYLE_ICON_NAME = 'style_3d'

    @classmethod
    def _packSingleBonus(cls, bonus, item, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(item.get('value', 0))
        c11nItem = bonus.getC11nItem(item)
        iconName = c11nItem.itemTypeName
        if iconName == 'style' and c11nItem.modelsSet:
            iconName = cls._3D_STYLE_ICON_NAME
        model.setIconSource(_R_BONUS_ICONS.s600x450.dyn(iconName)())
        return model


class EventLootBoxGoodiesBonusUIPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        model.setIconSource(_R_BONUS_ICONS.s600x450.dyn(icon)())
        return model


class EventLootBoxBlueprintBonusUIPacker(BlueprintBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(bonus.getCount())
        model.setIconSource(R.images.gui.maps.icons.blueprints.fragment.s600x450.dyn(bonus.getImageCategory())())
        return [model]


class EventLootBoxItemBonusUIPacker(ItemBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, item, count):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        model.setIconSource(_R_BONUS_ICONS.s600x450.dyn(item.getGUIEmblemID())())
        model.setOverlayType(item.getOverlayType())
        return model


class EventLootBoxCrewBookBonusUIPacker(CrewBookBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, book, count):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(count)
        iconSource = R.images.gui.maps.icons.crewBooks.books.s600x450.dyn(getIconResourceName(book.icon))()
        model.setIconSource(iconSource)
        return model


class EventLootBoxTokenBonusUIPacker(TokenBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        for tokenID, token in bonusTokens.iteritems():
            complexToken = parseComplexToken(tokenID)
            if tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
                packedBonus = cls._packToken(bonus, complexToken, token)
                if packedBonus is not None:
                    result.append(packedBonus)

        return result

    @classmethod
    def _getToolTip(cls, bonus):
        bonusTokens = bonus.getTokens()
        result = []
        for tokenID, _ in bonusTokens.iteritems():
            if tokenID.startswith(BATTLE_BONUS_X5_TOKEN):
                tooltip = TokenBonusFormatter.getBonusFactorTooltip(BATTLE_BONUS_X5_TOKEN)
                result.append(createTooltipData(tooltip))

        return result

    @classmethod
    def _packToken(cls, bonus, *args):
        model = RewardModel()
        cls._packCommon(bonus, model)
        model.setCount(bonus.getCount())
        model.setIconSource(_R_BONUS_ICONS.s600x450.bonus_battle_task())
        return model


class EventLootBoxPremiumBonusUIPacker(EventLootBoxSimpleBonusUIPacker):
    _SPEC_ICON_FOR_COUNT = 3

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = RewardModel()
        cls._packCommon(bonus, model)
        if bonus.getValue() <= cls._SPEC_ICON_FOR_COUNT:
            model.setCount(1)
            model.setIconSource(_R_BONUS_ICONS.s600x450.dyn('_'.join((bonus.getName(), str(bonus.getValue()))))())
        else:
            model.setCount(int(bonus.getValue()))
            model.setIconSource(_R_BONUS_ICONS.s600x450.dyn('{}_1'.format(bonus.getName()))())
        return model


class EventLootBoxVehiclesBonusUIPacker(VehiclesBonusUIPacker):

    @classmethod
    def _packVehicleBonusModel(cls, bonus, vehInfo, isRent, vehicle):
        model = RewardModel()
        model.setName(bonus.getName() + VEHICLE_RENT_ICON_POSTFIX if isRent else bonus.getName())
        model.setIsCompensation(bonus.isCompensation())
        if bonus.isCompensation():
            model.setIconSource(R.images.event_lootboxes.gui.maps.rewards.s600x450.gold())
        return model

    @classmethod
    def _packVehicles(cls, bonus, vehicles):
        packedVehicles = []
        for vehicle, vehInfo in vehicles:
            compensation = bonus.compensation(vehicle, bonus)
            if compensation:
                packer = EventLootBoxSimpleBonusUIPacker()
                for bonusComp in compensation:
                    packedVehicles.extend(packer.pack(bonusComp))

            packedVehicles.append(cls._packVehicle(bonus, vehInfo, vehicle))

        return packedVehicles


class VehicleBlueprintsPacker(object):

    @staticmethod
    def pack(bonuses):
        model = RewardModel()
        if any([ bonus.getBlueprintName() == BlueprintsBonusSubtypes.VEHICLE_FRAGMENT for bonus in bonuses ]):
            iconSource = R.images.gui.maps.icons.blueprints.fragment.s600x450.vehicle
        else:
            iconSource = R.images.gui.maps.icons.blueprints.fragment.s600x450.vehicle_complete
        model.setIconSource(iconSource())
        count = sum((bonus.getCount() for bonus in bonuses))
        model.setCount(count)
        model.setIsCompensation(False)
        return model

    @staticmethod
    def getTooltip(bonuses):
        fragmentCDs = [ bonus.getBlueprintSpecialArgs() for bonus in bonuses ]
        return TooltipData(tooltip=None, isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_LOOT_BOXES_VEHICLE_BLUEPRINT_FRAGMENT, specialArgs=[fragmentCDs])


class InfoTypeRewardPacker(SimpleBonusUIPacker):

    @classmethod
    def _pack(cls, bonus):
        return [cls._packSingleBonus(bonus, '')]

    @classmethod
    def _packCommon(cls, bonus, model):
        model.setName(bonus.getName())

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = InfotypeRewardModel()
        cls._packCommon(bonus, model)
        model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return []


class InfoTypeBlueprintRewardPacker(InfoTypeRewardPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = InfotypeRewardModel()
        model.setName(bonus.getBlueprintName())
        if bonus.getBlueprintName() == BlueprintsBonusSubtypes.NATION_FRAGMENT:
            model.setIcon(R.images.gui.maps.icons.blueprints.fragment.small.randomNational())
        else:
            model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        model.setCount(bonus.getCount())
        return model


class InfoTypeVehiclePacker(InfoTypeRewardPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = InfotypeRewardModel()
        model.setName(bonus.formatValue())
        model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        return model


class InfoTypeItemPacker(InfoTypeRewardPacker):

    @classmethod
    def _packSingleItem(cls, item, count):
        model = InfotypeRewardModel()
        model.setName(item.userName)
        model.setCount(count)
        model.setIcon(_R_BONUS_ICONS.dyn(AWARDS_SIZES.SMALL).dyn(item.getGUIEmblemID())())
        return model

    @classmethod
    def _pack(cls, bonus):
        return [ cls._packSingleItem(item, count) for item, count in bonus.getItems().iteritems() ]


class InfoTypeTmanTemplateBonusPacker(InfoTypeRewardPacker):

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
        recruit = getRecruitInfo(tokenID)
        if recruit is None:
            return
        else:
            model = InfotypeRewardModel()
            cls._packCommon(bonus, model)
            model.setIcon(_R_BONUS_ICONS.dyn(AWARDS_SIZES.SMALL).dyn('tankwoman' if recruit.isFemale() else 'tankman')())
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


class InfoTypeCustomizationPacker(InfoTypeRewardPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label):
        model = InfotypeRewardModel()
        model.setName(bonus.getName())
        model.setCount(sum((item.get('value', 1) for item in bonus.getCustomizations())))
        customizationItem = bonus.getC11nItem(bonus.getCustomizations()[0])
        if isStyle3D(customizationItem):
            model.setIcon(_R_BONUS_ICONS.small.style_3d())
        elif customizationItem.itemTypeName in (_DECAL, _PROJECTION_DECAL):
            model.setIcon(_R_BONUS_ICONS.small.decal())
        elif customizationItem.itemTypeName == _INSCRIPTION:
            model.setIcon(_R_BONUS_ICONS.small.inscription())
        elif customizationItem.itemTypeName == _EMBLEM:
            model.setIcon(_R_BONUS_ICONS.small.emblem())
        elif customizationItem.itemTypeName == _CAMOUFLAGE:
            model.setIcon(_R_BONUS_ICONS.small.camouflage())
        else:
            model.setIcon(_R_BONUS_ICONS.small.style())
        return model


class InfoTypeGoodiesPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = InfotypeRewardModel()
        model.setName(bonus.getName())
        model.setCount(count)
        model.setIcon(_R_BONUS_ICONS.small.dyn(icon)())
        return model

    @classmethod
    def _getToolTip(cls, bonus):
        return []


class InfoTypeCrewBooksPacker(InfoTypeItemPacker):

    @classmethod
    def _packSingleItem(cls, item, count):
        model = InfotypeRewardModel()
        model.setName(item.getBookType())
        model.setCount(count)
        if item.isCommon():
            model.setIcon(R.images.gui.maps.icons.crewBooks.books.big.universalBook())
        else:
            model.setIcon(R.images.gui.maps.icons.crewBooks.books.small.dyn(getIconResourceName(item.icon))())
        return model

    @classmethod
    def _pack(cls, bonus):
        packedBonus = []
        bonusItems = bonus.getItems()
        for item in bonusItems:
            count = item[1]
            packedBonus.append(cls._packSingleItem(item[0], count))

        return packedBonus


class InfoTypeCrewSkinsPacker(InfoTypeCrewBooksPacker):

    @classmethod
    def _packSingleItem(cls, item, count):
        model = InfotypeRewardModel()
        model.setCount(count)
        model.setIcon(_R_BONUS_ICONS.small.dyn('{}{}'.format(item.itemTypeName, item.getRarity()))())
        return model


class InfoTypeTokenPacker(EventLootBoxTokenBonusUIPacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return []

    @classmethod
    def _packToken(cls, bonus, *args):
        model = InfotypeRewardModel()
        model.setName(bonus.getName())
        model.setCount(bonus.getCount())
        model.setIcon(bonus.getIconResource(AWARDS_SIZES.SMALL))
        return model


def packBonusModelAndTooltipData(bonuses, rewardModels, tooltipData, vehicleModel):
    bonusIndexTotal = 0
    if tooltipData is not None:
        bonusIndexTotal = len(tooltipData)
    vehicleBlueprints = [ bonus for bonus in bonuses if _isVehicleBlueprintBonus(bonus) ]
    if len(vehicleBlueprints) > 1:
        bonuses = [ bonus for bonus in bonuses if bonus not in vehicleBlueprints ]
        model = VehicleBlueprintsPacker.pack(vehicleBlueprints)
        rewardModels.addViewModel(model)
        tooltipIdx = str(bonusIndexTotal)
        model.setTooltipId(tooltipIdx)
        tooltipData[tooltipIdx] = VehicleBlueprintsPacker.getTooltip(vehicleBlueprints)
        bonusIndexTotal += 1
    universalBlueprints = [ bonus for bonus in bonuses if isinstance(bonus, IntelligenceBlueprintBonus) ]
    if len(universalBlueprints) > 1:
        bonuses = [ bonus for bonus in bonuses if bonus not in universalBlueprints ]
        bonuses.append(IntelligenceBlueprintBonus('blueprints', (universalBlueprints[0].getValue()[0], sum((b.getCount() for b in universalBlueprints)))))
    packer = getWtEventSimpleBonusPacker()
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = packer.pack(bonus)
            bonusTooltipList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = packer.getToolTip(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                if bonus.getName() == 'vehicles' and item.getIsCompensation() or bonus.getName() != 'vehicles':
                    rewardModels.addViewModel(item)
                if tooltipData is not None and bonusTooltipList:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    bonusIndexTotal += 1
                    if bonus.getName() == 'vehicles' and not item.getIsCompensation():
                        vehicleModel.setTooltipId(tooltipIdx)

    return


def _isVehicleBlueprintBonus(bonus):
    return isinstance(bonus, VehicleBlueprintBonus) and bonus.getBlueprintName() in (BlueprintsBonusSubtypes.FINAL_FRAGMENT, BlueprintsBonusSubtypes.VEHICLE_FRAGMENT)
