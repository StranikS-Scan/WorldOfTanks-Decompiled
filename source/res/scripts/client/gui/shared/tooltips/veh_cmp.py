# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/veh_cmp.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.customization.tooltips.element import SimplifiedStatsBlockConstructor
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.customization.data_aggregator import VEHICLE_CAMOUFLAGE_BONUS
from gui.customization.elements import CamouflageQualifier, Camouflage
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.Tankman import getSkillSmallIconPath, getRoleWhiteIconPath, Tankman
from gui.shared.items_parameters import params_helper
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.shared import IItemsCache

class VehCmpCustomizationTooltip(BlocksTooltipData):
    """Tooltip data provider for the customization element in vehicle config view.
    """
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, context):
        super(VehCmpCustomizationTooltip, self).__init__(context, TOOLTIP_TYPE.VEH_CMP_CUSTOMIZATION)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(380)
        self._showTTC = False

    def _packBlocks(self, *args):
        self._showTTC = args[0]
        items = [self.__packTitleBlock(), self.__packBonusBlock(), self.__packBottomPanelBlock()]
        return items

    @staticmethod
    def __packTitleBlock():
        return formatters.packImageTextBlockData(title=text_styles.highTitle(VEH_COMPARE.VEHCONF_TOOLTIPS_CAMOTITLE), padding={'top': -5})

    @staticmethod
    def __packBottomPanelBlock():
        return formatters.packImageTextBlockData(title=text_styles.standard(VEH_COMPARE.VEHCONF_TOOLTIPS_CAMOINFO), img=RES_ICONS.MAPS_ICONS_LIBRARY_INFO, imgPadding={'left': 25,
         'top': 3}, txtGap=-4, txtOffset=65, padding={'top': -1,
         'left': 7})

    def __packBonusBlock(self):
        blocks = []
        vehicle = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicle()
        itemID, camo = cmp_helpers.getSuitableCamouflage(vehicle)
        if camo:
            camo['itemID'] = itemID
        cmpItem = self.__getItem(camo, VEHICLE_CAMOUFLAGE_BONUS[vehicle.type])
        bonusTitleLocal = makeHtmlString('html_templates:lobby/textStyle', 'bonusLocalText', {'message': '{0}{1}'.format(cmpItem.qualifier.getFormattedValue(), '')})
        blocks.append(formatters.packImageTextBlockData(title=text_styles.concatStylesWithSpace(bonusTitleLocal), desc=text_styles.main(cmpItem.qualifier.getExtendedName()), img=cmpItem.qualifier.getIcon42x42(), imgPadding={'left': 11,
         'top': 3}, txtGap=-4, txtOffset=65, padding={'top': -1,
         'left': 7}))
        if not self._showTTC and vehicle is not None:
            stockVehicle = self.itemsCache.items.getStockVehicle(vehicle.intCD)
            comparator = params_helper.camouflageComparator(vehicle, cmpItem)
            stockParams = params_helper.getParameters(stockVehicle)
            simplifiedBlocks = SimplifiedStatsBlockConstructor(stockParams, comparator).construct()
            if simplifiedBlocks:
                blocks.extend(simplifiedBlocks)
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    @staticmethod
    def __getItem(camouflage=None, value=0):
        params = {'itemID': 12,
         'nationID': 2,
         'rawElement': {'kind': 1,
                        'description': '#vehicle_customization:camouflage/usa/bicolor/GuamBicolor',
                        'groupName': 'summer',
                        'isNew': False,
                        'deny': frozenset([57121]),
                        'invisibilityFactor': 1.0,
                        'igrType': 0,
                        'colors': (2107107828, 1160008016, 410907375, 496544381),
                        'texture': 'vehicles/american/Camouflage/Cusa_1_1GuamBicolor.dds',
                        'allow': frozenset([])},
         'qualifier': CamouflageQualifier('summer', value),
         'isInDossier': False,
         'isInQuests': False,
         'isInShop': True,
         'allowedVehicles': [],
         'notAllowedVehicles': frozenset([57121]),
         'allowedNations': None,
         'notAllowedNations': None,
         'isReplacedByIGR': False,
         'numberOfItems': None,
         'numberOfDays': None,
         'readableGroupName': '#vehicle_customization:camouflage/summer',
         'price': {}}
        if camouflage is not None:
            params['itemID'] = camouflage['itemID']
            params['rawElement']['kind'] = camouflage['kind']
            params['rawElement']['description'] = camouflage['description']
            params['rawElement']['groupName'] = camouflage['groupName']
            params['rawElement']['isNew'] = camouflage['isNew']
            params['rawElement']['deny'] = camouflage['deny']
            params['rawElement']['invisibilityFactor'] = camouflage['invisibilityFactor']
            params['rawElement']['igrType'] = camouflage['igrType']
            params['rawElement']['colors'] = camouflage['colors']
            params['rawElement']['texture'] = camouflage['texture']
            params['rawElement']['allow'] = camouflage['allow']
        return Camouflage(params)


