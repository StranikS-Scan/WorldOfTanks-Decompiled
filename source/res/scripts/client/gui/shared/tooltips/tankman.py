# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/tankman.py
import math
import nations
from crew2 import settings_globals
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, moneyWithIcon
from gui.shared.gui_items.Tankman import Tankman, getFullUserName, getSkillBigIconPath
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.tooltips import ToolTipDataField, ToolTipAttrField, ToolTipData, TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers import i18n
from helpers import time_utils
from helpers.i18n import makeString
from items.components.component_constants import EMPTY_STRING
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from items.tankmen import SKILLS_BY_ROLES, getSkillsConfig, MAX_SKILL_LEVEL
from shared_utils import findFirst
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
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
        skillsList = self._getBaseSkills(tankman)
        self._addNewSkills(tankman, skillsList)
        return skillsList

    @staticmethod
    def _getBaseSkills(tankman):
        skillsList = []
        idx = 0
        for skill in tankman.skills:
            if skill.name == 'commander_sixthSense':
                continue
            skillsList.append({'id': str(idx),
             'label': skill.userName,
             'level': skill.level,
             'enabled': tankman.isInTank or skill.isEnable})
            idx += 1

        return skillsList

    def _addNewSkills(self, tankman, skillsList):
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


class BattleRoyaleTankmanSkillListField(TankmanSkillListField):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def _getValue(self):
        skills = self.__battleRoyaleController.getBrCommanderSkills()
        skillsList = []
        for idx, skill in enumerate(skills):
            skillsList.append({'id': str(idx),
             'label': skill.userName,
             'level': skill.level,
             'enabled': skill.isEnable})

        return skillsList

    def _addNewSkills(self, tankman, skillsList):
        pass


class TankmanNewSkillCountField(ToolTipDataField):

    def _getValue(self):
        tankman = self._tooltip.item
        return tankman.newSkillCount[0] if not tankman.isDismissed else 0


def formatRecoveryLeftValue(secondsLeft):
    closestUnit = findFirst(lambda (k, v): v < secondsLeft, _TIME_FORMAT_UNITS)
    if closestUnit is not None:
        name, factor = closestUnit
        timeLeft = int(secondsLeft / factor)
        return makeString(TOOLTIPS.template_all_short(name), value=timeLeft)
    else:
        return makeString(TOOLTIPS.TEMPLATE_TIME_LESSTHENMINUTE)


def getRecoveryStatusText(restoreInfo):
    price, timeLeft = restoreInfo
    if not price:
        itemsCache = dependency.instance(IItemsCache)
        restoreConfig = itemsCache.items.shop.tankmenRestoreConfig
        duration = restoreConfig.billableDuration - restoreConfig.freeDuration
        text = makeString(TOOLTIPS.BARRACKS_TANKMEN_RECOVERY_FREE_BODY, totalLeftValue=text_styles.stats(formatRecoveryLeftValue(timeLeft)), freeLeftValue=text_styles.stats(formatRecoveryLeftValue(timeLeft - duration)), price=moneyWithIcon(restoreConfig.cost), withMoneyLeftValue=text_styles.stats(formatRecoveryLeftValue(duration)))
    else:
        text = makeString(TOOLTIPS.BARRACKS_TANKMEN_RECOVERY_GOLD_BODY, totalLeftValue=text_styles.stats(formatRecoveryLeftValue(timeLeft)), price=moneyWithIcon(price))
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


