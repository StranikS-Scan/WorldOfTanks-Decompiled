# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/skill.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import getSkillBigIconPath
from gui.shared.tooltips import TOOLTIP_TYPE, ToolTipData, ToolTipAttrField, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from constants import SIXTH_SENSE_BASE_TIME_DELAY
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui import makeHtmlString
from helpers import i18n
SKILLS_DELAYS = {'commander_sixthSense': SIXTH_SENSE_BASE_TIME_DELAY}

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
        items = [self.__packTitleBlock()]
        return items

    def __packTitleBlock(self):
        skillDelay = int(SKILLS_DELAYS.get(self.__skillType, 0))
        description = text_styles.standard(i18n.makeString(TOOLTIPS.skillTooltipDescr(self.__skillType), delay=text_styles.bonusAppliedText(skillDelay)))
        description = description.replace('{colorTagOpen}', '<font color="#80D43A">')
        description = description.replace('{colorTagClose}', '</font>')
        return formatters.packImageTextBlockData(title=text_styles.highTitle(TOOLTIPS.skillTooltipHeader(self.__skillType)), desc=description, img=getSkillBigIconPath(self.__skillType), imgPadding={'left': 0,
         'top': 3}, txtGap=-4, txtOffset=60, padding={'top': -1,
         'left': 7,
         'bottom': 10})
