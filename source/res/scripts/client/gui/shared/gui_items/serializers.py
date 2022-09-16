# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/serializers.py
import copy
import cPickle
import math
import collections
from typing import List, Dict
from constants import SwitchState
from gui.shared.money import Money, Currency
from helpers import dependency, i18n
from items.components import skills_constants
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from gui.goodies import IGoodiesCache
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.fitting_item import ICONS_MASK
from gui.shared.gui_items import Tankman, Vehicle
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

def packTankmanSkill(skill, isPermanent=False):
    if skill.roleType in skills_constants.ACTIVE_SKILLS or skill.roleType in skills_constants.ROLES:
        roleIconPath = Tankman.getRoleSmallIconPath(skill.roleType)
    else:
        roleIconPath = ''
    return {'name': skill.name,
     'level': skill.level,
     'userName': skill.userName,
     'description': skill.description,
     'shortDescription': skill.shortDescription,
     'icon': {'big': skill.bigIconPath,
              'small': skill.smallIconPath,
              'role': roleIconPath},
     'isActive': skill.isActive,
     'isEnable': skill.isEnable,
     'roleType': skill.roleType,
     'isPerk': skill.isPerk,
     'isPermanent': isPermanent}


def packTankman(tankman, isCountPermanentSkills=True, splitFreeAndEarnedSkills=False):

    def vehicleIcon(vDescr, subtype=''):
        return ICONS_MASK % {'type': 'vehicle',
         'subtype': subtype,
         'unicName': vDescr.name.replace(':', '-')}

    nativeVehicleData = {'typeCompDescr': tankman.vehicleNativeDescr.type.compactDescr,
     'userName': Vehicle.getShortUserName(tankman.vehicleNativeDescr.type),
     'icon': vehicleIcon(tankman.vehicleNativeDescr),
     'iconContour': vehicleIcon(tankman.vehicleNativeDescr, 'contour/')}
    currentVehicleData = None
    if tankman.isInTank:
        currentVehicleData = {'inventoryID': tankman.vehicleInvID,
         'typeCompDescr': tankman.vehicleDescr.type.compactDescr,
         'userName': Vehicle.getShortUserName(tankman.vehicleDescr.type),
         'icon': vehicleIcon(tankman.vehicleDescr),
         'iconContour': vehicleIcon(tankman.vehicleDescr, 'contour/')}
    freeSkills = []
    skills = []
    if splitFreeAndEarnedSkills:
        for tankmanSkill in tankman.freeSkills:
            freeSkills.append(packTankmanSkill(tankmanSkill, isPermanent=True))

        for tankmanSkill in tankman.earnedSkills:
            skills.append(packTankmanSkill(tankmanSkill, isPermanent=False))

    else:
        tManChosenFreeSkillsNum = tankman.chosenFreeSkillsCount
        startSkillNumber = 0 if isCountPermanentSkills else tManChosenFreeSkillsNum
        tManSkills = tankman.skills
        for i in xrange(startSkillNumber, len(tManSkills)):
            skills.append(packTankmanSkill(tManSkills[i], isPermanent=i < tManChosenFreeSkillsNum))

    return {'strCD': cPickle.dumps(tankman.strCD),
     'inventoryID': tankman.invID,
     'nationID': tankman.nationID,
     'firstUserName': tankman.firstUserName,
     'lastUserName': tankman.lastUserName,
     'roleName': tankman.descriptor.role,
     'rankUserName': tankman.rankUserName,
     'roleUserName': tankman.roleUserName,
     'freeSkills': freeSkills,
     'newFreeSkillsCount': tankman.newFreeSkillsCount,
     'skills': skills,
     'efficiencyRoleLevel': tankman.efficiencyRoleLevel,
     'realRoleLevel': tankman.realRoleLevel,
     'roleLevel': tankman.roleLevel,
     'icon': {'big': Tankman.getBigIconPath(tankman.nationID, tankman.descriptor.iconID),
              'small': Tankman.getSmallIconPath(tankman.nationID, tankman.descriptor.iconID),
              'barracks': Tankman.getBarracksIconPath(tankman.nationID, tankman.descriptor.iconID)},
     'iconRole': {'big': Tankman.getRoleBigIconPath(tankman.descriptor.role),
                  'medium': Tankman.getRoleMediumIconPath(tankman.descriptor.role),
                  'small': Tankman.getRoleSmallIconPath(tankman.descriptor.role)},
     'iconRank': {'big': Tankman.getRankBigIconPath(tankman.nationID, tankman.descriptor.rankID),
                  'small': Tankman.getRankSmallIconPath(tankman.nationID, tankman.descriptor.rankID)},
     'isInTank': tankman.isInTank,
     'newSkillsCount': tankman.newSkillCount,
     'nativeVehicle': nativeVehicleData,
     'currentVehicle': currentVehicleData}


