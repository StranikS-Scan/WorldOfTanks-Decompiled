# Embedded file name: scripts/client/gui/shared/tooltips/tutorial.py
from gui.Scaleform.locale.RES_COMMON import RES_COMMON
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.formatters import text_styles
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui import GUI_NATIONS

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


class ResearchVehicleInfoPacker(HeaderPacker):

    def __init__(self, context):
        super(ResearchVehicleInfoPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_TITLE
        self._descr = TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_HEADERDESCRIPTION

    def _packBlocks(self, *args, **kwargs):
        items = super(ResearchVehicleInfoPacker, self)._packBlocks(*args, **kwargs)
        imgPdg = {'left': 2,
         'top': 3}
        txtOffset = 25
        blocksGap = 7
        txtGap = -4
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlockSmallTitle(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_EXPTITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_EXPDESCRIPTION)), formatters.packBuildUpBlockData([formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_BATTLEEXPTITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_BATTLEEXPDESCRIPTION), RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON, imgPdg, txtOffset=txtOffset, txtGap=txtGap), formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_FREEEXPTITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_FREEEXPDESCRIPTION), RES_ICONS.MAPS_ICONS_LIBRARY_FREEXPICON_2, {'left': 1,
           'top': 3}, txtOffset=txtOffset, txtGap=txtGap), formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_VEHICLEINFO_TOTALEXPTITLE), '', RES_ICONS.MAPS_ICONS_LIBRARY_POWERLEVELICON_1, imgPdg, txtOffset=txtOffset, txtGap=txtGap)], gap=12)], blocksGap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        return items


class ResearchModulesPacker(HeaderPacker):

    def __init__(self, context):
        super(ResearchModulesPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_TITLE
        self._descr = TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_HEADERDESCRIPTION

    def _packBlocks(self, *args, **kwargs):
        items = super(ResearchModulesPacker, self)._packBlocks(*args, **kwargs)
        blocksGap = 5
        imgPdg = {'left': 15,
         'right': 20}
        txtGap = -4
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_TYPESTITLE)),
         formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_GUNTITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_GUNDESCRIPTION), RES_ICONS.MAPS_ICONS_MODULES_GUN, imgPdg, txtGap=txtGap),
         formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_TURRETTITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_TURRETDESCRIPTION), RES_ICONS.MAPS_ICONS_MODULES_TOWER, imgPdg, txtGap=txtGap),
         formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_ENGINETITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_ENGINEDESCRIPTION), RES_ICONS.MAPS_ICONS_MODULES_ENGINE, imgPdg, txtGap=txtGap),
         formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_CHASSISTITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_CHASSISDESCRIPTION), RES_ICONS.MAPS_ICONS_MODULES_CHASSIS, imgPdg, txtGap=txtGap),
         formatters.packImageTextBlockData(text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_RADIOSETTITLE), text_styles.standard(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_RADIOSETDESCRIPTION), RES_ICONS.MAPS_ICONS_MODULES_RADIO, imgPdg, txtGap=txtGap)], blocksGap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        return items


class ResearchModulesPackerEx(ResearchModulesPacker):

    def __init__(self, context):
        super(ResearchModulesPackerEx, self).__init__(context)

    def _packBlocks(self, *args, **kwargs):
        items = super(ResearchModulesPackerEx, self)._packBlocks(*args, **kwargs)
        blocksGap = 3
        imgPdg = {'top': 3}
        txtOffset = 75
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_ACTIONBUTTONSTITLE)),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_RESEARCHBUTTONDESCRIPTION), img=RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_RESEARCHBUTTON, imgPadding=imgPdg, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_BUYBUTTONDESCRIPTION), img=RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_BUYBUTTON, imgPadding=imgPdg, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCH_MODULES_INHANGARDESCRIPTION), img=RES_ICONS.MAPS_ICONS_LIBRARY_COMPLETEDINDICATOR, imgPadding={'top': -3}, txtOffset=txtOffset)], blocksGap))
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


