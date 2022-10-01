# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/comp7_tooltips.py
import logging
import typing
from gui import g_htmlTemplates
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, getRoleText
from gui.shared.items_parameters import formatters as params_formatters
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips.module import ModuleTooltipBlockConstructor
from gui.shared.utils.functions import stripColorTagDescrTags
if typing.TYPE_CHECKING:
    from items.artefacts import Equipment, VisualScriptEquipment
_logger = logging.getLogger(__name__)

class RoleSkillBattleTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(RoleSkillBattleTooltipData, self).__init__(context, None)
        self._setContentMargin(top=20, left=20, bottom=10, right=20)
        self._setWidth(320)
        return

    def _packBlocks(self, roleName):
        equipment = self.context.buildItem(roleName)
        if equipment is None:
            _logger.error('Missing Role Skill for role = %s', roleName)
            return []
        else:
            items = [self.__packTooltipBlock(roleName, equipment)]
            return items

    @staticmethod
    def __packTooltipBlock(roleName, equipment):
        blocks = []
        blocks.append(formatters.packTitleDescBlock(title=text_styles.main(getRoleText(roleName)), desc=text_styles.middleTitle(equipment.userString)))
        active, passive = getRoleSkillDescription(equipment)
        if active:
            blocks.append(formatters.packTextBlockData(text=text_styles.standard(stripColorTagDescrTags(active)), padding=formatters.packPadding(bottom=15)))
        if passive:
            blocks.append(formatters.packTextBlockData(text=text_styles.standard(stripColorTagDescrTags(passive)), padding=formatters.packPadding(bottom=15)))
        blocks.append(formatters.packTextBlockData(text=text_styles.standard(getCooldown(equipment))))
        return formatters.packBuildUpBlockData(blocks=blocks)


class RoleSkillLobbyTooltipData(BlocksTooltipData):
    _PARAMS_TEMPLATE = g_htmlTemplates['html_templates:comp7/tooltips/']['roleSkill']

    def __init__(self, context):
        super(RoleSkillLobbyTooltipData, self).__init__(context, None)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setWidth(width=400)
        return

    def _packBlocks(self, equipmentName):
        equipment = self.context.buildItem(equipmentName)
        if equipment is None:
            _logger.error('Missing Role Skill = %s', equipmentName)
            return []
        else:
            items = filter(None, [self.__packHeaderBlock(equipment), self.__packDescriptionBlock(equipment), self.__packInfoBlock()])
            return items

    @classmethod
    def __packHeaderBlock(cls, equipment):
        blocks = [formatters.packTitleDescBlock(title=text_styles.highTitle(equipment.userString), desc=cls.__getCooldown(equipment), gap=-3), formatters.packItemTitleDescBlockData(img=backport.image(cls.__getRoleSkillIcon(equipment)), padding=formatters.packPadding(left=90))]
        return formatters.packBuildUpBlockData(blocks=blocks)

    @classmethod
    def __packDescriptionBlock(cls, equipment):
        blocks = []
        active, passive = getRoleSkillDescription(equipment)
        if passive:
            blocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.roleSkill.description.passive())), desc=text_styles.main(cls.__formatEquipmentParams(passive))))
        if active:
            blocks.append(formatters.packTitleDescBlock(title=text_styles.middleTitle(backport.text(R.strings.tooltips.roleSkill.description.active())), desc=text_styles.main(cls.__formatEquipmentParams(active))))
        return None if not blocks else formatters.packBuildUpBlockData(blocks=blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    @classmethod
    def __formatEquipmentParams(cls, description):
        formatted = description.format(**cls._PARAMS_TEMPLATE.source)
        return formatted

    @staticmethod
    def __packInfoBlock():
        text = text_styles.main(backport.text(R.strings.tooltips.roleSkill.info()))
        return formatters.packTextBlockData(text=text)

    @staticmethod
    def __getCooldown(equipment):
        paramName = ModuleTooltipBlockConstructor.RELOAD_COOLDOWN_SECONDS
        paramValue = params_formatters.formatParameter(paramName, equipment.cooldownSeconds)
        cooldown = params_formatters.formatParamNameColonValueUnits(paramName=paramName, paramValue=paramValue)
        return cooldown

    @staticmethod
    def __getRoleSkillIcon(equipment):
        icon = R.images.gui.maps.icons.roleSkills.c_180x180.dyn(equipment.name)
        if not icon:
            _logger.error('Missing RoleSkill icon: R.images.gui.maps.icons.roleSkills.%s', equipment.name)
            return R.invalid()
        return icon()


def getCooldown(equipment):
    cooldown = R.strings.ingame_gui.consumables_panel.equipment.cooldownSeconds()
    return backport.text(cooldown, cooldownSeconds=equipment.cooldownSeconds)


def getRoleSkillDescription(equipment):
    params = {}
    for k, v in equipment.tooltipParams.iteritems():
        if isinstance(v, tuple):
            for level, levelValue in enumerate(v):
                levelKey = '_'.join((k, str(level + 1)))
                params[levelKey] = levelValue

        params[k] = v

    description = R.strings.artefacts.dyn(equipment.name).dyn('descr')
    active = description.dyn('active')
    active = backport.text(active(), **params) if active.exists() else ''
    passive = description.dyn('passive')
    passive = backport.text(passive(), **params) if passive.exists() else ''
    return (active, passive)


def getPoIEquipmentDescription(equipment):
    description = R.strings.artefacts.dyn(equipment.name).dyn('descr')
    return backport.text(description(), **equipment.tooltipParams)


class BattleResultsPrestigePointsTooltip(BlocksTooltipData):

    def __init__(self, ctx):
        super(BattleResultsPrestigePointsTooltip, self).__init__(ctx, None)
        self._setContentMargin(top=14, left=20, bottom=10, right=20)
        self._setMargins(afterBlock=10)
        self._setWidth(350)
        return

    def _packBlocks(self, *args):
        items = super(BattleResultsPrestigePointsTooltip, self)._packBlocks()
        items.append(self.__packHeaderBlock())
        items.append(self.__packDescriptionBlock())
        return items

    @classmethod
    def __packHeaderBlock(cls):
        blocks = [formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.comp7.battleResult.personal.tooltip.title()))), formatters.packTextBlockData(text_styles.main(backport.text(R.strings.comp7.battleResult.personal.tooltip.descr())))]
        return formatters.packBuildUpBlockData(blocks=blocks)

    @classmethod
    def __packDescriptionBlock(cls):
        blocks = [formatters.packTextBlockData(text_styles.alert(backport.text(R.strings.comp7.battleResult.personal.tooltip.loseTitle())), padding=formatters.packPadding(top=-6, bottom=4)), formatters.packTextBlockData(text_styles.main(backport.text(R.strings.comp7.battleResult.personal.tooltip.loseDescr())))]
        return formatters.packBuildUpBlockData(blocks=blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)


def getRoleEquipmentTooltipParts(equipment):
    active, passive = getRoleSkillDescription(equipment)
    cooldown = getCooldown(equipment)
    body = '\n\n'.join(filter(None, (passive, active, cooldown)))
    return (equipment.userString, stripColorTagDescrTags(body))
