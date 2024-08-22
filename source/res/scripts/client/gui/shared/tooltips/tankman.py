# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/tankman.py
from typing import List, Optional
import nations
from gui import makeHtmlString
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import getFullUserName, getSpecialIconPath, getSkillBigIconPath, Tankman
from gui.shared.tooltips import ToolTipDataField, TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, i18n, time_utils
from helpers.i18n import makeString
from items.components.component_constants import EMPTY_STRING
from items.tankmen import TankmanDescr, MAX_SKILL_LEVEL
from skeletons.gui.game_control import IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_TIME_FORMAT_UNITS = [('days', time_utils.ONE_DAY), ('hours', time_utils.ONE_HOUR), ('minutes', time_utils.ONE_MINUTE)]

def getSkillIcon(skillName, tankmanSkill):
    return backport.image(R.images.gui.maps.icons.tankmen.skills.big.new_skill_with_frame()) if skillName == 'new_skill' else tankmanSkill(skillName=skillName).bigIconPath


class TankmanSkillListField(ToolTipDataField):

    def _getValue(self):
        tankman = self._tooltip.item
        skillsList = self._getBaseSkills(tankman)
        self._addNewSkills(tankman, skillsList)
        return skillsList

    @staticmethod
    def _getBaseSkills(tankman):
        skillsList = []
        for idx, skill in enumerate(tankman.skills):
            skillsList.append({'id': str(idx),
             'label': skill.userName,
             'level': skill.level,
             'enabled': tankman.isInTank or skill.isEnable})

        return skillsList

    def _addNewSkills(self, tankman, skillsList):
        newSkillsCount, newSkillLevel = tankman.newSkillsCount
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
        freeSkills = item.getFreeSkills()
        if freeSkills:
            tankmanSkill = item.getTankmanSkill()
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.NOTRECRUITEDTANKMAN_FREESKILLSTITLE), useHtml=True, padding=formatters.packPadding(top=17 if hasDescr else 18, bottom=10)))
            blocks.append(formatters.packImageListParameterBlockData(listIconSrc=[ formatters.packImageListIconData(getSkillIcon(skillName, tankmanSkill)) for skillName in freeSkills ], columnWidth=52, rowHeight=52, verticalGap=10, horizontalGap=10))
        skills = item.getEarnedSkills(multiplyNew=True)
        if skills:
            tankmanSkill = item.getTankmanSkill()
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.NOTRECRUITEDTANKMAN_SKILLSTITLE), useHtml=True, padding=formatters.packPadding(top=17 if hasDescr else 18, bottom=10)))
            blocks.append(formatters.packImageListParameterBlockData(listIconSrc=[ formatters.packImageListIconData(getSkillIcon(skillName, tankmanSkill)) for skillName in skills ], columnWidth=52, rowHeight=52, verticalGap=10, horizontalGap=10))
        expiryTime = item.getExpiryTime()
        if expiryTime:
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.NOTRECRUITEDTANKMAN_EXPIRETITLE), useHtml=True, padding=formatters.packPadding(top=20 if skills else (17 if hasDescr else 16), bottom=2)))
            expireDateStr = makeString(TOOLTIPS.NOTRECRUITEDTANKMAN_USEBEFORE, date=expiryTime)
            blocks.append(formatters.packTextParameterWithIconBlockData(name=text_styles.premiumVehicleName(expireDateStr), value='', icon=ICON_TEXT_FRAMES.RENTALS, padding=formatters.packPadding(left=-60, bottom=-18), iconYOffset=3))
        items.append(formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=-5)))
        return items


class SpecialTankmanTooltipData(BlocksTooltipData):
    __slots__ = ()

    def __init__(self, ctx):
        super(SpecialTankmanTooltipData, self).__init__(ctx, TOOLTIP_TYPE.SPECIAL_TANKMAN)
        self._setWidth(440)

    def _packBlocks(self, tankmanData, groupName, *args, **kwargs):
        items = super(SpecialTankmanTooltipData, self)._packBlocks()
        blocks = list()
        fullName = getFullUserName(tankmanData.nationID, tankmanData.firstNameID, tankmanData.lastNameID)
        blocks.append(formatters.packImageTextBlockData(title=text_styles.highTitle(fullName), desc=text_styles.main(TOOLTIPS.getNotRecruitedTankmanEventLabel(groupName))))
        blocks.append(formatters.packImageBlockData(img=getSpecialIconPath(tankmanData.nationID, tankmanData.iconID), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        blocks.append(formatters.packSeparatorBlockData(paddings=formatters.packPadding(top=-40), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        blocks.append(formatters.packTextBlockData(text_styles.main(TOOLTIPS.getNotRecruitedTankmanEventDesc(groupName)), useHtml=True, padding=formatters.packPadding(top=18)))
        freeSkills = tankmanData.freeSkills
        if freeSkills:
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.NOTRECRUITEDTANKMAN_FREESKILLSTITLE), useHtml=True, padding=formatters.packPadding(top=17, bottom=10)))
            blocks.append(formatters.packImageListParameterBlockData(listIconSrc=[ formatters.packImageListIconData(getSkillBigIconPath(skill)) for skill in freeSkills ], columnWidth=52, rowHeight=52, verticalGap=10, horizontalGap=10))
        skillNum = self.__getNewSkillCount(tankmanData.freeXP)
        icon = backport.image(R.images.gui.maps.icons.tankmen.skills.big.new_skill_with_frame())
        if skillNum:
            blocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.NOTRECRUITEDTANKMAN_SKILLSTITLE), useHtml=True, padding=formatters.packPadding(top=17, bottom=10)))
            blocks.append(formatters.packImageListParameterBlockData(listIconSrc=[ formatters.packImageListIconData(icon) for _ in range(skillNum) ], columnWidth=52, rowHeight=52, verticalGap=10, horizontalGap=10))
        items.append(formatters.packBuildUpBlockData(blocks, padding=formatters.packPadding(bottom=-5)))
        return items

    def __getNewSkillCount(self, freeXP):
        skillNum = 0
        skillsCost = 0
        while skillsCost <= freeXP:
            skillNum += 1
            skillsCost += sum((TankmanDescr.levelUpXpCost(level, skillNum) for level in xrange(0, MAX_SKILL_LEVEL)))

        return skillNum - 1