def packFittingItem(item):
    return {'buyPrice': item.buyPrices.itemPrice.price,
     'defBuyPrice': item.buyPrices.itemPrice.defPrice,
     'actionPrc': item.buyPrices.itemPrice.getActionPrc(),
     'sellPrice': item.sellPrices.itemPrice.price,
     'defSellPrice': item.sellPrices.itemPrice.defPrice,
     'sellActionPrc': item.sellPrices.itemPrice.getActionPrc(),
     'inventoryCount': item.inventoryCount,
     'isHidden': item.isHidden,
     'isRemovable': item.isRemovable,
     'intCD': item.intCD,
     'itemTypeName': item.itemTypeName,
     'itemTypeID': item.itemTypeID,
     'userName': item.userName,
     'description': item.fullDescription,
     'level': item.level,
     'nationID': item.nationID,
     'innationID': item.innationID}


def packShell(shell):
    result = packFittingItem(shell)
    result.update({'count': shell.count,
     'kind': shell.type})
    return result


def packVehicle(vehicle):
    result = packFittingItem(vehicle)
    result.update({'buyPrice': vehicle.buyPrices.itemPrice.price,
     'defBuyPrice': vehicle.buyPrices.itemPrice.defPrice,
     'actionPrc': vehicle.buyPrices.itemPrice.getActionPrc(),
     'sellPrice': vehicle.sellPrices.itemPrice.price,
     'defSellPrice': vehicle.sellPrices.itemPrice.defPrice,
     'sellActionPrc': vehicle.sellPrices.itemPrice.getActionPrc(),
     'inventoryCount': vehicle.inventoryCount,
     'isHidden': vehicle.isHidden,
     'isRemovable': vehicle.isRemovable,
     'intCD': vehicle.intCD,
     'itemTypeName': vehicle.itemTypeName,
     'itemTypeID': vehicle.itemTypeID,
     'userName': vehicle.userName,
     'description': vehicle.fullDescription,
     'level': vehicle.level,
     'nationID': vehicle.nationID,
     'innationID': vehicle.innationID,
     'inventoryID': vehicle.invID,
     'xp': vehicle.xp,
     'dailyXPFactor': vehicle.dailyXPFactor,
     'clanLock': vehicle.clanLock,
     'isUnique': vehicle.isUnique,
     'crew': [ (packTankman(tankman) if tankman else None) for _, tankman in vehicle.crew ],
     'settings': vehicle.settings,
     'lock': vehicle.lock,
     'repairCost': vehicle.repairCost,
     'health': vehicle.health,
     'gun': packFittingItem(vehicle.gun),
     'turret': packFittingItem(vehicle.turret),
     'engine': packFittingItem(vehicle.engine),
     'chassis': packFittingItem(vehicle.chassis),
     'radio': packFittingItem(vehicle.radio),
     'fuelTank': packFittingItem(vehicle.fuelTank),
     'optDevices': [ (packFittingItem(dev) if dev else None) for dev in vehicle.optDevices.installed ],
     'shells': [ (packShell(shell) if shell else None) for shell in vehicle.shells.installed ],
     'eqs': [ (packFittingItem(eq) if eq else None) for eq in vehicle.consumables.installed ],
     'eqsLayout': [ (packFittingItem(eq) if eq else None) for eq in vehicle.consumables.layout ],
     'type': vehicle.type,
     'isPremium': vehicle.isPremium,
     'isElite': vehicle.isElite,
     'icon': vehicle.icon,
     'isLocked': vehicle.isLocked,
     'isBroken': vehicle.isBroken,
     'isAlive': vehicle.isAlive})
    return result


@dependency.replace_none_kwargs(itemsCache=IItemsCache, goodiesCache=IGoodiesCache, lobbyContext=ILobbyContext)
def packDropSkill(tankman, itemsCache=None, goodiesCache=None, lobbyContext=None):
    items = itemsCache.items
    vehicle = items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
    currentMoney = items.stats.money
    prices = items.shop.dropSkillsCost.values()
    trainingCosts = [ Money(credits=price[Currency.CREDITS] or None, gold=price[Currency.GOLD] or None) for price in prices ]
    defaultCosts = [ Money(credits=price[Currency.CREDITS] or None, gold=price[Currency.GOLD] or None) for price in items.shop.defaults.dropSkillsCost.itervalues() ]
    states = [ cost <= currentMoney or cost.get(Currency.GOLD) is not None for cost in trainingCosts ]
    factors = [ price['xpReuseFraction'] for price in prices ]
    tankmanLevels = [ math.floor(tankman.efficiencyRoleLevel * factor) for factor in factors ]
    result = [ {'level': '{}%'.format(int(lvl)),
     'enabled': state,
     'price': [cost.getCurrency(), cost.getSignValue(cost.getCurrency())],
     'isMoneyEnough': cost <= currentMoney,
     'isNativeVehicle': True,
     'nation': vehicle.nationName,
     'showAction': cost != defCost} for lvl, state, cost, defCost in zip(tankmanLevels, states, trainingCosts, defaultCosts) ]
    rfo = copy.deepcopy(result[0])
    rfo['level'] = '100%'
    recertificationFormGoodie = goodiesCache.getRecertificationForm(currency='gold')
    rfo['enabled'] = SwitchState.ENABLED.value == lobbyContext.getServerSettings().recertificationFormState() and recertificationFormGoodie.enabled and recertificationFormGoodie.count > 0
    result.append(rfo)
    return result


