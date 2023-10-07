# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/serializers.py
import cPickle
from typing import Dict
from helpers import dependency, i18n
from items.components import skills_constants
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
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
     'isActive': True,
     'isEnable': skill.isEnable,
     'roleType': skill.roleType,
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

    rrl = tankman.realRoleLevel
    realRoleLevel = (rrl.lvl, tuple(rrl.bonuses))
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
     'realRoleLevel': realRoleLevel,
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


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def repackTankmanWithSkinData(item, data, itemsCache=None, lobbyContext=None):
    if item.skinID != NO_CREW_SKIN_ID:
        skinItem = itemsCache.items.getCrewSkin(item.skinID)
        data['icon']['big'] = Tankman.getCrewSkinIconBig(skinItem.getIconID())
        data['firstUserName'] = i18n.makeString(skinItem.getFirstName())
        data['lastUserName'] = i18n.makeString(skinItem.getLastName())
        data['fullName'] = localizedFullName(skinItem)
    else:
        data['fullName'] = item.fullUserName