class VehCmpSkillsTooltip(BlocksTooltipData):
    """Tooltip data provider for the skills block header in vehicle config view.
    """

    def __init__(self, context):
        super(VehCmpSkillsTooltip, self).__init__(context, TOOLTIP_TYPE.VEH_CMP_CUSTOMIZATION)
        self._setContentMargin(top=0, left=30, bottom=25, right=30)
        self._setMargins(afterBlock=20, afterSeparator=20)
        self._setWidth(420)

    def _packBlocks(self, *args):
        items = [self._packTitleBlock(), self.__packDescBlock(), self.__packSkillsBlock()]
        return items

    @staticmethod
    def _packTitleBlock():
        return formatters.packImageTextBlockData(title=text_styles.highTitle(VEH_COMPARE.VEHCONF_TOOLTIPS_SKILLS_HEADER), padding={'top': 20})

    @staticmethod
    def __packDescBlock():
        blocks = [formatters.packImageTextBlockData(title=text_styles.middleTitle(VEH_COMPARE.VEHCONF_TOOLTIPS_SKILLS_DESCHEADER)), formatters.packImageTextBlockData(title=text_styles.main(_ms(VEH_COMPARE.VEHCONF_TOOLTIPS_SKILLS_DESC1, influence=text_styles.alert(VEH_COMPARE.VEHCONF_TOOLTIPS_SKILLS_DESC1_INFLUENCE))), img=RES_ICONS.MAPS_ICONS_LIBRARY_COUNTER_1, imgPadding={'top': 3}, txtOffset=35), formatters.packImageTextBlockData(title=text_styles.main(_ms(VEH_COMPARE.VEHCONF_TOOLTIPS_SKILLS_DESC2, perc=text_styles.alert(VEH_COMPARE.VEHCONF_TOOLTIPS_SKILLS_DESC2_PERC))), img=RES_ICONS.MAPS_ICONS_LIBRARY_COUNTER_2, imgPadding={'top': 3}, txtOffset=35)]
        return formatters.packBuildUpBlockData(blocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, gap=15)

    @staticmethod
    def __packSkillsBlock():

        def __packSkill(crewRole, skills):
            skills = cmp_helpers.sortSkills(skills)
            skillsStr = ' '.join(map(lambda skillType: icons.makeImageTag(getSkillSmallIconPath(skillType), 14, 14, 0, 0), skills))
            return formatters.packCrewSkillsBlockData(text_styles.main(ITEM_TYPES.tankman_roles(crewRole)), skillsStr, getRoleWhiteIconPath(crewRole), padding={'left': -10})

        blocks = [formatters.packImageTextBlockData(title=text_styles.middleTitle(VEH_COMPARE.VEHCONF_TOOLTIPS_SKILLS_SKILLSLIST), padding={'bottom': 10})]
        configurator_view = cmp_helpers.getCmpConfiguratorMainView()
        configured_vehicle = configurator_view.getCurrentVehicle()
        skills_by_roles = cmp_helpers.getVehicleCrewSkills(configured_vehicle)
        skills_by_roles.sort(key=lambda (role, skillsSet): Tankman.TANKMEN_ROLES_ORDER[role])
        blocks.extend(map(lambda data: __packSkill(*data), skills_by_roles))
        return formatters.packBuildUpBlockData(blocks, gap=0, padding={'bottom': -10})
