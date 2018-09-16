# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/tankman.py
import math
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.shared.tooltips import ToolTipDataField, ToolTipAttrField, ToolTipData, TOOLTIP_TYPE, formatters
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from helpers import time_utils
from helpers.i18n import makeString
from items.tankmen import SKILLS_BY_ROLES, getSkillsConfig
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, moneyWithIcon
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui import makeHtmlString
from gui.shared.tooltips.common import BlocksTooltipData
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
TANKMAN_DISMISSED = 'dismissed'
_TIME_FORMAT_UNITS = [('days', time_utils.ONE_DAY), ('hours', time_utils.ONE_HOUR), ('minutes', time_utils.ONE_MINUTE)]

class TankmanRoleLevelField(ToolTipDataField):

    def _getValue(self):
        tankman = self._tooltip.item
        if tankman:
            roleLevel, _ = tankman.realRoleLevel
            return roleLevel


class TankmanRoleBonusesField(ToolTipDataField):

    class BONUSES(object):
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
        if tankman:
            _, roleBonuses = tankman.realRoleLevel
            for idx in self.__ids:
                result += int(math.ceil(float(roleBonuses[idx])))

        return result


class TankmanCurrentVehicleAttrField(ToolTipAttrField):
    itemsCache = dependency.descriptor(IItemsCache)

    def _getItem(self):
        tankman = self._tooltip.item
        return self.itemsCache.items.getVehicle(tankman.vehicleInvID) if tankman and tankman.isInTank else None


class TankmanNativeVehicleAttrField(ToolTipAttrField):
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
            elif inactiveRoles:

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


class TankmanTooltipDataBlock(BlocksTooltipData):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(TankmanTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.SKILL)
        self._setWidth(320)
        self.item = None
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(TankmanTooltipDataBlock, self)._packBlocks()
        item = self.context.buildItem(*args, **kwargs)
        self.item = item
        vehicle = None
        nativeVehicle = self.itemsCache.items.getItemByCD(item.vehicleNativeDescr.type.compactDescr)
        if item.isInTank:
            vehicle = self.itemsCache.items.getVehicle(item.vehicleInvID)
        items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(item.fullUserName), desc=text_styles.main(item.rankUserName)))
        innerBlock = []
        if vehicle:
            innerBlock.append(formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'grayTitle', {'message': makeString(TOOLTIPS.HANGAR_CREW_ASSIGNEDTO)})))
            footballRole = vehicle.getFootballRole()
            if footballRole is not None:
                vehType = footballRole
            else:
                vehType = vehicle.type
            innerBlock.append(formatters.packImageTextBlockData(img=vehicle.iconContour, txtGap=-4, padding=formatters.packPadding(bottom=0, top=10, left=0), title=text_styles.stats(vehicle.shortUserName), desc=text_styles.stats('#menu:header/vehicleType/%s' % vehType), flipHorizontal=True))
        if innerBlock:
            items.append(formatters.packBuildUpBlockData(innerBlock, padding=formatters.packPadding(left=0, right=50, top=-5, bottom=0), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        commonStatsBlock = [formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'grayTitle', {'message': makeString(TOOLTIPS.HANGAR_CREW_SPECIALTY_SKILLS)}))]
        penalty = self._getBonusValue(item, [TankmanRoleBonusesField.BONUSES.PENALTY])
        addition = self._getBonusValue(item, [TankmanRoleBonusesField.BONUSES.COMMANDER,
         TankmanRoleBonusesField.BONUSES.EQUIPMENTS,
         TankmanRoleBonusesField.BONUSES.DEVICES,
         TankmanRoleBonusesField.BONUSES.BROTHERHOOD])
        addition_ = '' if addition == 0 else self._getSign(addition) + str(addition)
        penalty_ = '' if penalty == 0 else self._getSign(penalty) + str(penalty)
        if penalty != 0 or addition != 0:
            addRoleLevels = ' (' + str(item.roleLevel) + addition_ + penalty_ + ')'
        else:
            addRoleLevels = ''
        if not vehicle or nativeVehicle.shortUserName == vehicle.shortUserName:
            vehicleName = text_styles.main(nativeVehicle.shortUserName)
        else:
            vehicleName = text_styles.critical(nativeVehicle.shortUserName)
        commonStatsBlock.append(formatters.packTextParameterBlockData(text_styles.main(item.roleUserName + ' ') + vehicleName, text_styles.stats(str(item.roleLevel + penalty + addition) + '%' + addRoleLevels), valueWidth=90, padding=formatters.packPadding(left=0, right=0, top=5, bottom=0)))
        field = TankmanSkillListField(self, 'skills')
        _, value = field.buildData()
        skills = value
        maxPopUpBlocks = 14
        for skill in skills[:maxPopUpBlocks]:
            commonStatsBlock.append(formatters.packTextParameterBlockData(text_styles.main(skill['label']), text_styles.stats(str(skill['level']) + '%'), valueWidth=90))

        if len(skills) > maxPopUpBlocks:
            diff = str(len(skills) - maxPopUpBlocks)
            commonStatsBlock.append(formatters.packAlignedTextBlockData(text=text_styles.middleTitle(makeString(TOOLTIPS.HANGAR_CREW_MORESKILLS, skill_cnt=diff)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=5))
        field = TankmanNewSkillCountField(self, '')
        _, newSkillCount = field.buildData()
        isEvent = g_currentVehicle.item.isEvent
        if newSkillCount > 0 and not isEvent:
            items.append(formatters.packImageTextBlockData(img='../maps/icons/tankmen/skills/small/new_skill.png', txtOffset=20, padding=formatters.packPadding(bottom=0, top=5, left=0), imgPadding=formatters.packPadding(left=0, top=3), title=makeHtmlString('html_templates:lobby/textStyle', 'goldTextTitle', {'message': makeString(TOOLTIPS.HANGAR_CREW_NEW_SKILL_AVAILABLE_HEADER)}), desc=makeHtmlString('html_templates:lobby/textStyle', 'goldTextField', {'message': makeString(TOOLTIPS.HANGAR_CREW_NEW_SKILL_AVAILABLE_TEXT)})))
        elif isEvent:
            items.append(formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_32X32, txtOffset=80, padding=formatters.packPadding(bottom=5, top=2, left=5), imgPadding=formatters.packPadding(bottom=10, left=30, top=5), title=makeHtmlString('html_templates:lobby/textStyle', 'alertText', {'message': makeString(FOOTBALL2018.FOOTBALL_CREW_SKILLS_DISABLED)}), txtAlign='center'))
        field = TankmanStatusField(self, '')
        _, status = field.buildData()
        if status['header'] != '':
            items.append(formatters.packImageTextBlockData(title=text_styles.warning(status['header']), desc=makeHtmlString('html_templates:lobby/textStyle', 'statusWarningField', {'message': status['text']})))
        return items

    def _getSign(self, val):
        return '' if val < 0 else '+'

    def _getBonusValue(self, tankman, ids):
        result = 0
        if tankman:
            _, roleBonuses = tankman.realRoleLevel
            for idx in ids:
                result += roleBonuses[idx]

        return int(result)


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
