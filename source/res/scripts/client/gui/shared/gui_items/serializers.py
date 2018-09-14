# Embedded file name: scripts/client/gui/shared/gui_items/serializers.py
import cPickle
from items import tankmen
from gui.shared.gui_items import _ICONS_MASK, Tankman, Vehicle

def packTankmanSkill(skill, isPermanent = False):
    if skill.roleType in tankmen.getSkillsConfig():
        roleIconPath = Tankman.getRoleSmallIconPath(skill.roleType)
    else:
        roleIconPath = ''
    return {'name': skill.name,
     'level': skill.level,
     'userName': skill.userName,
     'description': skill.description,
     'shortDescription': skill.shortDescription,
     'icon': {'big': Tankman.getSkillBigIconPath(skill.name),
              'small': Tankman.getSkillSmallIconPath(skill.name),
              'role': roleIconPath},
     'isActive': skill.isActive,
     'isEnable': skill.isEnable,
     'roleType': skill.roleType,
     'isPerk': skill.isPerk,
     'isPermanent': isPermanent}


def packTankman(tankman, isCountPermanentSkills = True):

    def vehicleIcon(vDescr, subtype = ''):
        return _ICONS_MASK % {'type': 'vehicle',
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
    skills = []
    tManFreeSkillsNum = tankman.descriptor.freeSkillsNumber
    startSkillNumber = 0 if isCountPermanentSkills else tManFreeSkillsNum
    tManSkills = tankman.skills
    for i in range(startSkillNumber, len(tManSkills)):
        skills.append(packTankmanSkill(tManSkills[i], isPermanent=True if i < tManFreeSkillsNum else False))

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
                  'small': Tankman.getRoleSmallIconPath(tankman.descriptor.role)},
     'iconRank': {'big': Tankman.getRankBigIconPath(tankman.nationID, tankman.descriptor.rankID),
                  'small': Tankman.getRankSmallIconPath(tankman.nationID, tankman.descriptor.rankID)},
     'isInTank': tankman.isInTank,
     'newSkillsCount': tankman.newSkillCount,
     'nativeVehicle': nativeVehicleData,
     'currentVehicle': currentVehicleData}


def packFittingItem(item):
    return {'buyPrice': item.buyPrice,
     'defBuyPrice': item.defaultPrice,
     'actionPrc': item.actionPrc,
     'sellPrice': item.sellPrice,
     'defSellPrice': item.defaultSellPrice,
     'sellActionPrc': item.sellActionPrc,
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
     'defaulCount': shell.defaultCount,
     'kind': shell.type})
    return result


def packVehicle(vehicle):
    result = packFittingItem(vehicle)
    result.update({'buyPrice': vehicle.buyPrice,
     'defBuyPrice': vehicle.defaultPrice,
     'actionPrc': vehicle.actionPrc,
     'sellPrice': vehicle.sellPrice,
     'defSellPrice': vehicle.defaultSellPrice,
     'sellActionPrc': vehicle.sellActionPrc,
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
     'inventoryID': vehicle.inventoryID,
     'xp': vehicle.xp,
     'dailyXPFactor': vehicle.dailyXPFactor,
     'clanLock': vehicle.clanLock,
     'isUnique': vehicle.isUnique,
     'crew': [ (packTankman(tankman) if tankman else None) for role, tankman in vehicle.crew ],
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
     'optDevices': [ (packFittingItem(dev) if dev else None) for dev in vehicle.optDevices ],
     'shells': [ (packShell(shell) if shell else None) for shell in vehicle.shells ],
     'eqs': [ (packFittingItem(eq) if eq else None) for eq in vehicle.eqs ],
     'eqsLayout': [ (packFittingItem(eq) if eq else None) for eq in vehicle.eqsLayout ],
     'type': vehicle.type,
     'isPremium': vehicle.isPremium,
     'isElite': vehicle.isElite,
     'icon': vehicle.icon,
     'isLocked': vehicle.isLocked,
     'isBroken': vehicle.isBroken,
     'isAlive': vehicle.isAlive})
    return result
