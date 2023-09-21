# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_simple_bonus_packers.py
import logging
from collections import namedtuple
import constants
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.portal_reward import PortalReward, TooltipType
from gui.impl.backport import createTooltipData
from gui.impl.gen.view_models.views.lobby.wt_event.tank_reward import TankReward
from gui.impl.lobby.wt_event.wt_event_constants import BonusGroup
from gui.server_events.bonuses import mergeBonuses, getSplitBonusFunction, RandomCrewbook, RandomEventStyle3d, RandomEventStyle2d, RandomEventDecal, LootBoxTokensBonus, RandomEventInscription, RandomEventEmblem, RandomEventCamouflage, WtCustomizationsBonus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared.gui_items.customization.c11n_items import isStyle3D
from gui.shared.money import Currency
from gui.shared.missions.packers.bonus import BaseBonusUIPacker, SimpleBonusUIPacker, GoodiesBonusUIPacker, BonusUIPacker, ItemBonusUIPacker, VehiclesBonusUIPacker
from gui.shared.utils.functions import makeTooltip
from gui.wt_event.wt_event_bonuses_packers import WTCrewBookBonusUIPacker, WTCrewSkinBonusUIPacker
from gui.wt_event.wt_event_helpers import getSpecialVehicles
from helpers.dependency import replace_none_kwargs
from skeletons.gui.game_control import ILootBoxesController
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
 'crewBooks',
 _RANDOM_CREWBOOK,
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
 _CREWBOOK))

def getWtSplitBonusFunction(bonus):
    return None if bonus.getName() in NO_SPLITTED_BONUSES else getSplitBonusFunction(bonus)


def mergeWtBonuses(bonuses):
    for composer in _BONUS_COMPOSERS:
        bonuses = composer(bonuses)

    return mergeBonuses(bonuses)


def mergeWtProgressionBonuses(bonuses):
    bonuses = _composeProgressionCustomizations(bonuses)
    return mergeBonuses(bonuses)


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
        vehicles = getSpecialVehicles()
        vehicleBonuses.reverse()
        for bonus in vehicleBonuses:
            for vehicle, _ in bonus.getVehicles():
                if any((x.intCD == vehicle.intCD for x in vehicles)):
                    item = TankReward()
                    item.setTankName(vehicle.name.split(':')[1])
                    item.setIsCollected(vehicle.isInInventory or vehicle.isRestorePossible())
                    tooltipID = len(tooltipItems)
                    tooltipData = WtEventVehiclesBonusUIPacker().getToolTip(bonus)
                    if tooltipData:
                        tooltipItems[str(tooltipID)] = first(tooltipData)
                        item.setTooltipId(tooltipID)
                    model.addViewModel(item)

        model.invalidate()
        return


def sortBonuses(bonus, orderList):
    bonusName = bonus.getName()
    return orderList.index(bonusName) if bonusName in orderList else len(orderList)


@replace_none_kwargs(boxCtrl=ILootBoxesController)
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
            if itemType in ('decal', 'projectionDecal'):
                decals.append(bonus)
            if itemType == 'inscription':
                inscriptions.append(bonus)
            if itemType == 'emblem':
                emblems.append(bonus)
            if itemType == 'camouflage':
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
        return model


class SimpleEventGoldPacker(SimpleEventCountablePacker):

    @classmethod
    def _getToolTip(cls, bonus):
        return [createTooltipData(tooltip=makeTooltip(backport.text(R.strings.event.bonusTooltip.gold.header()), backport.text(R.strings.event.bonusTooltip.gold.body())))]


class SimpleEventPremiumPacker(SimpleBonusUIPacker):

    @classmethod
    def _packSingleBonus(cls, bonus, label=''):
        model = PortalReward()
        model.setIcon(_ICON_PATH.quests.bonuses.small.dyn('premium_plus')())
        model.setTooltipType(TooltipType.DEFAULT)
        return model


class SimpleEventGoodiesPacker(GoodiesBonusUIPacker):

    @classmethod
    def _packIconBonusModel(cls, bonus, icon, count, label):
        model = PortalReward()
        model.setIcon(_ICON_PATH.quests.bonuses.small.dyn(icon)())
        model.setTooltipType(TooltipType.DEFAULT)
        return model

    @classmethod
    def _getBoostersToolTip(cls, tooltipData, booster):
        boosterName = booster.boosterGuiType
        tooltipData.append(createTooltipData(tooltip=makeTooltip(backport.text(R.strings.event.bonusTooltip.dyn(boosterName).header()), backport.text(R.strings.event.bonusTooltip.dyn(boosterName).body()))))


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
        hasMultipleConditions = 'hasMultipleConditions' if 'rent' in vehInfo and 'hasMultipleConditions' in vehInfo['rent'] else ''
        return [vehicle.intCD, hasMultipleConditions]


def getWtEventSimpleBonusPacker():
    result = {Currency.CREDITS: SimpleEventCountablePacker(),
     Currency.GOLD: SimpleEventGoldPacker(),
     'goodies': SimpleEventGoodiesPacker(),
     'items': SimpleEventItemPacker(),
     'slots': SimpleEventCountablePacker(),
     constants.PREMIUM_ENTITLEMENTS.PLUS: SimpleEventPremiumPacker(),
     'crewBooks': SimpleEventCrewBookPacker(),
     _RANDOM_CREWBOOK: SimpleEventRandomCrewBookPacker(),
     _RANDOM_STYLE_2D: SimpleEventRandomElementPacker(),
     _RANDOM_DECAL: SimpleEventRandomElementPacker(),
     _INSCRIPTION: SimpleEventRandomElementPacker(),
     _EMBLEM: SimpleEventRandomElementPacker(),
     _CAMOUFLAGE: SimpleEventRandomElementPacker(),
     _CREWSKINS: SimpleEventCrewSkinPacker()}
    return BonusUIPacker(result)


_SEGREGATE_BONUSES = {_RANDOM_STYLE_3D: Event3dStylePacker(),
 _RANDOM_STYLE_2D: Event2dStylePacker()}