class BattleRoyaleTankmanTooltipDataBlock(BlocksTooltipData):
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _skillIconNamePadding = {'padding': formatters.packPadding(left=65),
     'titlePadding': formatters.packPadding(left=6),
     'iconPadding': formatters.packPadding(top=-1)}

    def __init__(self, context):
        super(BattleRoyaleTankmanTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.SKILL)
        self._setWidth(320)
        self.item = None
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(BattleRoyaleTankmanTooltipDataBlock, self)._packBlocks()
        item = self.context.buildItem(*args, **kwargs)
        self.item = item
        vehicle = None
        if item.isInTank:
            vehicle = self._itemsCache.items.getVehicle(item.vehicleInvID)
        fullUserName = self._getFullUserName(item)
        titleBlock = []
        titleBlock.append(formatters.packTitleDescBlock(title=text_styles.highTitle(fullUserName), desc=text_styles.main(self._getTankmanDescription(item))))
        items.append(formatters.packBuildUpBlockData(titleBlock))
        innerBlock = []
        if vehicle:
            self._createLabel(innerBlock)
            self._createVehicleBlock(innerBlock, vehicle)
        if innerBlock:
            items.append(formatters.packBuildUpBlockData(innerBlock, padding=formatters.packPadding(left=0, right=50, top=-5, bottom=0), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        commonStatsBlock = []
        self._createEarnedSkillsBlock(commonStatsBlock)
        if commonStatsBlock:
            items.append(formatters.packBuildUpBlockData(commonStatsBlock, gap=5))
        return items

    def _getSign(self, val):
        return '' if val < 0 else '+'

    def _getBonusValue(self, tankman, ids):
        result = 0
        if tankman:
            bonuses = tankman.realRoleLevel.bonuses
            for idx in ids:
                result += bonuses[idx]

        return int(result)

    def _getVehicleName(self, vehicle=None, nativeVehicle=None):
        return text_styles.main(nativeVehicle.shortUserName) if not vehicle or nativeVehicle.shortUserName == vehicle.shortUserName else text_styles.critical(nativeVehicle.shortUserName)

    def _createLabel(self, innerBlock):
        innerBlock.append(formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'grayTitle', {'message': backport.text(R.strings.tooltips.hangar.crew.assignedTo())})))

    def _createEarnedSkillsBlock(self, commonStatsBlock):
        field = self._getSkillList()
        _, skills = field.buildData()
        if not skills:
            return
        commonStatsBlock.append(formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'grayTitle', {'message': self._crewSpecialSkillsTitle()})))
        maxPopUpBlocks = 14
        for skill in skills[:maxPopUpBlocks]:
            commonStatsBlock.append(formatters.packTextParameterBlockData(text_styles.main(skill['label']), text_styles.stats(str(skill['level']) + '%'), valueWidth=90))

        if len(skills) > maxPopUpBlocks:
            diff = str(len(skills) - maxPopUpBlocks)
            commonStatsBlock.append(formatters.packAlignedTextBlockData(text=text_styles.middleTitle(makeString(TOOLTIPS.HANGAR_CREW_MORESKILLS, skill_cnt=diff)), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))

    def _getFullUserName(self, item):
        nationName = nations.NAMES[item.nationID]
        nationResId = R.strings.battle_royale.commanderInfo.fullName.dyn(nationName)()
        result = backport.text(nationResId)
        return result

    def _crewSpecialSkillsTitle(self):
        return backport.text(R.strings.battle_royale.commanderTooltip.specialty_skills())

    def _getTankmanDescription(self, _):
        return backport.text(R.strings.battle_royale.commanderInfo.commonRank())

    def _getSkillList(self):
        return BattleRoyaleTankmanSkillListField(self, 'skills')

    def _createVehicleBlock(self, innerBlock, vehicle):
        vehName = vehicle.shortUserName
        innerBlock.append(formatters.packTextBlockData(text=text_styles.stats(backport.text(R.strings.battle_royale.commanderTooltip.vehicleDescription(), vehicle=vehName)), padding=formatters.packPadding(top=10, right=-50)))
