# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/tankman.py
import math
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.shared.tooltips import ToolTipDataField, ToolTipAttrField, ToolTipData, TOOLTIP_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from helpers import time_utils
from helpers.i18n import makeString
from items.tankmen import SKILLS_BY_ROLES, getSkillsConfig
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, moneyWithIcon
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
TANKMAN_DISMISSED = 'dismissed'
_TIME_FORMAT_UNITS = [('days', time_utils.ONE_DAY), ('hours', time_utils.ONE_HOUR), ('minutes', time_utils.ONE_MINUTE)]

class TankmanRoleLevelField(ToolTipDataField):

    def _getValue(self):
        tankman = self._tooltip.item
        roleLevel, _ = tankman.realRoleLevel
        return roleLevel


class TankmanRoleBonusesField(ToolTipDataField):

    class BONUSES:
        COMMANDER = 0
        BROTHERHOOD = 1
        EQUIPMENTS = 2
        DEVICES = 3
        PENALTY = 4

    def __init__(self, context, name, ids):
        super(TankmanRoleBonusesField, self).__init__(context, name)
        self.__ids = ids

    def _getValue(self):
        tankman = self._tooltip.item
        result = 0
        _, roleBonuses = tankman.realRoleLevel
        for idx in self.__ids:
            result += roleBonuses[idx]

        return result


class TankmanCurrentVehicleAttrField(ToolTipAttrField):
    """Tankman current vehicle data field"""
    itemsCache = dependency.descriptor(IItemsCache)

    def _getItem(self):
        tankman = self._tooltip.item
        return self.itemsCache.items.getVehicle(tankman.vehicleInvID) if tankman.isInTank else None


class TankmanNativeVehicleAttrField(ToolTipAttrField):
    """Tankman native vehicle data field."""
    itemsCache = dependency.descriptor(IItemsCache)

    def _getItem(self):
        tankman = self._tooltip.item
        return self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)


class TankmanSkillListField(ToolTipDataField):

    def _getValue(self):
        tankman = self._tooltip.item
        skillsList = []
        for idx, skill in enumerate(tankman.skills):
            skillsList.append({'id': str(idx),
             'label': skill.userName,
             'level': skill.level,
             'enabled': tankman.isInTank or skill.isEnable})

        newSkillsCount, newSkillLevel = tankman.newSkillCount
        if newSkillsCount > 0:
            if newSkillsCount > 2:
                newSkills = [str(newSkillsCount - 1) + 'x100']
            elif newSkillsCount == 2:
                newSkills = [100]
            else:
                newSkills = []
            if newSkillLevel > 0:
                newSkills.append(newSkillLevel)
            newSkillStr = makeString(TOOLTIPS.BARRACKS_TANKMEN_RECOVERY_NEWSKILL)
            for idx, skillLevel in enumerate(newSkills, start=len(skillsList)):
                skillsList.append({'id': str(idx),
                 'label': newSkillStr,
                 'level': skillLevel,
                 'enabled': False})

        return skillsList


class TankmanNewSkillCountField(ToolTipDataField):

    def _getValue(self):
        tankman = self._tooltip.item
        return tankman.newSkillCount[0] if not tankman.isDismissed else 0


def formatRecoveryLeftValue(secondsLeft):
    closestUnit = findFirst(lambda (k, v): v < secondsLeft, _TIME_FORMAT_UNITS)
    if closestUnit is not None:
        name, factor = closestUnit
        timeLeft = int(math.ceil(float(secondsLeft) / factor))
        return makeString(TOOLTIPS.template_all_short(name), value=timeLeft)
    else:
        return makeString(TOOLTIPS.TEMPLATE_TIME_LESSTHENMINUTE)
        return


def getRecoveryStatusText(restoreInfo):
    price, timeLeft = restoreInfo
    if not price:
        itemsCache = dependency.instance(IItemsCache)
        restoreConfig = itemsCache.items.shop.tankmenRestoreConfig
        duration = restoreConfig.billableDuration - restoreConfig.freeDuration
        text = makeString(TOOLTIPS.BARRACKS_TANKMEN_RECOVERY_FREE_BODY, totalLeftValue=formatRecoveryLeftValue(timeLeft), freeLeftValue=formatRecoveryLeftValue(timeLeft - duration), price=moneyWithIcon(restoreConfig.cost), withMoneyLeftValue=formatRecoveryLeftValue(duration))
    else:
        text = makeString(TOOLTIPS.BARRACKS_TANKMEN_RECOVERY_GOLD_BODY, totalLeftValue=formatRecoveryLeftValue(timeLeft), price=moneyWithIcon(price))
    return text_styles.main(text)