_ButtonData = collections.namedtuple('ButtonData', 'moneyDefault, moneyActual, trainingLevel, state, nativeVehicle')

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def packTraining(vehicle, crew=None, itemsCache=None):
    items = itemsCache.items
    currentMoney = items.stats.money
    trainingCostsActual = items.shop.tankmanCost
    trainingCostsDefault = items.shop.defaults.tankmanCost
    if crew is not None:
        tankmansTrainingData = (_getTrainingButtonsForTankman(trainingCostsActual, trainingCostsDefault, currentMoney, vehicle, tankman) for tankman in crew)
    else:
        tankmansTrainingData = (_getTrainingButtonsForTankman(trainingCostsActual, trainingCostsDefault, currentMoney),)
    result = []
    for buttons in zip(*tankmansTrainingData):
        defaultPrice = min((button.moneyDefault for button in buttons))
        actualPrice = max((button.moneyActual for button in buttons))
        buttonMinLevel = min((button.trainingLevel for button in buttons))
        buttonMaxLevel = max((button.trainingLevel for button in buttons))
        buttonState = any((button.state for button in buttons))
        allNative = all((button.nativeVehicle for button in buttons))
        isRange = crew is not None and len(crew) > 1 and buttonMinLevel != buttonMaxLevel
        currency = actualPrice.getCurrency()
        price = actualPrice.getSignValue(actualPrice.getCurrency())
        result.append({'level': _formatLevel(buttonMinLevel, buttonMaxLevel, isRange),
         'enabled': buttonState,
         'price': [currency, price],
         'isMoneyEnough': currentMoney >= actualPrice or currency == Currency.GOLD,
         'isNativeVehicle': allNative,
         'nation': vehicle.nationName if vehicle is not None else None,
         'showAction': actualPrice != defaultPrice})

    return result


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def repackTankmanWithSkinData(item, data, itemsCache=None, lobbyContext=None):
    if item.skinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        skinItem = itemsCache.items.getCrewSkin(item.skinID)
        data['icon']['big'] = Tankman.getCrewSkinIconBig(skinItem.getIconID())
        data['firstUserName'] = i18n.makeString(skinItem.getFirstName())
        data['lastUserName'] = i18n.makeString(skinItem.getLastName())
        data['fullName'] = localizedFullName(skinItem)
    else:
        data['fullName'] = item.fullUserName


def _getTrainingButtonsForTankman(costsActual, costsDefault, currentMoney, vehicle=None, tankman=None):
    trainingButtonsData = []
    defaults = vehicle is None or tankman is None
    roleLevel = 0
    sameVehicle = True
    sameVehicleType = True
    if not defaults:
        roleLevel = tankman.roleLevel
        sameVehicle = vehicle.intCD == tankman.vehicleNativeDescr.type.compactDescr
        sameVehicleType = sameVehicle if sameVehicle else vehicle.type == tankman.vehicleNativeType
    for costActual, costDefault in zip(costsActual, costsDefault):
        moneyDefault = Money(credits=costDefault[Currency.CREDITS] or None, gold=costDefault[Currency.GOLD] or None)
        moneyActual = Money(credits=costActual[Currency.CREDITS] or None, gold=costActual[Currency.GOLD] or None)
        trainingLevel = defaultTrainingLevel = costActual['roleLevel']
        buttonState = moneyActual <= currentMoney or moneyActual.get(Currency.GOLD) is not None
        if not defaults:
            baseRoleLoss = costActual['baseRoleLoss']
            classChangeRoleLoss = costActual['classChangeRoleLoss']
            if sameVehicle:
                trainingLossMultiplier = 0.0
            elif sameVehicleType:
                trainingLossMultiplier = baseRoleLoss
            else:
                trainingLossMultiplier = baseRoleLoss + classChangeRoleLoss
            trainingLevel = roleLevel - roleLevel * trainingLossMultiplier
            if trainingLevel < defaultTrainingLevel or sameVehicle:
                trainingLevel = defaultTrainingLevel
            buttonState = buttonState and (trainingLevel > roleLevel if sameVehicle else trainingLevel >= defaultTrainingLevel)
        trainingButtonsData.append(_ButtonData(moneyDefault, moneyActual, trainingLevel, buttonState, sameVehicle))

    return trainingButtonsData


def _makeMoneyFromTankmanCost(cost):
    return Money(credits=cost[Currency.CREDITS] or None, gold=cost[Currency.GOLD] or None)


def _formatLevel(minLvl, maxLvl, isRange):
    return '{}-{}%'.format(int(minLvl), int(maxLvl)) if isRange else '{}%'.format(int(maxLvl))