class NotRecruitedTooltipData(BlocksTooltipData):

    def __init__(self, ctx):
        super(NotRecruitedTooltipData, self).__init__(ctx, TOOLTIP_TYPE.NOT_RECRUITED_TANKMAN)
        self._setWidth(350)
        self.item = None
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(NotRecruitedTooltipData, self)._packBlocks()
        item = self.context.buildItem(*args)
        self.item = item
        blocks = list()
        blocks.append(formatters.packImageTextBlockData(title=text_styles.highTitle(item.getFullUserName()), desc=text_styles.main(item.getLabel())))
        specialIcon = item.getSpecialIcon()
        blocks.append(formatters.packImageBlockData(img=specialIcon if specialIcon is not None else item.getBigIcon(), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, width=350 if specialIcon is not None else -1, height=238 if specialIcon is not None else -1))
        blocks.append(formatters.packSeparatorBlockData(paddings=formatters.packPadding(top=-40)))
        descrStr = i18n.makeString(item.getDescription())
        hasDescr = descrStr != EMPTY_STRING
        if hasDescr:
            blocks.append(formatters.packTextBlockData(text_styles.main(descrStr), useHtml=True, padding=formatters.packPadding(top=18)))
        howToGetStr = i18n.makeString(item.getHowToGetInfo())
        hasHowToGetStr = howToGetStr != EMPTY_STRING
        if hasHowToGetStr:
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.tooltips.notrecruitedtankman.howToGet())), useHtml=True, padding=formatters.packPadding(top=17 if hasDescr else 18, bottom=5)))
            blocks.append(formatters.packTextBlockData(text_styles.main(howToGetStr), useHtml=True, padding=formatters.packPadding()))
        skills = item.getLearntSkills(multiplyNew=True)
        if skills:
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.NOTRECRUITEDTANKMAN_SKILLSTITLE), useHtml=True, padding=formatters.packPadding(top=17 if hasDescr else 18, bottom=10)))
            blocks.append(formatters.packImageListParameterBlockData(listIconSrc=[ formatters.packImageListIconData(getSkillBigIconPath(skillName=skillName)) for skillName in skills ], columnWidth=52, rowHeight=52, verticalGap=10, horizontalGap=10))
        expiryTime = item.getExpiryTime()
        if expiryTime:
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.NOTRECRUITEDTANKMAN_EXPIRETITLE), useHtml=True, padding=formatters.packPadding(top=20 if skills else (17 if hasDescr else 16), bottom=2)))
            expireDateStr = makeString(TOOLTIPS.NOTRECRUITEDTANKMAN_USEBEFORE, date=expiryTime)
            blocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.premiumVehicleName(expireDateStr), value='', icon=ICON_TEXT_FRAMES.RENTALS, padding=formatters.packPadding(left=-60, bottom=-18), iconYOffset=3))
        items.append(formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=-5)))
        return items