class NationsPacker(HeaderPacker):

    def __init__(self, context):
        super(NationsPacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_NATIONS_TITLE
        self._setWidth(190)
        self._setMargins(afterBlock=12)

    def _packBlocks(self, *args, **kwargs):
        items = super(NationsPacker, self)._packBlocks(*args, **kwargs)
        nationItems = []
        for nation in GUI_NATIONS:
            if nation == 'czech':
                continue
            nationItems.append(formatters.packImageTextBlockData(desc=text_styles.main('#tooltips:hangarTutorial/nations/%s' % nation), img='../maps/icons/filters/nations/%s.png' % nation, imgPadding={'left': 4,
             'top': 4}, txtGap=1, txtOffset=36))

        items.append(formatters.packBuildUpBlockData(nationItems, 2))
        return items


class ResearchTreePacker(HeaderPacker):

    def __init__(self, context):
        super(ResearchTreePacker, self).__init__(context)
        self._title = TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TITLE
        self._descr = TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_DESCRIPTION
        self._setMargins(afterBlock=13)
        self._setWidth(375)

    def _packBlocks(self, *args, **kwargs):
        items = super(ResearchTreePacker, self)._packBlocks(*args, **kwargs)
        imgPdg = {'left': 12,
         'top': 30}
        txtGap = 2
        blocksGap = 12
        items.append(formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TECHBLOCK_COMMONTECH_TITLE), desc=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TECHBLOCK_COMMONTECH_DESCRIPTION), img=RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_COMMONTANK, imgPadding=imgPdg, txtGap=txtGap, imgAtLeft=False), formatters.packImageTextBlockData(title=text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TECHBLOCK_PREMIUMTECH_TITLE), desc=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TECHBLOCK_PREMIUMTECH_DESCRIPTION), img=RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_PREMTANK, imgPadding=imgPdg, txtGap=txtGap, imgAtLeft=False)], blocksGap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        imgPdg = {'left': 12,
         'top': 3}
        txtOffset = 34
        txtGap = 0
        blocksGap = 2
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TYPESBLOCK_TITLE)),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TYPESBLOCK_LIGHTTANK), img=RES_ICONS.MAPS_ICONS_VEHICLETYPES_LIGHTTANK, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TYPESBLOCK_MEDIUMTANK), img=RES_ICONS.MAPS_ICONS_VEHICLETYPES_MEDIUMTANK, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TYPESBLOCK_HEAVYTANK), img=RES_ICONS.MAPS_ICONS_VEHICLETYPES_HEAVYTANK, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TYPESBLOCK_AT_SPG), img=RES_ICONS.MAPS_ICONS_VEHICLETYPES_AT_SPG, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_TYPESBLOCK_SPG), img=RES_ICONS.MAPS_ICONS_VEHICLETYPES_SPG, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset)], blocksGap))
        imgPdg = {'left': 3,
         'top': 2}
        txtOffset = 82
        txtGap = 0
        blocksGap = 8
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_BUTTONSBLOCK_TITLE)),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_BUTTONSBLOCK_RESEARCH), img=RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_RESEARCHBUTTON, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_BUTTONSBLOCK_BUY), img=RES_ICONS.MAPS_ICONS_HANGARTUTORIAL_BUYBUTTON, imgPadding=imgPdg, txtGap=txtGap, txtOffset=txtOffset),
         formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.HANGARTUTORIAL_RESEARCHTREE_BUTTONSBLOCK_INHANGAR), img=RES_ICONS.MAPS_ICONS_LIBRARY_COMPLETEDINDICATOR, imgPadding={'left': 3,
          'top': -3}, txtGap=txtGap, txtOffset=txtOffset)], blocksGap))
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

    def _packBlocks(self, *args, **kwargs):
        items = super(EquipmentPacker, self)._packBlocks(*args, **kwargs)
        blocksGap = 10
        items.append(formatters.packBuildUpBlockData([formatters.packTitleDescBlockSmallTitle(text_styles.middleTitle(TOOLTIPS.HANGARTUTORIAL_EQUIPMENT_PREM_TITLE), text_styles.main(TOOLTIPS.HANGARTUTORIAL_EQUIPMENT_PREM_DESCRIPTION))], blocksGap))
        return items
