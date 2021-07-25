# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/serializers.py
import cPickle
import math
import collections
from gui.shared.money import Money, Currency
from helpers import dependency, i18n
from items import vehicles
from items.components import skills_constants
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from gui.shared.gui_items.crew_skin import localizedFullName, getCrewSkinIconBig
from gui.shared.gui_items.fitting_item import ICONS_MASK
from gui.shared.gui_items import Tankman, Vehicle
from items.tankmen import MAX_SKILL_LEVEL, MIN_ROLE_LEVEL_75
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
_LOSS_ACADEMY_LEVEL = 0
_LOSS_SCHOOL_LEVEL_MIN = 10
_LOSS_SCHOOL_LEVEL_MAX = 20
_LOSS_COURSE_LEVEL_MIN = 20
_LOSS_COURSE_LEVEL_MAX = 40

def packTankmanSkill(skill, isPermanent=False, tankman=None):
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


def packTankman(tankman, isCountPermanentSkills=True):

    def vehicleIcon(vDescr, subtype=''):
        return ICONS_MASK % {'type': 'vehicle',
         'subtype': subtype,
         'unicName': vDescr.name.replace(':', '-')}

    nativeVehType = set(vehicles.VEHICLE_CLASS_TAGS & tankman.vehicleNativeDescr.type.tags).pop()
    nativeVehicleData = {'typeCompDescr': tankman.vehicleNativeDescr.type.compactDescr,
     'userName': Vehicle.getShortUserName(tankman.vehicleNativeDescr.type),
     'icon': vehicleIcon(tankman.vehicleNativeDescr),
     'iconContour': vehicleIcon(tankman.vehicleNativeDescr, 'contour/'),
     'type': nativeVehType,
     'typeIconFlat': Vehicle.getTypeFlatIconPath(nativeVehType)}
    currentVehicleData = None
    if tankman.isInTank:
        currentVehicleData = {'inventoryID': tankman.vehicleInvID,
         'typeCompDescr': tankman.vehicleDescr.type.compactDescr,
         'userName': Vehicle.getShortUserName(tankman.vehicleDescr.type),
         'icon': vehicleIcon(tankman.vehicleDescr),
         'iconContour': vehicleIcon(tankman.vehicleDescr, 'contour/')}
    skills = []
    td = tankman.descriptor
    tManFreeSkillsNum = td.freeSkillsNumber
    startSkillNumber = 0 if isCountPermanentSkills else tManFreeSkillsNum
    tManSkills = tankman.skills
    for i in range(startSkillNumber, len(tManSkills)):
        skills.append(packTankmanSkill(tManSkills[i], isPermanent=True if i < tManFreeSkillsNum else False, tankman=tankman))

    return {'strCD': cPickle.dumps(tankman.strCD),
     'inventoryID': tankman.invID,
     'nationID': tankman.nationID,
     'firstUserName': tankman.firstUserName,
     'lastUserName': tankman.lastUserName,
     'roleName': tankman.descriptor.role,
     'rankUserName': tankman.rankUserName,
     'roleUserName': tankman.roleUserName,
     'skills': skills,
     'efficiencyRoleLevel': tankman.efficiencyRoleLevel,
     'realRoleLevel': tankman.realRoleLevel,
     'roleLevel': tankman.roleLevel,
     'icon': {'big': Tankman.getBigIconPath(tankman.nationID, tankman.descriptor.iconID),
              'small': Tankman.getSmallIconPath(tankman.nationID, tankman.descriptor.iconID),
              'barracks': Tankman.getBarracksIconPath(tankman.nationID, tankman.descriptor.iconID)},
     'iconRole': {'big': Tankman.getRoleBigIconPath(tankman.descriptor.role),
                  'medium': Tankman.getRoleMediumIconPath(tankman.descriptor.role),
                  'small': Tankman.getRoleSmallIconPath(tankman.descriptor.role),
                  '42x42': Tankman.getRole42x42IconPath(tankman.descriptor.role)},
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


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def packDropSkill(tankman, itemsCache=None):
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
    return result


_ButtonData = collections.namedtuple('ButtonData', 'moneyDefault, moneyActual, lossLevel, state, nativeVehicle,percentLoss')

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
        buttonMinLevel = min((button.lossLevel for button in buttons))
        buttonMaxLevel = max((button.lossLevel for button in buttons))
        totalMaxLevel = sum((button.lossLevel for button in buttons))
        buttonMaxPercentLoss = max((button.percentLoss for button in buttons))
        buttonState = any((button.state for button in buttons))
        allNative = all((button.nativeVehicle for button in buttons))
        isRange = crew is not None and len(crew) > 1 and buttonMinLevel != buttonMaxLevel
        currency = actualPrice.getCurrency()
        price = actualPrice.getSignValue(actualPrice.getCurrency())
        actionData = {}
        if actualPrice != defaultPrice:
            actionData = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, '{}TankmanCost'.format(currency), True, actualPrice, defaultPrice)
        result.append({'level': _formatLevel(buttonMinLevel, buttonMaxLevel, isRange),
         'penalty': '-{}%'.format(buttonMaxPercentLoss) if buttonMaxPercentLoss else '',
         'penaltyXP': -totalMaxLevel,
         'enabled': buttonState,
         'price': [currency, price],
         'isMoneyEnough': currentMoney >= actualPrice or currency == Currency.GOLD,
         'isNativeVehicle': allNative,
         'nation': vehicle.nationName if vehicle is not None else None,
         'showAction': actualPrice != defaultPrice,
         'actionPrice': actionData})

    return result


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def repackTankmanWithSkinData(item, data, detachmentData, itemsCache=None, lobbyContext=None):
    if detachmentData.skinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        skinItem = itemsCache.items.getCrewSkin(detachmentData.skinID)
        data['icon']['big'] = getCrewSkinIconBig(skinItem.getIconID())
        data['firstUserName'] = i18n.makeString(skinItem.getFirstName())
        data['lastUserName'] = i18n.makeString(skinItem.getLastName())
        data['fullName'] = localizedFullName(skinItem)
    else:
        data['fullName'] = item.fullUserName