class TankmanTooltipDataBlock(BlocksTooltipData):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, context):
        super(TankmanTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.SKILL)
        self._setWidth(324)
        self._setContentMargin(top=0, bottom=21)

    def _packBlocks(self, tmanInvID, _=None, desiredVehicleIntCD=None, *args, **kwargs):
        items = super(TankmanTooltipDataBlock, self)._packBlocks(*args, **kwargs)
        tman = self._itemsCache.items.getTankman(int(tmanInvID))
        currentVehicle = None
        if tman.isInTank:
            currentVehicle = self._itemsCache.items.getVehicle(tman.vehicleInvID)
        desiredVehicle = None
        if desiredVehicleIntCD:
            desiredVehicle = self._itemsCache.items.getStockVehicle(desiredVehicleIntCD)
        self._buildTankmanNameBlock(items, tman, desiredVehicle or currentVehicle)
        innerBlocks = []
        self._buildLockCrew(innerBlocks, tman)
        self._buildLeaderInfoBlock(innerBlocks, tman, currentVehicle if desiredVehicle is None else None)
        self._buildUniqueCrewInfoBlock(innerBlocks, tman)
        self._buildNotFullRoleLevelWarningBlock(innerBlocks, tman)
        self._buildInstructorInfoBlock(innerBlocks, tman)
        if innerBlocks:
            items.append(formatters.packBuildUpBlockData(innerBlocks, gap=8, padding=formatters.packPadding(top=-2, bottom=-8)))
        self._buildVehicleInfoBlock(items, currentVehicle)
        self._buildNeedSpecializationForVehicleErrorBlock(items, tman, currentVehicle)
        if tman.skills or tman.hasNewSkill():
            self._createBlockForWarningSkillsNotWorking(items, tman, True)
        self._buildDismissedBlock(items, tman)
        self._buildStateBlock(items, tman)
        return items

    def _buildTankmanNameBlock(self, items, tman, desiredVehicle):
        fullUserName = self._getFullUserName(tman)
        nativeVehicle = self._itemsCache.items.getItemByCD(tman.vehicleNativeDescr.type.compactDescr)
        vehicleName = nativeVehicle.userName
        if desiredVehicle and desiredVehicle.intCD != tman.vehicleNativeDescr.type.compactDescr:
            vehicleName = text_styles.error(vehicleName)
        items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(fullUserName), desc=text_styles.main(backport.text(R.strings.tooltips.hangar.crew.tman_name.text(), roleName=tman.roleUserName, vehicleName=vehicleName)), padding=formatters.packPadding(top=12, bottom=-1)))

    def _buildLockCrew(self, items, tman):
        nativeVehicle = self._itemsCache.items.getItemByCD(tman.vehicleNativeDescr.type.compactDescr)
        if nativeVehicle.isCrewLocked:
            items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.lockIcon()), imgPadding=formatters.packPadding(left=4, top=4, right=7), desc=text_styles.main(backport.text(R.strings.tooltips.hangar.crew.is_lock_crew.header()))))

    def _getFullUserName(self, tman):
        if tman.skinID != NO_CREW_SKIN_ID and self._lobbyContext.getServerSettings().isCrewSkinsEnabled():
            skinItem = self._itemsCache.items.getCrewSkin(tman.skinID)
            return localizedFullName(skinItem)
        return tman.fullUserName

    def _buildLeaderInfoBlock(self, items, tman, vehicle):
        if not tman.isLeader:
            return
        items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.attentionIcon()), imgPadding=formatters.packPadding(left=-1, right=3, top=2), title=text_styles.yellowTitle(backport.text(R.strings.tooltips.hangar.crew.is_leader.header())), padding=formatters.packPadding(left=2)))
        if vehicle and len(self._getLeadersFromVehicle(vehicle)) > 1:
            items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.alertIcon()), imgPadding=formatters.packPadding(left=0, top=1, right=5), desc=text_styles.statusAlertSmall(backport.text(R.strings.tooltips.hangar.crew.too_many_leaders.header())), padding=formatters.packPadding(top=-8)))
        detachmentPreset = settings_globals.g_conversion.getDetachmentForTankman(tman.descriptor)
        if detachmentPreset and detachmentPreset.instructorSlots:
            instructorsCount = len(detachmentPreset.instructorSlots)
            if instructorsCount:
                uniqueCrewName = backport.text(R.strings.detachment.presetName.dyn(detachmentPreset.name)())
                items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.detachment.icons.instr_4_icon()), imgPadding=formatters.packPadding(left=-20, top=-14, right=-9), title=text_styles.blueBoosterTitle(backport.text(R.strings.tooltips.hangar.crew.instructors_for_leader.header())), desc=text_styles.mainFieldSmall(makeHtmlString('html_templates:lobby/detachment', 'instructorsForLeader', ctx={'uniqueCrewName': uniqueCrewName})), padding=formatters.packPadding(bottom=-14)))

    def _getLeadersFromVehicle(self, vehicle):
        return [ tman for _, tman in vehicle.crew if tman and tman.isLeader ]

    def _buildUniqueCrewInfoBlock(self, items, tman):
        detachmentPresetName, _ = settings_globals.g_conversion.getUnremovableInstructorForTankman(tman.descriptor)
        if not detachmentPresetName:
            return
        detachmentPreset = settings_globals.g_detachmentSettings.presets.getDetachmentPreset(detachmentPresetName)
        uniqueCrewName = backport.text(R.strings.detachment.presetName.dyn(detachmentPreset.name)())
        commanderPreset = detachmentPreset.commander
        commanderName = getFullUserName(detachmentPreset.nationID, commanderPreset.firstNameID, commanderPreset.secondNameID)
        items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.attentionIcon()), imgPadding=formatters.packPadding(left=1, top=3, right=3), title=text_styles.yellowTitle(backport.text(R.strings.tooltips.hangar.crew.is_unique_crew_member.header(), crewName=uniqueCrewName)), desc=text_styles.brownSmall(backport.text(R.strings.tooltips.hangar.crew.is_unique_crew_member.text(), crewName=uniqueCrewName, commanderName=commanderName))))

    def _buildInstructorInfoBlock(self, items, tman):
        if not tman.isInstructor:
            return
        items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.detachment.icons.instr_1_icon()), imgPadding=formatters.packPadding(left=-16, top=-14, right=-12), title=text_styles.blueBoosterTitle(backport.text(R.strings.tooltips.hangar.crew.instructor_info.header())), desc=text_styles.mainFieldSmall(backport.text(R.strings.tooltips.hangar.crew.instructor_info.text())), padding=formatters.packPadding(bottom=-14)))

    def _buildNotFullRoleLevelWarningBlock(self, items, tman):
        if tman.roleLevel < MAX_SKILL_LEVEL and not tman.skills:
            items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.WarningIcon_1()), imgPadding=formatters.packPadding(top=2, right=4), title=text_styles.yellowTitle(backport.text(R.strings.tooltips.hangar.crew.not_full_role.header())), desc=text_styles.brownSmall(backport.text(R.strings.tooltips.hangar.crew.not_full_role.text(), roleLevel=text_styles.stats('{}%'.format(tman.roleLevel)))), descPadding=formatters.packPadding(top=-2), padding=formatters.packPadding(bottom=1)))

    def _buildVehicleInfoBlock(self, items, vehicle):
        if not vehicle:
            return
        vehType = vehicle.type.replace('-', '_')
        innerBlock = [formatters.packTextBlockData(text=text_styles.grayTitle(backport.text(R.strings.tooltips.hangar.crew.assignedTo())), padding=formatters.packPadding(top=9)), formatters.packImageTextBlockData(img=vehicle.iconContour, flipHorizontal=True, padding=formatters.packPadding(top=8, bottom=-2), title=text_styles.stats(vehicle.shortUserName), desc=text_styles.stats(backport.text(R.strings.menu.header.vehicleType.dyn(vehType)())), descPadding=formatters.packPadding(top=-4))]
        items.append(formatters.packBuildUpBlockData(innerBlock, padding=formatters.packPadding(top=-17, bottom=-6), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))

    def _buildNeedSpecializationForVehicleErrorBlock(self, items, tman, vehicle):
        if vehicle and vehicle.intCD != tman.vehicleNativeDescr.type.compactDescr:
            items.append(formatters.packTitleDescBlock(title=text_styles.errorBold(backport.text(R.strings.tooltips.hangar.crew.need_vehicle_specialization.header(), vehicleName=vehicle.userName)), desc=text_styles.mainFieldSmall(backport.text(R.strings.tooltips.hangar.crew.need_vehicle_specialization.text())), descPadding=formatters.packPadding(top=-2), padding=formatters.packPadding(top=-2, bottom=-8)))

    def _builSixthSenseInfoBlock(self, items):
        items.append(formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.tankmen.skills.small.commander_sixthSense()), imgPadding=formatters.packPadding(top=4, right=5), title=text_styles.mainTitle(backport.text(R.strings.tooltips.hangar.crew.commander_sixth_sense.header())), desc=text_styles.standardSmall(backport.text(R.strings.tooltips.hangar.crew.commander_sixth_sense.text())), padding=formatters.packPadding(top=-2, bottom=-1)))

    def _createBlockForWarningSkillsNotWorking(self, items, tman, showSixSenth):
        blocks = [formatters.packImageTextBlockData(img=backport.image(R.images.gui.maps.icons.library.alertIcon()), imgPadding=formatters.packPadding(top=3, right=3), title=text_styles.statusAlert(backport.text(R.strings.tooltips.hangar.crew.skills_not_working.header())), desc=text_styles.statusAlertSmall(backport.text(R.strings.tooltips.hangar.crew.skills_not_working.text())))]
        self._createSkillsBlock(blocks, tman, showSixSenth)
        items.append(formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(top=-2, bottom=-8)))

    def _createSkillsBlock(self, items, tman, showSixSenth):
        skills = [ {'label': backport.text(R.strings.tooltips.hangar.crew.is_permanent_skill(), skillName=skill.userName) if skill.isPermanent else skill.userName,
         'level': skill.level} for skill in tman.skills if skill.name != 'commander_sixthSense' or showSixSenth ]
        maxPopUpBlocks = 10
        commonStatsBlock = [ formatters.packTextParameterBlockData(text_styles.main(skill['label']), text_styles.stats('{}%'.format(skill['level'])), valueWidth=90) for skill in skills[:maxPopUpBlocks] ]
        newSkillsCount, lastSkillLevel = tman.newSkillCount
        isPartialLastSkill = bool(newSkillsCount > 0 and lastSkillLevel < MAX_SKILL_LEVEL)
        fullSkillPoints = newSkillsCount - int(isPartialLastSkill)
        if fullSkillPoints:
            commonStatsBlock.append(formatters.packTextParameterBlockData(text_styles.main(backport.text(R.strings.tooltips.barracks.tankmen.recovery.newSkill())), text_styles.stats('{}x{}%'.format(fullSkillPoints, MAX_SKILL_LEVEL)), valueWidth=90))
        if isPartialLastSkill:
            commonStatsBlock.append(formatters.packTextParameterBlockData(text_styles.main(backport.text(R.strings.tooltips.barracks.tankmen.recovery.newSkill())), text_styles.stats('{}%'.format(lastSkillLevel)), valueWidth=90))
        if len(skills) > maxPopUpBlocks:
            diff = len(skills) - maxPopUpBlocks
            commonStatsBlock.append(formatters.packTextBlockData(text=text_styles.stats(makeString(TOOLTIPS.HANGAR_CREW_MORESKILLS, skill_cnt=diff)), padding=formatters.packPadding(left=95)))
        if commonStatsBlock:
            items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=5, padding=formatters.packPadding(top=8, bottom=-7, left=-30)))

    def _buildStateBlock(self, items, tman):
        state = tman.getTankmanState()
        if not state:
            return
        items.append(formatters.packAlignedTextBlockData(text=text_styles.mainTitle(state), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-7, bottom=-1)))

    def _buildDismissedBlock(self, items, tman):
        if not tman.isDismissed:
            return
        items.append(formatters.packTitleDescBlock(title=text_styles.whiteOrangeTitle(backport.text(R.strings.tooltips.hangar.crew.is_dismissed.header())), desc=getRecoveryStatusText(getTankmenRestoreInfo(tman)), descPadding=formatters.packPadding(top=-4), padding=formatters.packPadding(top=-3, bottom=-8)))