class TankmanStatusField(ToolTipDataField):
    """Tankman status data field."""
    itemsCache = dependency.descriptor(IItemsCache)

    def _getValue(self):
        header = ''
        text = ''
        statusTemplate = '#tooltips:tankman/status/%s'
        tankman = self._tooltip.item
        vehicle = None
        if tankman.isInTank:
            vehicle = self.itemsCache.items.getVehicle(tankman.vehicleInvID)
        nativeVehicle = self.itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
        if tankman.isDismissed:
            return {'header': text_styles.warning(TOOLTIPS.BARRACKS_TANKMEN_RECOVERY_HEADER),
             'text': getRecoveryStatusText(getTankmenRestoreInfo(tankman)),
             'level': TANKMAN_DISMISSED}
        else:
            inactiveRoles = list()
            if tankman.isInTank:
                for skill in tankman.skills:
                    if not skill.isEnable:
                        role = self.__getRoleBySkill(skill)
                        if role not in inactiveRoles:
                            inactiveRoles.append(role)

            if vehicle is not None and nativeVehicle.innationID != vehicle.innationID:
                if (vehicle.isPremium or vehicle.isPremiumIGR) and vehicle.type in nativeVehicle.tags:
                    header = makeString(statusTemplate % 'wrongPremiumVehicle/header')
                    text = makeString(statusTemplate % 'wrongPremiumVehicle/text') % {'vehicle': vehicle.shortUserName}
                else:
                    header = makeString(statusTemplate % 'wrongVehicle/header') % {'vehicle': vehicle.shortUserName}
                    text = makeString(statusTemplate % 'wrongVehicle/text')
            elif len(inactiveRoles):

                def roleFormat(role):
                    return makeString(statusTemplate % 'inactiveSkillsRoleFormat') % makeString(getSkillsConfig().getSkill(role).userString)

                header = makeString(statusTemplate % 'inactiveSkills/header')
                text = makeString(statusTemplate % 'inactiveSkills/text') % {'skills': ', '.join([ roleFormat(role) for role in inactiveRoles ])}
            return {'header': header,
             'text': text,
             'level': Vehicle.VEHICLE_STATE_LEVEL.WARNING}
            return

    def __getRoleBySkill(self, skill):
        for role, skills in SKILLS_BY_ROLES.iteritems():
            if skill.name in skills:
                return role


class TankmanTooltipData(ToolTipData):

    def __init__(self, context):
        super(TankmanTooltipData, self).__init__(context, TOOLTIP_TYPE.TANKMAN)
        self.fields = (ToolTipAttrField(self, 'name', 'fullUserName'),
         ToolTipAttrField(self, 'rank', 'rankUserName'),
         ToolTipAttrField(self, 'role', 'roleUserName'),
         ToolTipAttrField(self, 'roleLevel'),
         ToolTipAttrField(self, 'isInTank'),
         ToolTipAttrField(self, 'iconRole'),
         ToolTipAttrField(self, 'nation', 'nationID'),
         TankmanRoleLevelField(self, 'efficiencyRoleLevel'),
         TankmanRoleBonusesField(self, 'addition', [TankmanRoleBonusesField.BONUSES.COMMANDER,
          TankmanRoleBonusesField.BONUSES.EQUIPMENTS,
          TankmanRoleBonusesField.BONUSES.DEVICES,
          TankmanRoleBonusesField.BONUSES.BROTHERHOOD]),
         TankmanRoleBonusesField(self, 'penalty', [TankmanRoleBonusesField.BONUSES.PENALTY]),
         TankmanNativeVehicleAttrField(self, 'vehicleType', 'type'),
         TankmanNativeVehicleAttrField(self, 'vehicleName', 'shortUserName'),
         TankmanCurrentVehicleAttrField(self, 'currentVehicleType', 'type'),
         TankmanCurrentVehicleAttrField(self, 'currentVehicleName', 'shortUserName'),
         TankmanSkillListField(self, 'skills'),
         TankmanNewSkillCountField(self, 'newSkillsCount'),
         TankmanCurrentVehicleAttrField(self, 'vehicleContour', 'iconContour'),
         TankmanCurrentVehicleAttrField(self, 'isCurrentVehiclePremium', 'isPremium'),
         TankmanStatusField(self, 'status'))