def makePercentLoss(roleLevel, sameVehicleType):
    if roleLevel == MAX_SKILL_LEVEL:
        percentLoss = _LOSS_ACADEMY_LEVEL
    elif sameVehicleType:
        percentLoss = _LOSS_SCHOOL_LEVEL_MIN if roleLevel == MIN_ROLE_LEVEL_75 else _LOSS_COURSE_LEVEL_MIN
    else:
        percentLoss = _LOSS_SCHOOL_LEVEL_MAX if roleLevel == MIN_ROLE_LEVEL_75 else _LOSS_COURSE_LEVEL_MAX
    return percentLoss


def _getTrainingButtonsForTankman(costsActual, costsDefault, currentMoney, vehicle=None, tankman=None):
    trainingButtonsData = []
    defaults = vehicle is None or tankman is None
    sameVehicle = True
    sameVehicleType = True
    lossLevel = 0
    percentLoss = 0
    if not defaults:
        sameVehicle = vehicle.intCD == tankman.vehicleNativeDescr.type.compactDescr
        sameVehicleType = sameVehicle if sameVehicle else vehicle.type == tankman.vehicleNativeType
    for costActual, costDefault in zip(costsActual, costsDefault):
        moneyDefault = Money(credits=costDefault[Currency.CREDITS] or None, gold=costDefault[Currency.GOLD] or None)
        moneyActual = Money(credits=costActual[Currency.CREDITS] or None, gold=costActual[Currency.GOLD] or None)
        minRoleLevel = costActual['roleLevel']
        buttonState = moneyActual <= currentMoney or moneyActual.get(Currency.GOLD) is not None
        if not defaults:
            baseRoleLoss = costActual['baseRoleLoss']
            classChangeRoleLoss = costActual['classChangeRoleLoss']
            if sameVehicle:
                lossLevel = 0
                percentLoss = 0
            elif sameVehicleType:
                lossLevel = tankman.descriptor.calculateRealDecreaseXP(baseRoleLoss, minRoleLevel)
                percentLoss = makePercentLoss(minRoleLevel, sameVehicleType)
            else:
                lossLevel = tankman.descriptor.calculateRealDecreaseXP(classChangeRoleLoss, minRoleLevel)
                percentLoss = makePercentLoss(minRoleLevel, sameVehicleType)
        trainingButtonsData.append(_ButtonData(moneyDefault, moneyActual, lossLevel, buttonState, sameVehicle, percentLoss))

    return trainingButtonsData


def _makeMoneyFromTankmanCost(cost):
    return Money(credits=cost[Currency.CREDITS] or None, gold=cost[Currency.GOLD] or None)


def _formatLevel(minLvl, maxLvl, isRange):
    return '{}-{}%'.format(int(minLvl), int(maxLvl)) if isRange else '{}%'.format(int(maxLvl))
