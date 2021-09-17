# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/skill.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.shared.items_parameters import params
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import getSkillBigIconPath, getRoleMediumIconPath
from gui.shared.items_parameters.comparator import VehiclesComparator
from gui.shared.tooltips import TOOLTIP_TYPE, ToolTipData, ToolTipAttrField, formatters
from gui.shared.items_parameters import params_helper, MAX_RELATIVE_VALUE, formatters as params_formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers.i18n import makeString as _ms
from items import tankmen
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui import makeHtmlString

class SkillTooltipData(ToolTipData):

    def __init__(self, context):
        super(SkillTooltipData, self).__init__(context, TOOLTIP_TYPE.SKILL)
        LOG_DEBUG('SkillTooltipData')
        self.fields = (ToolTipAttrField(self, 'name', 'userName'),
         ToolTipAttrField(self, 'shortDescr', 'shortDescription'),
         ToolTipAttrField(self, 'descr', 'description'),
         ToolTipAttrField(self, 'level'),
         ToolTipAttrField(self, 'type'),
         ToolTipAttrField(self, 'count'))


class BuySkillTooltipData(SkillTooltipData):

    def __init__(self, context):
        super(BuySkillTooltipData, self).__init__(context)
        self.fields = self.fields + (ToolTipAttrField(self, 'header'),)


class SkillTooltipDataBlock(BlocksTooltipData):

    def __init__(self, context):
        super(SkillTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.SKILL)
        self._setWidth(350)

    def _packBlocks(self, *args, **kwargs):
        items = super(SkillTooltipDataBlock, self)._packBlocks()
        item = self.context.buildItem(*args, **kwargs)
        items.append(formatters.packTextBlockData(text=text_styles.highTitle(item.userName)))
        infoBlock = formatters.packTextBlockData(text=makeHtmlString('html_templates:lobby/textStyle', 'mainTextSmall', {'message': item.description}))
        if infoBlock:
            items.append(formatters.packBuildUpBlockData([infoBlock], padding=formatters.packPadding(left=0, right=58, top=-5, bottom=0), linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        items.append(formatters.packTextBlockData(text=text_styles.main(ITEM_TYPES.tankman_skills_type(item.type))))
        return items


class TankmanSkillTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(TankmanSkillTooltipData, self).__init__(context, TOOLTIP_TYPE.TANKMAN)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(445)
        self.__skillType = None
        return

    def _packBlocks(self, *args):
        self.__skillType = args[0]
        self.__showParams = args[1]
        items = [self.__packTitleBlock(), self.__packStatusBlock()]
        if self.__showParams:
            configuratorView = cmp_helpers.getCmpConfiguratorMainView()
            stockvehicle = configuratorView.getCurrentVehicle()
            stockParams = params_helper.getParameters(stockvehicle)
            currentParams = params.VehicleParams(stockvehicle).getParamsDict()
            vehicleWithSkill = configuratorView.getVehicleWithAppliedSkill(self.__skillType)
            if vehicleWithSkill is not None:
                updatedParams = params.VehicleParams(vehicleWithSkill).getParamsDict()
                comparator = VehiclesComparator(updatedParams, currentParams)
                paramBlocks = self.__packParamsBlock(stockParams, comparator)
                if paramBlocks:
                    items.insert(1, formatters.packBuildUpBlockData(paramBlocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        return items

    def __packTitleBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(TOOLTIPS.skillTooltipHeader(self.__skillType)), desc=text_styles.standard(TOOLTIPS.skillTooltipDescr(self.__skillType)), img=getSkillBigIconPath(self.__skillType), imgPadding={'left': 0,
         'top': 3}, txtGap=-4, txtOffset=60, padding={'top': -1,
         'left': 7,
         'bottom': 10})

    def __packStatusBlock(self):
        isPerk = self.__skillType in tankmen.PERKS
        role = self.__getSkillRoleType(self.__skillType)
        specialStatus = ''
        if role == 'radioman':
            specialStatus = TOOLTIPS.SKILLS_STATUS_FOR2RADIOMEN
        if self.__skillType in ('camouflage', 'repair'):
            specialStatus = TOOLTIPS.SKILLS_STATUS_AVGEXP
        blocks = [formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.SKILLS_STATUS_MOMENTAL) if not isPerk else text_styles.alert(TOOLTIPS.SKILLS_STATUS_REQUIERSWHOLECREW), img=RES_ICONS.MAPS_ICONS_LIBRARY_INFO if not isPerk else RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON, imgPadding={'left': 30 if isPerk else 25,
          'top': 3}, txtGap=-4, txtOffset=60, padding={'top': 9,
          'left': 7}), formatters.packImageTextBlockData(title=text_styles.main(_ms(TOOLTIPS.SKILLS_STATUS_ISFORROLE, role=_ms(TOOLTIPS.roleForSkill(role)), special=text_styles.neutral(specialStatus))), img=RES_ICONS.MAPS_ICONS_TANKMEN_CREW_CREWOPERATIONS if role == 'common' else getRoleMediumIconPath(role), imgPadding={'left': 20 if role == 'common' else 22,
          'top': -3 if role == 'common' else -5}, txtGap=-4, txtOffset=60, padding={'top': 30,
          'left': 7})]
        return formatters.packBuildUpBlockData(blocks)

    @staticmethod
    def __packParamsBlock(stockParams, comparator):
        blocks = []
        for parameter in params_formatters.getRelativeDiffParams(comparator):
            delta = parameter.state[1]
            value = parameter.value
            if delta > 0:
                value -= delta
            blocks.append(formatters.packStatusDeltaBlockData(title=text_styles.middleTitle(MENU.tank_params(parameter.name)), valueStr=params_formatters.simplifiedDeltaParameter(parameter), statusBarData={'value': value,
             'delta': delta,
             'minValue': 0,
             'markerValue': stockParams[parameter.name],
             'maxValue': MAX_RELATIVE_VALUE,
             'useAnim': False}, padding=formatters.packPadding(left=67, top=8)))

        return blocks

    @classmethod
    def __getSkillRoleType(cls, skillName):
        if skillName in tankmen.COMMON_SKILLS:
            return 'common'
        else:
            for role, skills in tankmen.SKILLS_BY_ROLES.iteritems():
                if skillName in skills:
                    return role

            return None
