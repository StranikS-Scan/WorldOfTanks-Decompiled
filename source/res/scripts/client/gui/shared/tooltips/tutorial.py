# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/tutorial.py
from gui.Scaleform.locale.RES_COMMON import RES_COMMON
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES

class HangarTutorialTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(HangarTutorialTooltipData, self).__init__(context, TOOLTIP_TYPE.HANGAR_TUTORIAL)
        self._setContentMargin(top=15, left=19, bottom=21, right=22)
        self._setMargins(afterBlock=14)
        self._setWidth(380)


class HeaderPacker(HangarTutorialTooltipData):

    def __init__(self, context):
        super(HeaderPacker, self).__init__(context)
        self._title = None
        self._descr = None
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(HeaderPacker, self)._packBlocks(*args, **kwargs)
        items.append(formatters.packTitleDescBlock(text_styles.highTitle(self._title), desc=text_styles.main(self._descr) if self._descr else None))
        return items


class CustomizationTypesPacker(HeaderPacker):

    def __init__(self, context):
        super(CustomizationTypesPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_TITLE

    def _packBlocks(self, *args, **kwargs):
        items = super(CustomizationTypesPacker, self)._packBlocks(*args, **kwargs)
        imgPdg = {'left': 3,
         'right': 8,
         'top': -4}
        txtGap = -4
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlockSmallTitle(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_CAMOUFLAGEBLOCKTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_CAMOUFLAGEBLOCKDESCRIPTION)), formatters.packBuildUpBlockData([formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_WINTERCAMOUFLAGETITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_WINTERCAMOUFLAGEDESCRIPTION), RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_WINTER, imgPdg, txtGap=txtGap), formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_SUMMERCAMOUFLAGETITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_SUMMERCAMOUFLAGEDESCRIPTION), RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_SUMMER, imgPdg, txtGap=txtGap), formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_DESERTCAMOUFLAGETITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_DESERTCAMOUFLAGEDESCRIPTION), RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_DESERT, imgPdg, txtGap=txtGap)], gap=5)], gap=13))
        items.append(formatters.packTitleDescBlockSmallTitle(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_EMBLEMBLOCKTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_EMBLEMBLOCKDESCRIPTION)))
        items.append(formatters.packTitleDescBlockSmallTitle(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_LABELSBLOCKTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_CUSTOMIZATION_TYPES_LABELSBLOCKDESCRIPTION)))
        return items


class PersonalCaseSkillsPacker(HeaderPacker):

    def __init__(self, context):
        super(PersonalCaseSkillsPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_SKILLS_TITLE
        self._descr = TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_SKILLS_HEADERDESCRIPTION

    def _packBlocks(self, *args, **kwargs):
        items = super(PersonalCaseSkillsPacker, self)._packBlocks(*args, **kwargs)
        blocksGap = 2
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_SKILLS_SPECIALTYTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_SKILLS_SPECIALTYDESCRIPTION))], blocksGap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        items.append(formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_SKILLS_SPECIALTYWARNING), img=RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON1)], blocksGap))
        return items


class PersonalCasePerksPacker(HeaderPacker):

    def __init__(self, context):
        super(PersonalCasePerksPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_PERKS_TITLE
        self._descr = TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_PERKS_HEADERDESCRIPTION

    def _packBlocks(self, *args, **kwargs):
        items = super(PersonalCasePerksPacker, self)._packBlocks(*args, **kwargs)
        blocksGap = 2
        imgPdg = {'left': 0,
         'right': 10,
         'top': 4}
        txtGap = 0
        items.append(formatters.packBuildUpBlockData([formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_PERKS_NEWPERKTITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_PERKS_NEWPERKDESCRIPTION), RES_COMMON.MAPS_ICONS_TANKMEN_SKILLS_BIG_NEW_SKILL, imgPdg, txtGap=txtGap)], blocksGap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        return items


class PersonalCaseAdditionalPacker(HeaderPacker):

    def __init__(self, context):
        super(PersonalCaseAdditionalPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_TITLE

    def _packBlocks(self, *args, **kwargs):
        items = super(PersonalCaseAdditionalPacker, self)._packBlocks(*args, **kwargs)
        blocksGap = 10
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_RECORDTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_RECORDDESCRIPTION)),
         formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_TRAININGTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_TRAININGDESCRIPTION)),
         formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_PERKSTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_PERKSDESCRIPTION)),
         formatters.packTitleDescBlock(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_DOCUMENTSTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_PERSONALCASE_ADDITIONAL_DOCUMENTSDESCRIPTION))], blocksGap))
        return items


class AmmunitionPacker(HeaderPacker):

    def __init__(self, context):
        super(AmmunitionPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TITLE
        self._descr = TOOLTIPS.HANGARTUTORIAL_AMMUNITION_DESCRIPTION
        self._setWidth(378)

    def _packBlocks(self, *args, **kwargs):
        items = super(AmmunitionPacker, self)._packBlocks(*args, **kwargs)
        imgPdg = {'left': 0,
         'top': 4}
        txtOffset = 56
        txtGap = -5
        blocksGap = 10
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_TITLE)),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_PIERCING_TITLE), desc=text_styles.standard(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_PIERCING_DESCRIPTION), img=RES_ICONS.MAPS_ICONS_AMMOPANEL_AMMO_ARMOR_PIERCING, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_HIGH_EXPLOSIVE_TITLE), desc=text_styles.standard(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_HIGH_EXPLOSIVE_DESCRIPTION), img=RES_ICONS.MAPS_ICONS_AMMOPANEL_AMMO_HIGH_EXPLOSIVE, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_SUBCALIBER_TITLE), desc=text_styles.standard(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_SUBCALIBER_DESCRIPTION), img=RES_ICONS.MAPS_ICONS_AMMOPANEL_AMMO_ARMOR_PIERCING_CR, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_CUMULATIVE_TITLE), desc=text_styles.standard(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_TYPE_CUMULATIVE_DESCRIPTION), img=RES_ICONS.MAPS_ICONS_AMMOPANEL_AMMO_HOLLOW_CHARGE, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset)], blocksGap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        imgPdg = {'left': 0,
         'top': 0}
        txtOffset = 0
        txtGap = 0
        blocksGap = 0
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlockSmallTitle(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_AMMOSET_TITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_AMMUNITION_AMMOSET_DESCRIPTION)), formatters.packImageTextBlockData(img=RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_AMMOSLIDER, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset)], blocksGap))
        return items


class EquipmentPacker(HeaderPacker):

    def __init__(self, context):
        super(EquipmentPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_EQUIPMENT_TITLE
        self._descr = TOOLTIPS.HANGARTUTORIAL_EQUIPMENT_DESCRIPTION
