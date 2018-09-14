# Embedded file name: scripts/client/gui/shared/tooltips/tankman.py
import BigWorld
from gui.shared import g_itemsCache
from gui.shared.tooltips import ToolTipDataField, ToolTipAttrField, ToolTipData, TOOLTIP_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from helpers.i18n import makeString
from items.tankmen import SKILLS_BY_ROLES, getSkillsConfig

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

    def _getItem(self):
        tankman = self._tooltip.item
        if tankman.isInTank:
            return g_itemsCache.items.getVehicle(tankman.vehicleInvID)
        else:
            return None


class TankmanNativeVehicleAttrField(ToolTipAttrField):

    def _getItem(self):
        tankman = self._tooltip.item
        return g_itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)


class TankmanSkillListField(ToolTipDataField):

    def _getValue(self):
        tankman = self._tooltip.item
        skillsList = []
        for idx, skill in enumerate(tankman.skills):
            skillsList.append({'id': str(idx),
             'label': skill.userName,
             'level': skill.level,
             'enabled': tankman.isInTank or skill.isEnable})

        return skillsList


class TankmanNewSkillCountField(ToolTipDataField):

    def _getValue(self):
        return self._tooltip.item.newSkillCount[0]


class TankmanStatusField(ToolTipDataField):

    def _getValue(self):
        header = ''
        text = ''
        statusTemplate = '#tooltips:tankman/status/%s'
        tankman = self._tooltip.item
        vehicle = None
        if tankman.isInTank:
            vehicle = g_itemsCache.items.getVehicle(tankman.vehicleInvID)
        nativeVehicle = g_itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
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
                return makeString(statusTemplate % 'inactiveSkillsRoleFormat') % makeString(getSkillsConfig()[role]['userString'])

            header = makeString(statusTemplate % 'inactiveSkills/header')
            text = makeString(statusTemplate % 'inactiveSkills/text') % {'skills': ', '.join([ roleFormat(role) for role in inactiveRoles ])}
        return {'header': header,
         'text': text,
         'level': Vehicle.VEHICLE_STATE_LEVEL.WARNING}

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