class BattleRoyaleTankmanTooltipDataBlock(TankmanTooltipDataBlock):

    def _getFullUserName(self, item):
        nationName = nations.NAMES[item.nationID]
        nationResId = R.strings.battle_royale.commanderInfo.fullName.dyn(nationName)()
        result = backport.text(nationResId)
        return result

    def _getTankmanDescription(self, _):
        return backport.text(R.strings.battle_royale.commanderInfo.commonRank())

    def _getSkillList(self):
        return BattleRoyaleTankmanSkillListField(self, 'skills')

    def _createVehicleBlock(self, innerBlock, vehicle):
        vehName = vehicle.shortUserName
        innerBlock.append(formatters.packTextBlockData(text=text_styles.stats(backport.text(R.strings.battle_royale.commanderTooltip.vehicleDescription(), vehicle=vehName)), padding=formatters.packPadding(top=10, right=-50)))

    def _createBlockForNewSkills(self, items):
        pass

    def _createMoreInfoBlock(self, items):
        pass


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


class TankmanDemobilizedStateTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(TankmanDemobilizedStateTooltipData, self).__init__(context, TOOLTIP_TYPE.TANKMAN)
        self._setContentMargin(bottom=8)

    def _packBlocks(self, *args, **kwargs):
        items = super(TankmanDemobilizedStateTooltipData, self)._packBlocks()
        tman = self.context.buildItem(*args, **kwargs)
        items.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.barracks.tankmen.recoveryBtn.header())), desc=getRecoveryStatusText(getTankmenRestoreInfo(tman))))
        return items
