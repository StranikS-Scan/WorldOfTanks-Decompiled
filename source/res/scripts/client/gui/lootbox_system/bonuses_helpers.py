# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lootbox_system/bonuses_helpers.py
from collections import namedtuple
from copy import deepcopy
from itertools import izip_longest
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.reward_row_model import RewardRowModel
from gui.lootbox_system.bonuses_packers import packBonusModelAndTooltipData
from gui.lootbox_system.awards_manager import AwardsManager
from gui.server_events.bonuses import _BONUSES, getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.shared.money import Money
from items import EQUIPMENT_TYPES, ITEM_TYPE_INDICES, parseIntCompactDescr
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from items.vehicles import getItemByCompactDescr
RewardsGroup = namedtuple('RewardsGroup', ('name', 'bonusTypes', 'bonuses', 'filterFuncs'))
REWARDS_GROUP_NAME_RES = R.strings.lootbox_system.autoOpenView.rewardGroups

def isOptionalDevice(itemTypeID, _):
    return itemTypeID == ITEM_TYPE_INDICES['optionalDevice']


def isBattleBooster(itemTypeID, itemCD):
    if itemTypeID != ITEM_TYPE_INDICES['equipment']:
        return False
    itemDescr = getItemByCompactDescr(itemCD)
    return itemDescr.equipmentType == EQUIPMENT_TYPES.battleBoosters


def isCrewBook(itemTypeID, _):
    return itemTypeID == ITEM_TYPE_INDICES['crewBook']


def noCompensation(info, _):
    return not (info.get('compensatedNumber', 0) > 0 or info.get('customCompensation', (0, 0)) != (0, 0))


def getVehiclesFilter(conditions):

    def vehiclesFilter(vehicles):
        filtered = []
        other = []
        for vehicle in vehicles:
            for vehCD, info in vehicle.items():
                if any((condition(info, vehCD) for condition in conditions)):
                    filtered.append(vehicle)
                else:
                    other.append(vehicle)
                break

        vehicles[:] = other
        return filtered

    return vehiclesFilter


def getItemsFilter(conditions):

    def itemsFilter(items):
        filtered = {}
        for itemCD, count in items.items():
            itemTypeID, _, _ = parseIntCompactDescr(itemCD)
            if any((condition(itemTypeID, itemCD) for condition in conditions)):
                filtered[itemCD] = count
                del items[itemCD]

        return filtered

    return itemsFilter


def getGoodiesFilter(conditions):

    def goodiesFilter(goodies):
        filtered = {}
        for goodieID, info in goodies.items():
            if any((condition(int(goodieID)) for condition in conditions)):
                filtered[goodieID] = info
                del goodies[goodieID]

        return filtered

    return goodiesFilter


def getTankmenFilter(tokens):
    filtered = {}
    for tID, tValue in tokens.items():
        if tID.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
            filtered[tID] = tValue
            del tokens[tID]

    return filtered


def packBonusGroups(bonuses, groupModels, groupsLayout, tooltipsData=None, packer=None):
    _groupBonuses(bonuses, groupsLayout)
    groupModels.clear()
    for group in groupsLayout:
        compensationBonuses = _mergeCompensations(group)
        groupBonuses = splitBonuses(_getLootBoxBonuses(group.bonuses))
        if group.name == REWARDS_GROUP_NAME_RES.other():
            groupBonuses += compensationBonuses
        AwardsManager.sortBonuses(groupBonuses, reverse=True)
        if not groupBonuses:
            continue
        groupModel = RewardRowModel()
        bonusModelsList = groupModel.rewards
        groupModel.setLabel(backport.text(group.name))
        bonusesCount = packBonusModelAndTooltipData(groupBonuses, bonusModelsList, tooltipData=tooltipsData, merge=False, packer=packer)
        if not bonusesCount:
            continue
        groupModel.setRewardsCount(bonusesCount)
        bonusModelsList.invalidate()
        groupModels.addViewModel(groupModel)

    groupModels.invalidate()


def _groupBonuses(bonuses, groupsLayout):
    bonuses = deepcopy(bonuses)
    for group in groupsLayout:
        if not group.bonusTypes:
            group.bonuses.update(bonuses)
            bonuses.clear()
        filterFuncs = group.filterFuncs or ()
        for bonusType, filterFunc in izip_longest(group.bonusTypes, filterFuncs):
            if bonusType not in bonuses:
                continue
            if filterFunc is None:
                group.bonuses[bonusType] = bonuses.pop(bonusType)
            bonus = bonuses[bonusType]
            filtered = filterFunc(bonus)
            if filtered:
                group.bonuses[bonusType] = filtered
            if not bonus:
                del bonuses[bonusType]

        if not bonuses:
            break

    return


def _mergeCompensations(bonusesGroup):
    compBonuses = []
    if bonusesGroup.name == REWARDS_GROUP_NAME_RES.other():
        vehicles = bonusesGroup.bonuses.get('vehicles', [])
        for compVehicle in vehicles:
            for _, vehInfo in compVehicle.items():
                compensatedNumber = vehInfo.get('compensatedNumber', 0)
                compensation = vehInfo.get('customCompensation')
                if compensatedNumber and compensation is not None:
                    money = Money(*compensation)
                    for currency, value in money.iteritems():
                        if value:
                            bonusClass = _BONUSES.get(currency)
                            compBonuses.append(bonusClass(currency, value, isCompensation=True))

    if compBonuses:
        del bonusesGroup.bonuses['vehicles']
    return mergeBonuses(compBonuses)


def _getLootBoxBonuses(rewards):
    bonuses = []
    for rewardType, rewardValue in rewards.iteritems():
        bonuses += getNonQuestBonuses(rewardType, rewardValue)

    return bonuses
